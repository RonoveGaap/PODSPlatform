from udado_model import *
from mip.model import *
from mip import OptimizationStatus
import time
import numpy as np

class uDADO:

    def __init__(self, devices: "list[Device]", attributes: "list[Attribute]", num_devices: int = 1, coverage_mode: bool = False) -> None:
        self._timing_rep = {}
        startup = time.perf_counter()
        self._devices = devices
        self._attributes = attributes
        self._num_devices = num_devices
        self._coverage_mode = coverage_mode
        self._normalization = {}
        self._mip_model = Model(name="uDADO")
        creation = time.perf_counter()
        self._timing_rep["Startup"] = creation-startup
        self._x_vars = self._create_variables()
        if coverage_mode:
            self._c_vars = {}
            self._create_coverage()
        var_creation = time.perf_counter()
        self._timing_rep["Variable creation"] = var_creation-creation
        self._create_constraints()
        const_creation = time.perf_counter()
        self._timing_rep["Constraint creation"] = const_creation-creation
        self._build_objective()
        self._ready_time = time.perf_counter()
        self._timing_rep["Objective creation"] = self._ready_time-const_creation
    
    def _create_variables(self) -> "dict[str, mip.Var]":
        return {d.id: self._mip_model.add_var(f"x_{d.id}", var_type=mip.BINARY) for d in self._devices}
    
    def _create_coverage(self) -> None:
        covered = {}
        for device in self._devices:
            covered_by = device.attributes["coverage"]
            for covered_dev in covered_by:
                covered[covered_dev] = covered.get(covered_dev, []) + [device.id]
        for covered_dev in covered:
            covering = covered[covered_dev]
            dev_var = self._mip_model.add_var(f"c_{covered_dev}", var_type=mip.BINARY)
            self._c_vars[covered_dev] = dev_var
            self._mip_model.add_constr(dev_var <= xsum(self._x_vars[covering_dev] for covering_dev in covering))
        self._normalization["coverage"]=(0, len(covered.keys()))

    def _create_constraints(self):
        if not self._coverage_mode:
            self._mip_model.add_constr(xsum(self._x_vars[x] for x in self._x_vars) == self._num_devices, name='num_devices')
        else:
            self._mip_model.add_constr(xsum(self._x_vars[x] for x in self._x_vars) <= self._num_devices, name='num_devices')
        eq_attrs = [a.id for a in self._attributes if a.eq is not None]
        lt_attrs = [a.id for a in self._attributes if a.lt is not None]
        gt_attrs = [a.id for a in self._attributes if a.gt is not None]
        for attr in self._attributes:
            attr_min = None
            attr_max = None
            for device in self._devices:
                if attr.id in device.attributes:
                    attr_val = device.attributes[attr.id]
                    if attr_min is None or attr_val < attr_min:
                        attr_min = attr_val
                    if attr_max is None or attr_val > attr_max:
                        attr_max = attr_val
                if attr.id in eq_attrs:
                    self._mip_model.add_constr(device.attributes.get(attr.id, 0)*self._x_vars[device.id] == attr.eq*self._x_vars[device.id], f'eq_{attr.id}_{device.id}')
                if attr.id in lt_attrs:
                    self._mip_model.add_constr(device.attributes.get(attr.id, 0)*self._x_vars[device.id] <= attr.lt*self._x_vars[device.id], f'lt_{attr.id}_{device.id}')
                if attr.id in gt_attrs:
                    self._mip_model.add_constr(device.attributes.get(attr.id, 0)*self._x_vars[device.id] >= attr.gt*self._x_vars[device.id], f'gt_{attr.id}_{device.id}')
            self._normalization[attr.id] = (attr_min if attr_min is not None else 0, attr_max if attr_max is not None else 1)
        
    def _build_objective(self):
        if self._coverage_mode:
            coverage_term = xsum((1-self._c_vars[c_id])*np.interp(1, self._normalization["coverage"], (0, 100)) for c_id in self._c_vars) + xsum((100/len(self._devices))*self._x_vars[d.id] for d in self._devices)
        else:
            coverage_term = 0
        self._mip_model.objective = coverage_term + xsum(np.interp(d.attributes.get(a.id, 0), self._normalization[a.id], (0, 1))*a.objective*self._x_vars[d.id] for d in self._devices for a in self._attributes)
        self._mip_model.sense = mip.MINIMIZE
    
    def optimize(self) -> "list[str]":
        status = self._mip_model.optimize()
        devices = []
        if status == OptimizationStatus.OPTIMAL:
            for var in self._mip_model.vars:
                if var.x > 0 and var.name.startswith('x_'):
                    devices.append(var.name[2:])
        self._timing_rep["Optimization"] =  time.perf_counter() - self._ready_time
        return devices
    
    def get_timing_report(self) -> "dict[str, float]":
        return self._timing_rep

class ModelParser:

    JSON_ATTRIBUTES_KEY = "attributes"
    JSON_DEVICES_KEY = "devices"
    JSON_DELEGATEES_KEY = "delegatees"
    JSON_COVERAGE_MODE_KEY = "coveragemode"

    @classmethod
    def _parse_dkt(cls, attributes_dkt: "list[dict]", devices_dkt: "list[dict]") -> "tuple[list[Device], list[Attribute]]":
        attributes = [Attribute(a_dkt) for a_dkt in attributes_dkt]
        devices = [Device(d_dkt) for d_dkt in devices_dkt]

        return (devices, attributes)

    @classmethod
    def parse_json(cls, json_file: str) -> "tuple[list[Device], list[Attribute], int, bool]":
        import json

        with open(json_file, 'r') as in_json:
            json_dict = json.load(in_json)
        
        coverage_mode = json_dict.get(cls.JSON_COVERAGE_MODE_KEY, False)

        attributes_json = json_dict[cls.JSON_ATTRIBUTES_KEY]
        devices_json = json_dict[cls.JSON_DEVICES_KEY]
        delegatees = json_dict.get(cls.JSON_DELEGATEES_KEY, 1)

        devices, attributes = cls._parse_dkt(attributes_json, devices_json)
        return (devices, attributes, delegatees, coverage_mode)

class CommandUI:

    ARGUMENTS = {
        "-i": {
            "required": True,
            "metavar": "uDADO config",
            "help": "Input file for uDADO"
        },
        "-o": {
            "required": False,
            "metavar": "output",
            "help": "Output file of the uDADO solution"
        },
        "--print": {
            "required": False,
            "action": "store_true",
            "help": "Print the uDADO solution on screen"
        },
        "--trep": {
            "required": False,
            "metavar": "timing report",
            "help": "Timing report for this execution of uDADO"
        }
    }

    def __init__(self) -> None:
        import argparse
        self.__ap = argparse.ArgumentParser(
            description="MicroDADO", add_help=True)
        for argument in self.ARGUMENTS:
            arg_params = self.ARGUMENTS[argument]
            self.__ap.add_argument(argument, **arg_params)

    def launch(self) -> None:
        ud_args = self.__ap.parse_args()
        json_file = ud_args.i

        devices, attributes, delegatees, coverage_mode = ModelParser.parse_json(json_file)

        udado_model = uDADO(devices, attributes, delegatees, coverage_mode)
        sol = udado_model.optimize()

        if ud_args.print:
            print(sol)
        if ud_args.o:
            import os
            dirname = os.path.dirname(ud_args.o)
            if dirname != '':
                os.makedirs(dirname, exist_ok=True)
            with open(ud_args.o, 'w') as out_file:
                for delegatee in sol:
                    out_file.write(f'{delegatee}\n')
        if ud_args.trep:
            trep = udado_model.get_timing_report()
            import os
            dirname = os.path.dirname(ud_args.trep)
            if dirname != '':
                os.makedirs(dirname, exist_ok=True)
            with open(ud_args.trep, 'w') as out_trep:
                out_trep.write("Step;Time (s)\n")
                for step, time in trep.items():
                    out_trep.write(f'{step};{time}\n')

if __name__ == '__main__':
    CommandUI().launch()