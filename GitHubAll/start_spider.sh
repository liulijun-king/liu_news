#!/bin/bash

# 检查 Docker 容器是否已经启动
if ! docker inspect -f '{{.State.Running}}' dazzling_bohr &>/dev/null; then
    echo "Docker container is not running. Restarting..."
    docker restart dazzling_bohr
else
    echo "Docker container is already running."
fi

# 进入 Docker 容器并执行 main.py 文件
docker exec -it dazzling_bohr  sh /data/start_all.sh
