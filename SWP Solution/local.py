'''
Author: I-Hsien
Date: 2021-01-28 20:02:50
LastEditTime: 2021-05-18 11:48:07
LastEditors: I-Hsien
Description: Client Program
FilePath: \Searchable-Encryption-Demos\SWP Solution\local.py
Comments: None
'''
import network
import pprint
import os
import sys
import string
import Log as log
import pickle
from cryptography.fernet import Fernet
from fuzzy_extractor import FuzzyExtractor
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
import hashlib
import random
Hash1pre = hashlib.md5


class Menu(object):
    '''
    处理菜单事务，并且这里调用事务类。
    '''

    def __init__(self):
        self.pp = pprint.PrettyPrinter(indent=4, width=41, compact=True)
        self.client = ClientTransactionInterface()

        self.choices = {
            "1": self.client.connection_test,
            "4": self.client.gen_wordlist,
            "2": self.client.gen_key,
            "5": self.client.encrypt,
            "6": self.client.query,
            "3": self.client.load_key,
            "0": self.quit
        }

    def display_menu(self) -> None:
        self.pp.pprint("SMP Demo")
        self.pp.pprint("1. Connection Test")
        self.pp.pprint("2. Generate Key")
        self.pp.pprint("3. Recover Key")
        self.pp.pprint("4. Generate Wordlist")
        self.pp.pprint("5. Encrypt and Upload")
        self.pp.pprint("6. Query")
        self.pp.pprint("0. Exit")
        self.pp.pprint("-----------------------")
        log.log.debug("Menu displayed")
        return

    def run(self):
        while True:  # Main Loop
            os.system("clear")
            self.display_menu()
            try:
                choice = input("Enter an option: ")
            except Exception as e:
                log.log.error("Wrong input:%s", choice)
                print("Please input a valid option!")
                continue
            choice = str(choice).strip()
            action = self.choices.get(choice)  # 在self.choice中查找对应的方法
            if action:
                log.log.info("Got Command %s", action)
                action()
            else:
                log.log.error("Invaild Choice")
                print("{0} is not a valid choice".format(choice))
            os.system("read -p Press any key to continue")

    def quit(self):
        print("\nThank you for using this script!\n")
        log.log.info("Exit")
        sys.exit()  # Exit Now


class ClientTransactionInterface(object):
    '''
    事务处理接口
    '''

    def __init__(self):
        self.connection = network.connection()  # initialize connection class
        self.extractor = FuzzyExtractor(16, 10)
        self.param_id = 'SS512'
        self.group = PairingGroup(self.param_id)
        self.sk = None
        self.pk = None

    def connection_test(self):
        '''
        Test Connection by sending test json
        {
            "type":"test",

            "test":1+2//使用eval()检验
        }
        '''
        log.log.info("Starting connection test")
        data = dict()  # Preparing data
        data["type"] = "test"
        num1 = random.randint(0, 1000)
        num2 = random.randint(0, 1000)
        data["test"] = str(num1)+"+"+str(num2)
        log.log.info("Ready to send %d and %d", num1, num2)

        rcvdict = self.connection.send(data)

        if rcvdict['result'] == num1+num2:
            print("Ping Success")
            log.log.info("Ping Success,%d plus %d = %d",
                         num1, num2, rcvdict['result'])
        else:
            print("Ping Failed")
            log.log.warning("Ping Failed")

    def gen_wordlist(self, FILES_AMOUNT=10, WORDS_PER_FILE=5, WORD_LEN=5) -> None:
        '''
        生成若干个文件，每个文件包含若干个单词，单词不重复且随机，配置见默认参数
        文件名为1,2,3,4,5,...
        '''
        log.log.info("Starting Generating wordlist")

        for i in range(FILES_AMOUNT):
            Filename = str(i+1)+".txt"
            with open(Filename, "w")as f:
                WordList = []
                for _ in range(WORDS_PER_FILE):
                    RandomStr = ''.join(random.sample(
                        string.ascii_lowercase, WORD_LEN))
                    WordList.append(RandomStr)
                # Write in Wordlist
                # File should be like mmmmm,nnnnn,...
                f.write(",".join(WordList))
                f.close()
                log.log.info("File %d written", i+1)
        return

    def gen_key(self):
        log.log.info("Start generating list")
        # Fuzzy Here
        fingerprint = input("Put in Fuzzy Fingerprints")
        if len(fingerprint) != 16:
            log.log.error("Wrong fingerprint format")
            return
        key, helper = self.extractor.generate(fingerprint)
        log.log.info("Fuzzy key generated")
        # Save helper
        with open("helper.bin", "wb")as f:
            pickle.dump(helper, f)
            f.close()
        # Generate true key
        random.seed(key)
        i = random.randint(-300000, 300000)
        log.log.debug("Random seed generated:%d", i)
        self.g = self.group.random(G1, seed=i)
        self.alpha = self.group.random(ZR, seed=i)
        log.log.debug("G and Alpha generated:%s and %s",
                      str(self.g), str(self.alpha))
        self.sk = self.group.serialize(self.alpha)
        self.pk = [self.group.serialize(
            self.g), self.group.serialize(self.g ** self.alpha)]
        log.log.info("sk and pk generated!")

    def load_key(self, HELPER_PATH="helper.bin") -> None:
        '''
        description: Load helper and try to recover and recover true key
        '''
        try:
            f = open(HELPER_PATH, "rb")
            helper = pickle.load(f)
        except IOError:
            log.log.error("No Such File:HELPER")
            return None
        else:
            log.log.info("Read HELPER successed")
            f.close()
        fingerprint = input("Put in Fuzzy Fingerprints")
        r_key = self.extractor.reproduce(fingerprint, helper)
        if not r_key:
            log.log.error("Key Recovery Failed")
            return
        else:
            log.log.debug("Key Recovered:%s", str(r_key))
            # Gen true key
            random.seed(r_key)
            i = random.randint(-300000, 300000)
            log.log.debug("Random seed generated:%d", i)
            g = self.group.random(G1, seed=i)
            alpha = self.group.random(ZR, seed=i)
            log.log.debug("G and Alpha RECOVERED:%s and %s",
                          str(g), str(alpha))
            self.sk = self.group.serialize(alpha)
            self.pk = [self.group.serialize(
                g), self.group.serialize(g ** alpha)]
            log.log.info("sk and pk recovered!")
            return

    def Enc(self, w, param_id='SS512'):
        '''
        work method
        之前已经检验过了pk 和 sk
        '''
        #group = PairingGroup(param_id)
        # 进行反序列化
        g, h = self.group.deserialize(
            self.pk[0]), self.group.deserialize(self.pk[1])
        r = self.group.random(ZR)
        t = pair(self.Hash1(w), h ** r)
        c1 = g ** r
        c2 = t
        # 对密文进行序列化

        return [self.group.serialize(c1), Hash2(self.group.serialize(c2)).hexdigest()]

    def encrypt(self, FILE_AMOUNT=10, param_id='SS512'):
        if not self.sk or not self.pk:
            log.log.error("No vaild key!")
            return
        for i in range(FILE_AMOUNT):
            FILE_PATH = str(i+1)+".txt"
            ENC_PATH = "Enc"+str(i+1)+".bin"
            with open(FILE_PATH, "r") as f:
                wordlist = f.read().split(",")
                enclist = []
                log.log.debug("Plain list is %s", wordlist)
                # newflag=True# 这个单词是否是文件的第一个

                for word in wordlist:
                    enctext = self.Enc(word)  # is a list
                    log.log.info("Encrypt:%s->%s", word, str(enctext))
                    enclist.append(enctext)

                # Upload here
                data = dict()
                data['type'] = "upload"
                data['content'] = enclist  # NO PACKED!
                data['filename'] = str(i+1)
                # data['flag']=newflag
                log.log.debug("data is %s", data)
                rcvdict = self.connection.send(data)
                if rcvdict['status'] == 200:  # Success
                    log.log.info("data upload success")
                else:
                    log.log.error("Upload Failed")
                    f.close()
                    # newflag=False#Set as false
            log.log.info("Enc %d Ends", i+1)
            # Send encrypt
            #datas = pickle.dumps(enclist)

    def query(self):

        log.log.info("Make Sure the Key has been Recovered")
        if not(self.pk and self.sk):
            log.log.error("key not recovered yet")
            return
        # Generate trapdoor
        w = input("Input word wanna search")
        if len(w)!=5:
            log.log.warning("Wrong word format")
            return
        sk = self.group.deserialize(self.sk)  # deserialize
        log.log.debug("Deserialized sk is %s", sk)
        td = self.Hash1(w)**sk
        content = self.group.serialize(td)
        # Send
        data = dict()
        data['type'] = 'query'
        data['query'] = content
        log.log.debug("data is %s", data)
        rcvdict = self.connection.send(data)
        if rcvdict['status']==200:  # Success
            log.log.info("data upload success")
            # TODO 解析回传报文
            if rcvdict['result'] == 200:
                log.log.info("Word hit,%s",rcvdict['filename'])
            elif rcvdict['result']==404:
                log.log.warning("Word not found,check if the word is incorrect or the key is not recovered correctly")                
                        
        else:
            log.log.error("Upload Failed")

    def Hash1(self, w):
        # 先对关键词w进行md5哈希
        hv = Hash1pre(str(w).encode('utf8')).hexdigest()
        
        # 再对md5值进行group.hash哈希，生成对应密文
        # 完整的Hash1由md5和group.hash组成
        hv = self.group.hash(hv, type=G1)
        return hv


Hash2 = hashlib.sha256

if __name__ == "__main__":

    menu = Menu()
    menu.run()
