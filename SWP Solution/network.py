'''
Author: I-Hsien
Date: 2021-01-27 21:41:45
LastEditTime: 2021-01-28 20:23:13
LastEditors: I-Hsien
Description: Network Connection for the Demo
FilePath: \Searchable-Encryption-Demos\SWP Solution\network.py
Comments: None
'''

# 导入库:
import socket
import json
import time
CONFIG_FILE="./config.json"
class connection(object):
    '''
    一开始初始化一个connection类，需要连接时调用send方法
    '''
    def __init__(self):
        # Read Config
        with open(CONFIG_FILE,"r")as f:
            self.conf = json.load(f)
    def send(self,data:dict)->Bool:
        '''
        description: Send request json to the server
        param {data:dict}
        return {status:Bool}
        
        '''        
        sendstr=json.dumps(data)# dict to json string
        
        # Create a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 建立连接:
        s.connect((self.conf["RemoteIP"], self.conf["RemotePort"]))
        s.send( bytes(sendstr, encoding='utf-8'))
        
        # 接收数据:
        buffer = []
        StartTime=time.time()
        while time.time()-StartTime<50:# Overtime Check, 50 Secs Maximum
            # 每次最多接收512字节:
            d = s.recv(512)
            if d:
                buffer.append(d)
            else:
                break
        rcvdatabin = b''.join(buffer)
        rcvdata=str(rcvdatabin, encoding='utf-8')
        rcvdict=json.loads(rcvdata)# json string to dict
        # 关闭连接:
        s.close()
        if rcvdict["status"]==200:
            return rcvdict
        elif rcvdict['status']==500 or time.time()-StartTime>50:
            return False
        else:
            return False
        