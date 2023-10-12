#!/usr/bin/env bash

file_name=$2
para=$1 #start/stop
python_path='/bin/python3'
info_dir='info'
all_param=($(ls *.py))
mkdir ${info_dir}
exp_grep='main.sh'

extract_path(){
	file=$1
	path=${file%/*}
	return ${path}
}

extract_file_name(){
	file=$1
	file_name=${file##*/}
	return ${file_name}
}

start(){
	file_name=$1
	is_running=`ps -ef | grep ${file_name} | grep -v grep | grep -v ${exp_grep} | awk '{print $2}' | wc -l`
	if [[ $is_running -gt 0 ]]; then
		return
	fi
	nohup ${python_path} ${file_name} &> ${info_dir}/${file_name}.log &
	echo "${file_name} is started"
}

stop(){
	file_name=$1
	ps -ef | grep ${file_name} | grep -v grep | grep -v ${exp_grep}  | awk '{print $2}' | xargs kill -9
	echo "${file_name} is stopped"
}

status(){
	file_name=$1
	ps -ef | grep ${file_name} | grep -v grep | grep -v ${exp_grep}
}

log(){
	file_name=$1
	file_name=${file_name##*/}
	tail ${info_dir}/${file_name}.log
}

start_all(){
	all_param=$1
	for i in ${all_param[*]}; do
		start ${i}
	done
}

stop_all(){
	all_param=$1
	for i in ${all_param[*]}; do
		stop ${i}
	done
}

if [[ $para == 'start' ]]; then
	start ${file_name}
elif [[ $para == 'stop' ]]; then
	stop ${file_name}
elif [[ $para == 'restart' ]]; then
	stop ${file_name}
	sleep 1
	start ${file_name}
elif [[ $para == 'status' ]]; then
	status ${file_name}
elif [[ $para == 'log' ]]; then
	log ${file_name}
elif [[ $para == 'start_all' ]]; then
	start_all ${all_param}
elif [[ $para == 'stop_all' ]]; then
	stop_all ${all_param}
fi
