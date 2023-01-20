import paho.mqtt.client as mqtt
import os
import json

all_devices = {}
coverage = {}
udado_in_folder = os.getenv('UDADO_IN_FOLDER', '../UDadoInput')

def on_connect(client, userdata, flags, rc):
    print(f'Connected with result code {rc}')

    client.subscribe("PADECPreparation")
    client.subscribe("CoverageUpdates")

def on_message(client, userdata, msg):
    global all_devices
    global coverage
    global udado_in_folder
    print(f'Received message on topic {msg.topic}')
    if msg.topic == 'PADECPreparation':
        payload = msg.payload.decode("utf-8")
        new_sub_topic = f'PADEC{payload}'
        client.subscribe(new_sub_topic)
        print(f'Subscribed to topic {new_sub_topic}')
    elif msg.topic == 'CoverageUpdates':
        coverage = json.loads(msg.payload.decode("utf-8"))
        print('Updated coverage')
    else:
        with open(f'Response{msg.topic}.txt', 'w') as out:
            out.write(msg.payload.decode("utf-8"))
        print(f'Message written to file Response{msg.topic}.txt')
        with open(f'Response{msg.topic}.txt', 'r') as in_file:
            flines = in_file.readlines()
        dev_info = parse_file(flines)
        all_devices[dev_info['id']] = dev_info
        j_out = generate_udado()
        with open(os.path.join(udado_in_folder, 'input.json'), 'w') as dadojson:
            json.dump(j_out, dadojson)
        print('Updated DADOJSON file')

def generate_udado() -> dict:
    global all_devices
    global coverage
    base_conf = {"coveragemode": True, "attributes": [
        {"id": "battery", "objective": -1},
        {"id": "cpu", "objective": -1},
        {"id": "ram", "objective": -1}
    ],
    "delegatees": 5}
    devices = []
    for dev_name in all_devices:
        device_conf = all_devices[dev_name]
        device_conf["attributes"]["coverage"] = coverage.get(dev_name, list(all_devices.keys()))
        devices.append(device_conf)
    base_conf["devices"] = devices
    return base_conf
    
def parse_file(flines: "list[str]") -> "dict[str, list[str]]":
    trigger_words = {"Device Name:": "name", "Model Info:": "model", "Power Info:": "power", "Storage Info:": "storage", "RAM Info:": "ram", "CPU Info:": "cpu"}
    lines = {"name": 1, "model": 1, "power": 4, "storage": 1, "ram": 2, "cpu": 108}
    counters = {k: 0 for k in lines}
    sorted_lines = {k: [] for k in lines}
    for line in flines:
     for word in trigger_words:
             if line.startswith(word):
                     counters[trigger_words[word]] = 1
     for cnt_keyword in counters:
             if counters[cnt_keyword] > 0:
                     sorted_lines[cnt_keyword].append(line)
                     counters[cnt_keyword] = counters[cnt_keyword]+1
                     if counters[cnt_keyword] > lines[cnt_keyword]+1:
                             counters[cnt_keyword] = -1
    info = {"id": sorted_lines["name"][1][:-1], "attributes": {
        "ram": float(sorted_lines["ram"][1][15:-1]), 
        "battery": 200 if sorted_lines["power"][1][:-1] == 'false' else float(sorted_lines["power"][3][18:-2]),
        "cpu": float(sorted_lines["cpu"][9][11:-1]) * int(sorted_lines["cpu"][14][12:-1])}}
    return info

if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    mqtt_server = os.getenv('MQTT_SERVER', '10.0.2.2')
    mqtt_port = int(os.getenv('MQTT_PORT', 1883))
    mqtt_timeout = int(os.getenv('MQTT_TIMEOUT', 280))

    print(f"Attepmting connection at {mqtt_server}:{mqtt_port}")

    client.connect(mqtt_server, mqtt_port, mqtt_timeout)

    client.loop_forever()