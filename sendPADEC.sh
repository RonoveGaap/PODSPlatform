#!/usr/bin/env bash

credential="/home/evaluator/credentials.json"
jsonpath="/home/evaluator/udado_sharepoint"
outpath="/home/evaluator/udado_out"
filename="/home/evaluator/docker-img-tmp"
imagefile="padec/performanceapp"
container="eval-app"
self="EVA-03"


docker run -v $jsonpath:/indata -v $outpath:/outdata padec/microdado

input="$outpath/solution.txt"
mosquitto_pub -f $input -h 10.0.2.2 -t NeighborsReport

if [ -e ./.apprunning ]; then
    echo "This device runs the service"
    stop=0
    must_stop=1
    while read -r neighbor
    do
        if [ $neighbor == $self ]; then
            echo "This device is also a delegatee"
            must_stop=0
        fi
    done < "$input"
    while read -r neighbor
    do
        if [ $neighbor != $self ]; then
            password=$(jq --arg NEI "$neighbor" '."\($NEI)".password' "$credential")
            tmp=${password%\"}
            password=${tmp#\"}
            dest=$(jq --arg NEI "$neighbor" '."\($NEI)".dest' "$credential")
            tmp=${dest%\"}
            dest=${tmp#\"}
            port=$(jq --arg NEI "$neighbor" '."\($NEI)".port' "$credential")
            finalcommand=$(echo "docker run -d -e RAM_RESOURCES=1024 --name $container $imagefile")
            echo "Delegating service"
            time -o "MigrationTime-$(date '+%Y-%m-%d-%H-%M').txt" sshpass -p $password ssh -p $port $dest $finalcommand
            if [ $stop = 0 ]; then
                stop=1
                echo "Stopping container"
                if [ $must_stop == 1 ]; then
                    rm .apprunning
                    time -o "StopTime-$(date '+%Y-%m-%d-%H-%M').txt" docker rm -f $container
                fi
            fi
        fi
    done < "$input"
fi
