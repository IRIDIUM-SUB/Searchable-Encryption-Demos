'''
Author: I-Hsien
Date: 2021-01-27 21:41:45
LastEditTime: 2021-05-03 17:08:12
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
import pickle
CONFIG_FILE = "config.json"


class connection(object):
    '''
    一开始初始化一个connection类，需要连接时调用send方法
    '''

    def __init__(self):
        # Read Config
        with open(CONFIG_FILE, "r")as f:
            self.conf = json.load(f)
            f.close()

    def send(self, data:dict) -> bool:
        '''
        description: Send request json to the server
        param {data}
        return {status:Bool}
        '''
        log.log.info("Starting sending data")

        sendstr = pickle.dumps(data)  # dict to json string

        # Create a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 建立连接:
        s.connect((self.conf["RemoteIP"], self.conf["RemotePort"]))
        log.log.info("connection estbalished")
        s.send(sendstr)
        log.log.info("data sent")
        # 接收数据:
        rcvdata = s.recv(4096)#4096 Bytes per most
        log.log.debug("received data:%s", rcvdata)
        rcvdict = pickle.loads(rcvdata)  # json string to dict
        
        # 关闭连接:
        s.close()
        log.log.debug("Stop Connection")
        if rcvdict["status"] == 200:
            return rcvdict
        else:
            log.log.error("Connection failed due to connection failed")
            return False
