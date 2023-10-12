FROM hanxinkong/network_scanning:centos7_nmap_dig_python3
WORKDIR ./network_scanning
ADD . .
ENV PYTHONPATH=/network_scanning
RUN pip3 install -r requirements.txt
RUN chmod a+x ./start.sh
CMD ["./start.sh"]