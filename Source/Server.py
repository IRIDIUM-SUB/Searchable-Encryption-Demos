'''
Author: I-Hsien
Date: 2021-01-27 21:55:57
LastEditTime: 2021-05-09 12:23:12
LastEditors: I-Hsien
Description: Another Isolated Program, act as server.
FilePath: \Searchable-Encryption-Demos\SWP Solution\Server.py
Comments: Also use Connection class and config.json
'''
import socket
import json
import time
import hashlib
import Log as log
import threading
import pickle
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair

CONFIG_FILE = "config.json"
FILE_AMOUNT=10

def tcplink(sock, addr) -> None:
    '''
    description: 处理每一个连接
    param {*}
    return {*}
    '''
    log.log.info('Accept new connection from %s:%s...',
                 str(addr[0]), str(addr[1]))
    rcvdatabin = b""

    while True:#Main loop,事务处理应该在这里面。
        log.log.debug("TCP Loop...")
        rcvdatabin = sock.recv(4096)

        time.sleep(1)
        if not rcvdatabin:
            log.log.warning("Connection Loop broken")
            break  # Stop receiving
        rcvdata = pickle.loads(rcvdatabin)#rcvdata is a plain dict
        log.log.debug("received data:%s", str(rcvdata))

        ServerTransactionInterface(sock, rcvdata)  # 传入事务处理接口
    
    sock.close()#Close Connection
    log.log.warning('Connection from %s closed.', addr)
    return


def ServerTransactionInterface(sock, data: dict) -> None:
    '''
    description: 服务器端的事务分发接口
    param {Sock,data:dict}
    return {*}
    data:
    {
        "type":"upload/query/test",
        "filename":"filename",
        "content":"....",//用空格分词
        "query":".....",//(x,k)
        "test":1+2//使用eval()检验
    }
    '''
    log.log.debug("Received request type:%s", data["type"])

    choices = {
        "upload": Upload,
        "query": Query,
        "test": TestConnection
    }
    try:
        choice = data["type"]
    except Exception as e:
        log.log.error("Wrong input:%s", choice)
        return

    choice = str(choice).strip()
    action = choices.get(choice)  # choice中查找对应的方法
    if action:
        log.log.info("Got Command %s", action)
        action(sock, data)
    else:
        log.log.error("%s is not a valid choice",choice)
        return


def SendErrorMsg(sock, msg) -> None:
    '''
    发送出现错误的报文
    有必要吗？
    '''
    pass


def TestConnection(sock, data) -> int:
    '''
    description: Connection test, return num1+num2
    param {sock,data:dict}
    return {int}
    response:
    {
        "type":"response",
        "status":200/500,//对于Upload/Query请求的response只回传这一个字段和type
        "filename":"",//用空格分词
        "index":"",//non-0 style
        "content":"",//用空格分词
        "result":3//测试连接用
    }
    '''
    result = eval(data["test"])
    log.log.info("Resolve successfully,result is %d", result)

    ResopnseMsg = dict()
    ResopnseMsg["type"] = "resopnse"
    ResopnseMsg["status"] = 200
    ResopnseMsg["result"] = result

    # Encode and send
    sock.send(pickle.dumps(ResopnseMsg))
    log.log.info("Response mseg sent,type:%s", data['type'])
    return

def Upload(sock,data):
    log.log.info("Start receiving enc")
    enctext=data['content'] #is a non-PICKLED list
    log.log.debug("enctext is %s",enctext)
    filename="ServerEnc"+data['filename']+".bin"
    
    with open (filename,"wb")as f:
        pickle.dump(enctext,f)
        
        f.close()
    
    log.log.info("File %s saved",filename)
    ResponseMsg=dict()
    ResponseMsg["status"]=200
    sock.send(pickle.dumps(ResponseMsg))
    log.log.info("Response msg sent,type:%s", data['type'])
    return
        
def Query(sock,data):
    log.log.info("Start query")
    for i in range(FILE_AMOUNT):# for each file
        filename="ServerEnc"+str(i+1)+".bin"
        log.log.info("Searching %s",filename)
        with open(filename,"rb") as f:
            enclist=pickle.load(f)#a list of enctext
            f.close()
        for word in enclist:
            log.log.info("Checking %s",str(word))
            if Test(data['query'],word): #match
                log.log.info("word hit,in %s",filename)
                #Ready to send msg
                data=dict()
                data['type']='response'
                data['status']=200
                data['result']=200
                data['filename']=filename
                sock.send(pickle.dumps(data))
                return
    # Failed
    log.log.warning("No word found")
    data=dict()
    data['type']='response'
    data['status']=200
    data['result']=404
    data['filename']=None
    sock.send(pickle.dumps(data))
    return
def Test(td, c, param_id='SS512'):
    group = PairingGroup(param_id)
    Hash2 = hashlib.sha256
    c1 = group.deserialize(c[0])
    c2 = c[1]
    #print(c2)
    td = group.deserialize(td)
    return Hash2(group.serialize(pair(td, c1))).hexdigest() == c2
if __name__ == "__main__":
    with open(CONFIG_FILE, "r")as f:
        NetConf = json.load(f)
        f.close()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((NetConf["RemoteIP"], NetConf["RemotePort"]))  # Bind port
    log.log.debug("Bind port,%s:%d",
                  NetConf["RemoteIP"], NetConf["RemotePort"])
    s.listen(5)  # Maxium Connections
    log.log.info('Waiting for connection...')
    while True:
        # 接受一个新连接:
        sock, addr = s.accept()
        # 创建新线程来处理TCP连接:
        t = threading.Thread(target=tcplink, args=(sock, addr))
        t.start()
