echo -n '{"type": "RAM", "value": "' > ./testRAM.json
echo -n $RAM_RESOURCES >> ./testRAM.json
echo -n '"}' >> ./testRAM.json
echo -n '{"type": "Operation", "value": "' > ./testOper.json
echo -n $COMP_TIMES >> ./testOper.json
echo -n '", "opeType": "' >> ./testOper.json
echo -n $COMP_TIMES >> ./testOper.json
echo -n '"}' >> ./testOper.json
echo -n '{"type": "IO", "value": "' > ./testIO.json
echo -n $IO_TIMES >> ./testIO.json
echo -n '", "IOType": "' >> ./testIO.json
echo -n $IO_TYPE >> ./testIO.json
echo -n '"}' >> ./testIO.json
cat ./testRAM.json
cat ./testOper.json
cat ./testIO.json
./myapp