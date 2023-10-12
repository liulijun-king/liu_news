import json
import traceback
from kafka3 import KafkaProducer
from kafka3.errors import KafkaError
from loguru import logger
from network_information_source.common import CJsonEncoder


class KafkaUtils:
    def __init__(self):
        pass

    # def push_new_server(self, _data, topic):
    #     """
    #     批量数据推送
    #     :param _data: 数据json
    #     :param topic: 索引名
    #     :return:
    #     """
    #     try:
    #         data = {
    #             "msg": json.dumps(_data, ensure_ascii=False),
    #             "topic": topic,
    #             "ip": "222.244.146.53"
    #         }
    #         # url = 'http://220.194.140.39:30015/kafka/allMediaBatchTokafka'
    #         # url = 'http://10.99.10.27:8081/kafka/allMediaBatchTokafka'
    #         url = 'http://140.210.203.161:9092/kafka/allMediaBatchTokafka'
    #         res = requests.post(url, data=data, timeout=10)
    #         if res:
    #             res_json = res.json()
    #             if res_json.get('status', '') == 1:
    #                 logger.success(f"【推送new】 成功 {len(_data)}条,返回结果：{res_json['msg']}")
    #             else:
    #                 logger.error(f"【推送new】 失败 返回结果：{res_json['msg']}")
    #     except Exception as e:
    #         logger.error(f"【推送new】 错误：{e}")
    @staticmethod
    def push_new_server(video_datas: list, topic: str, ):
        """
        直连kafka推送数据
        :param topic: 推送索引
        :param video_datas: 推送的数据列表  json类型
        :return:
        """
        while True:
            try:
                producer = KafkaProducer(
                    bootstrap_servers=['8.130.131.161:9092', '8.130.94.243:9092', '8.130.37.191:9092'])
            except(Exception,):
                traceback.print_exc()
                logger.error('连接kafka出现问题，等待kafka重新连接')
                # time.sleep(2)
            else:
                for video_data in video_datas:
                    d_count = 0
                    while d_count < 3:
                        try:
                            send_data = json.dumps(video_data, cls=CJsonEncoder)
                            future = producer.send(topic, send_data.encode())
                            record_metadata = future.get(timeout=20)
                            if record_metadata:
                                logger.success(f"推送kafka 任务id:【{video_data.get('task_id')}】 topic: 【{topic}】")
                                break
                            # logger.debug(record_metadata)
                            # logger.info(f'插入kafka成功')
                        except KafkaError as e:
                            d_count = d_count + 1
                            logger.error(str(e))
                break

        # while True:
        #     try:
        #         send_data = json.dumps(video_data)
        #         future = producer.send(topic, str(send_data).encode())
        #         record_metadata = future.get(timeout=20)
        #         if record_metadata:
        #             break
        #         # logger.debug(record_metadata)
        #         # logger.info(f'插入kafka成功')
        #     except KafkaError as e:
        #         logger.error(str(e))


kafka_utils = KafkaUtils()
