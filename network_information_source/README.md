# network_scanning

网络资源发现与验证


unzip network_information_source.zip -d network_information_source
cd network_information_source
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt

/u01/isi/CenterProject/network_information_source/venv/bin/python3 /u01/isi/CenterProject/network_information_source/run/deploy_verify.py 
/u01/isi/DataArchitecture/CenterProject/network_information_source/venv/bin/python3 /u01/isi/DataArchitecture/CenterProject/network_information_source/run/deploy_verify.py 


境内
bash main_domestic.sh start task_find_both.py
bash main_domestic.sh start task_find_domestic.py
bash main_domestic.sh start task_find_outbound.py

bash main_domestic.sh start task_verify_both.py
bash main_domestic.sh start task_verify_domestic.py
bash main_domestic.sh start task_verify_outbound.py

bash main_domestic.sh start deploy_verify.py
bash main_domestic.sh start deploy_find.py

境外
bash main_outbound.sh start deploy_verify.py
bash main_outbound.sh start deploy_find.py
