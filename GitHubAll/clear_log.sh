#!/bin/bash
#log_path=/u01/isi/CenterProject/GitHubAll/
##log_path=/home
#cd $log_path
#find $log_path -name "*.log" > .del.dat
#find $log_path -name "*.log.*" >> .del.dat
#find $log_path -name "nohup.out" >> .del.dat
#find $log_path -name "catalina.out" >> .del.dat
#for i in `cat .del.dat`
#do
#  cat /dev/null  > $i
#done

find /data -type f -name "*.log" -exec rm {} \;
find /data -type f -name "*.out" -exec rm {} \;