mon_file="/home/evaluator/udado_sharepoint/input.json"
last_date=0

while :
do
    sleep 60
    if [ -e $mon_file ]; then
        new_date=$(date -r $mon_file "+%s")
        if [ $new_date -gt $last_date ]; then
            last_date=$new_date
            sh ./sendPADEC.sh
        fi
    fi
done
