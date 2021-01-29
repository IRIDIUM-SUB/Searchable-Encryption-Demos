'''
Author: I-Hsien
Date: 2021-01-27 21:41:45
LastEditTime: 2021-01-29 21:12:01
LastEditors: I-Hsien
Description: Network Connection for the Demo
FilePath: \Searchable-Encryption-Demos\SWP Solution\network.py
Comments: None
'''

# 导入库:
import socket
import json
import time
import Log as log
CONFIG_FILE = "./config.json"


class connection(object):
    '''
    一开始初始化一个connection类，需要连接时调用send方法
    '''

    def __init__(self):
        # Read Config
        with open(CONFIG_FILE, "r")as f:
            self.conf = json.load(f)

    def send(self, data: dict) -> Bool:
        '''
        description: Send request json to the server
        param {data:dict}
        return {status:Bool}

        '''
        log.log.info("Starting sending data")

        sendstr = json.dumps(data)  # dict to json string

        # Create a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 建立连接:
        s.connect((self.conf["RemoteIP"], self.conf["RemotePort"]))

        log.log.info("connection estbalished")

        s.send(bytes(sendstr, encoding='utf-8'))
        log.log.info("data sent")
        # 接收数据:
        buffer = []
        StartTime = time.time()

        log.log.debug("Starting waiting %s", StartTime)

        while time.time()-StartTime < 50:  # Overtime Check, 50 Secs Maximum
            # 每次最多接收512字节:
            d = s.recv(512)
            if d:
                buffer.append(d)
                log.log.debug("received data:%s", d)
            else:
                log.log.debug("No more data")
                break
        rcvdatabin = b''.join(buffer)
        rcvdata = str(rcvdatabin, encoding='utf-8')# Decode
        rcvdict = json.loads(rcvdata)  # json string to dict
        # 关闭连接:
        s.close()
        log.log.debug("Stop Connection")
        if rcvdict["status"] == 200:
            return rcvdict
        elif time.time()-StartTime > 50:
            log.log.error("Connection failed due to timeout")
            return False
        else:
            log.log.error("Connection failed due to connection failed")
            return False
