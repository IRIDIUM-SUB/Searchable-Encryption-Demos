# SWP Solution
## Abstract
解决的问题：在不可信服务器中存储的加密文件中查询关键词，同时不损失机密性。
Song 等人于 2000 年提出了第一个实用的可搜索加密方案 SWP。该方案通过使用特殊的两层加密结构来搜索加密数据，该结构允许使用顺序扫描来搜索密文。核心的想法是分别加密每个单词，然后将一个哈希值（具有特殊格式）嵌入密文中。为了进行搜索，服务器可以提取该哈希值并检查该值是否具有这种特殊格式（表示查询与加密数据的匹配）。
## Details

### Flow Chart

[![szRSUg.png](https://s3.ax1x.com/2021/01/27/szRSUg.png)](https://imgchr.com/i/szRSUg)

### Preparation

- 用户有随机密钥k',k''
- 还需要一个Seed用于产生随机流S。
- f(x,k),F(x,k)分别为两种键控哈希函数。
- 用户有文件C，分为每个定长词w

### 创建密文

对于每个分词W：

1. 使用密钥k''和对称加密算法加密w->X
2. 分成L,R两个部分
3. 使用Seed生成随机流S(这里应该是每个文件生成一个),这里使用的是Si
4. 生成密钥:ki=f(L,k')
5. Y=(Si,F(Si,ki))
6. C=Xi XOR Yi
7. Ci作为该单词的密文发送给服务器

### 搜索:本地部分(创建陷门)

1. 使用密钥k''和对称加密算法加密关键词w->X
2. X=<L,R>
3. k=f(L,k')
4. Send(X,k)

### 搜索:服务器部分(检索)

对于每个文件C的每个词W:

1. (S,P)=W XOR X
2. 检验P,如果:
   1. P=F(S,k),则匹配,返回文件内容(?)C和关键词位置index
   2. 如果不匹配,检查下一个
3. Failed

### 解密

对每一个密文:

1. C=<Cl,Cr>
2. 找到对应的Seed,生成加密时一样的随机流Si
3. Xl=Cl XOR Si
4. K=f(Xl,k')
5. Tp=(Si,F(Si,K))
6. Xp=Cp XOR Tp
7. Wp=Decrypt(Xp),这里是之前的对称算法的解密操作,使用k''作为密钥.

 > HMACMD5 是从 MD5 哈希函数构造的一种键控哈希算法，被用作基于哈希的消息验证代码 (HMAC)。此 HMAC 进程将密钥与消息数据混合.使用哈希函数对混合结果进行哈希计算，将所得哈希值与该密钥混合，然后再次应用哈希函数。输出的哈希值长度为 128 位。




## Design
### Structure
分Client端和Server端，其中Server为不可信，使用Json传递参数

### 传参格式

#### Request

```json
{
    "type":"upload/query/test",
    "filename":"filename",
    "content":"....",//用空格分词
    "query":".....",//(x,k)
    "test":1+2//使用eval()检验
}
```

#### Response

```json
{
    "type":"response",
    "status":200/500,//对于Upload/Query请求的response只回传这一个字段和type
    "filename":"",//用空格分词
    "index":"",//non-0 style
    "content":"",//用空格分词
    "result":3//测试连接用
}
```

### Operation Process
#### 生成密文
1. 生成随机五字母单词列表
1. 如果没有读到key（文件存储），则生成**两个**key，使用`Fernet.generate_key()`,key是b格式串。（Tips：由于生物特征模糊提取器转化的是一个具有高度随机性的串，所以不需要对密码加盐之后键控哈希），并保存
>  A URL-safe base64-encoded 32-byte key
3. 获取到key之后初始化Fernet对象，加密分词`enc=l+r`（转化为b）

4. 生成随机流的方式：[Python实现LFSR+Geffe密钥流生成器 | Yihan's Blog (crushonu.top)](https://crushonu.top/python实现lfsr-geffe密钥流生成器-2/#具体实现代码)

    ```python
    # 以5级LFSR为例，运行时参照提示输入以下值进行初始化：
    请输入LFSR的级数：5
    请输入LFSR1反馈函数常数c的序列Cn~C1，为5位二进制数：01100
    请输入LFSR2反馈函数常数c的序列Cn~C1，为5位二进制数：11100
    请输入LFSR3反馈函数常数c的序列Cn~C1，为5位二进制数：10101
    请输入LFSR1寄存器的初始状态An~A1，为5位二进制数：：01010
    请输入LFSR2寄存器的初始状态An~A1，为5位二进制数：：11001
    请输入LFSR3寄存器的初始状态An~A1，为5位二进制数：：10001
    '''
    NOTE:这里的初始状态考虑使用Seed填充
    '''
    ```

5. 伪随机函数计算密钥k=f(L)（使用HMAC-MD5算法?）（参考http://codingdict.com/sources/py/Crypto.Cipher.ARC4/20482.html和[python md5,SHA1,Hmac加密 - 简书 (jianshu.com)](https://www.jianshu.com/p/2a427645f8f4)）
    ```python
    import hmac
    message = b'10010'
    key = b'${021~[8.@)}'
    h_mac = hmac.new(key, message, digestmod = 'MD5')
    print(h_mac.hexdigest()) #fd34d13d4e31d362f19f1fa9e783fcf0
    ```

6. 使用`key`参与对`k`的键控哈希SHA1:key和message都是bytes类型
    ```python
    import hmac
    message = b'10010'
    key = b'${021~[8.@)}'
    h_mac = hmac.new(key, s,digestmod = 'hashlib.sha1')
    print(res=h_mac.hexdigest()) #fd34d13d4e31d362f19f1fa9e783fcf0
    ```

7. Combine:`p=s+res`

8. XOR:`fin=p xor enc`

9. Upload`fin`
#### Query: Local
1. 输入关键词

2. 使用密钥k''和对称加密算法加密关键词w->X

3. X=<L,R>//Division

4. k=f(L,k')//思考:这里的f(x),F(x)是否写一个函数比较方便?

5. Send(X,k)

#### Query: Remote

对于每个文件C的每个词W:

1. (S,P)=W XOR X
2. 检验P,如果:
   1. P=F(S,k),则匹配,返回文件内容(?)C和关键词位置index
   2. 如果不匹配,检查下一个
3. Failed

#### Decrypt

对每一个密文:

1. C=<Cl,Cr>
2. 找到`filename`对应的`Seed`,生成加密时一样的随机流Si
3. Xl=Cl XOR Si
4. K=f(Xl,k')
5. Tp=(Si,F(Si,K))
6. Xp=Cp XOR Tp
7. Wp=Decrypt(Xp),这里是之前的对称算法的解密操作,使用k''作为密钥.

### 生成key

1. 用户有随机密钥k',k‘’，均使用`Fernet.generate_key()`
2. 还需要一个Seed用于产生随机流S。seed参考格式生成。

## Tech Notes

Technical skills acquired during the development.

### Json的读取和写入

考虑将配置写在`config.json`中,以及网络传参使用json.

Ref: [6.2 读写JSON数据 — python3-cookbook 3.0.0 文档 (python3-cookbook.readthedocs.io)](https://python3-cookbook.readthedocs.io/zh_CN/latest/c06/p02_read-write_json_data.html)

```python
# Writing JSON data
with open('data.json', 'w') as f:
    json.dump(data, f)

# Reading data back
with open('data.json', 'r') as f:
    data = json.load(f)
```





### Network

本Demo设计了一个客户端和一个服务端。

演示时暂定为都在`127.0.0.1`上运行.

#### 创建Socket和连接

```python
# 导入socket库:
import socket

# 创建一个socket:
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#AF_INET指定使用IPv4协议，如果要用更先进的IPv6，就指定为AF_INET6。SOCK_STREAM指定使用面向流的TCP协议
# 建立连接:
s.connect(('www.sina.com.cn', 80))
```
### Server
#### 设计过程

1. Send
2. Response(Response json)

### 编码和解码

项目中大范围使用了`byte`类型和`string`类型.

通用的转换方式:

```python
s1 = str(b, encoding='utf-8')#Byte to Str
b =  bytes(s1, encoding='utf-8')# Str to Byte
```
### 测试连接
使用`send()`方法发送一个模拟json报文。如果正常返回输出结果。？
### pprint
就像这样：
```python
pp = pprint.PrettyPrinter(indent=4,width=41, compact=True)
pp.pprint("SMP Demo")
```
### 快速实现菜单栏
示例代码
```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import time
import sys


class Things():
    def __init__(self, username='nobody'):
        self.username = username

    def clean_disk(self):
        print("cleaning disk ... ...")
        time.sleep(1)
        print("clean disk done!")

    def clean_dir1(self):
        print("cleaning dir1 ... ...")
        time.sleep(1)
        print("clean dir1 done!")

    def clean_dir2(self):
        print("cleaning dir2 ... ...")
        time.sleep(1)
        print("clean dir2 done!")


class Menu():
    def __init__(self):
        self.thing = Things()
        self.choices = {
            "1": self.thing.clean_disk,
            "2": self.thing.clean_dir1,
            "3": self.thing.clean_dir2,
            "4": self.quit
        }

    def display_menu(self):
        print("""
Operation Menu:
1. Clean disk
2. Clean dir1
3. Clean dir2
4. Quit
""")

    def run(self):
        while True:
            self.display_menu()
            try:
                choice = input("Enter an option: ")
            except Exception as e:
                print("Please input a valid option!")continue

            choice = str(choice).strip()
            action = self.choices.get(choice)#在self.choice中查找对应的方法
            if action:
                action()
            else:
                print("{0} is not a valid choice".format(choice))

    def quit(self):
        print("\nThank you for using this script!\n")
        sys.exit(0)


if __name__ == '__main__':
    Menu().run()
```
Via https://blog.csdn.net/u012904337/article/details/79504319
### 生成无重复的随机串
单词空间26^5，选择5000个...应该可以吧(心虚)
```python
import random
import string
file = open('1.txt','w')
for i in range(1000000):    
    random_str = ''.join(random.sample(string.digits *5 +string.ascii_letters*4,255))                 
    file.write(random_str + '\n')
file.close()

```
`string.ascii_lowercase`:小写
`string.ascii_letters`:大写+小写
Via https://blog.csdn.net/heybob/article/details/45341241

### Standard Logging Config 
```python
import logging as log
log.basicConfig(level="DEBUG",format="%(asctime)s-[%(levelname)s]:%(message)s")
```
日志中添加上下文变量
要记录变量的数据，可以使用一个格式串来格式化输出，并将变量作为参数传递给日志记录函数。
```python
logging.info("%d plus %d",num1,num2)
```
## TODO
1. log system
2. Events


