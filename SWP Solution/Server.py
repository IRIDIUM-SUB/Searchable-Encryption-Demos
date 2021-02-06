'''
Author: I-Hsien
Date: 2021-01-27 21:55:57
LastEditTime: 2021-02-03 10:59:20
LastEditors: I-Hsien
Description: Another Isolated Program, act as server.
FilePath: \Searchable-Encryption-Demos\SWP Solution\Server.py
Comments: Also use Connection class and config.json
'''
import socket
import json
import time
import Log as log
import threading
CONFIG_FILE = "config.json"


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
        rcvdatabin = sock.recv(1024)

        time.sleep(1)
        log.log.debug("Data Segment:%s", rcvdatabin.decode('utf-8'))
        if not rcvdatabin:
            log.log.warning("Connection Loop broken")
            break  # Stop receiving
        rcvdata = rcvdatabin.decode('utf-8')
        log.log.debug("received data:%s", rcvdata)

        ServerTransactionInterface(sock, json.loads(rcvdata))  # 传入事务处理接口
    
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
        "upload": "",
        "query": "",
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
        log.log.error("{0} is not a valid choice",format(choice))
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
    ResopnseJson = json.dumps(ResopnseMsg)
    sock.send(ResopnseJson.encode(encoding="utf-8"))
    log.log.info("Response mseg sent,type:%s", data['type'])
    return


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
