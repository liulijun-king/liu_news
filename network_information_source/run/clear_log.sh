#!/bin/bash
log_path=/u01/isi/CenterProject/network_information_source/run/
cd $log_path

type_file=("*.log" "*.log.*" "*.out" "nohup.out" "catalina.out")
for i in ${type_file}
do 
  find $log_path -name ${i} >> .del.dat
done

for i in `cat .del.dat`
do
  cat /dev/null  > $i
done
