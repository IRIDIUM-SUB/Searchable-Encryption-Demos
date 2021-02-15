'''
Author: I-Hsien
Date: 2021-01-28 20:02:50
LastEditTime: 2021-02-15 13:41:25
LastEditors: I-Hsien
Description: Client Program
FilePath: \Searchable-Encryption-Demos\SWP Solution\local.py
Comments: None
'''
import network
import pprint
import os
import sys
import random
import string
import Log as log
import secrets
import base64
import hmac
from cryptography.fernet import Fernet


class Menu(object):
    '''
    处理菜单事务，并且这里调用事务类。
    '''

    def __init__(self):
        self.pp = pprint.PrettyPrinter(indent=4, width=41, compact=True)
        self.client = ClientTransactionInterface()

        self.choices = {
            "1": self.client.connection_test,
            "3": self.client.gen_wordlist,
            "2": self.client.gen_key,
            "0": self.quit
        }

    def display_menu(self) -> None:
        self.pp.pprint("SMP Demo")
        self.pp.pprint("1. Connection Test")
        self.pp.pprint("2. Generate Key")
        self.pp.pprint("3. Generate Wordlist")
        self.pp.pprint("4. Encrypt and Upload")
        self.pp.pprint("5. Query")
        self.pp.pprint("0. Exit")
        self.pp.pprint("-----------------------")
        log.log.debug("Menu displayed")
        return

    def run(self):
        while True:  # Main Loop
            os.system("cls")
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
            os.system("PAUSE")

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

    def gen_wordlist(self, FILES_AMOUNT=10, WORDS_PER_FILE=500, WORD_LEN=5) -> None:
        '''
        生成若干个文件，每个文件包含若干个单词，单词不重复且随机
        文件名为1,2,3,4,5
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

    def gen_key(self, FILES_AMOUNT=10, SEED_LEN=30):
        log.log.info("Start generating list")
        k1 = Fernet.generate_key()  # k
        k2 = Fernet.generate_key()  # k'
        log.log.debug("key generated:k1=%s,k2=%s",
                      str(k1), str(k2))
        # Gen Seed
        SeedList = list()
        for _ in range(FILES_AMOUNT):
            SeedList.append(secrets.token_bytes(nbytes=SEED_LEN))
        log.log.debug("Seed generated:seed=%s", str(SeedList))

        # Write Files
        with open("k.bin", "wb") as f:
            f.write(k1)
            f.close()
        with open("k'.bin", "wb") as f:
            f.write(k2)
            f.close()
        with open("seed.bin", "wb") as s:
            for i in range(FILES_AMOUNT):  # Write seedlist
                s.write(SeedList[i])
            s.close()
        return

    def load_keys(self, FILE_LIST=["k.bin", "k'.bin", "seed.bin"]) -> list:
        '''
        description: Load keys via files
        param {None}
        return {list of keys,[k1,k2,seed]}
        '''
        try:
            f = open("k.bin", "rb")
            k1 = f.read(f)
        except IOError:
            log.log.error("No Such File:k")
            return None
        else:
            log.log.info("Read k successed")
            f.close()

        try:
            f = open("k'.bin", "rb")
            k2 = f.read(f)
        except IOError:
            log.log.error("No Such File:k'")
            return None
        else:
            log.log.info("Read k' successed")
            f.close()

        try:
            f = open("seed.bin", "rb")
            s = f.readlines(f)
            # Processing
            p = list()
            for items in s:
                p.append(items.strip())

        except IOError:
            log.log.error("No Such File:seed")
            return None
        else:
            log.log.info("Read seed successed")
            f.close()
        log.log.debug("load key:%s", str([k1, k2, p]))
        return [k1, k2, p]

    def encrypt(self, FILES_AMOUNT=10):
        # load keys
        KeysList = self.load_keys()  # [k1,k2,s]
        if not KeysList:
            log.log.error("Load key failed:see above for more info")
            return
        k1 = KeysList[0]
        k2 = KeysList[1]
        SeedList = KeysList[2]

        # load words
        CHIPER_LEN = 74  # chipertext should be byte and length is 74
        PlainList = list()
        for i in range(FILES_AMOUNT):
            filename = str(i+1)+".txt"
            with open(filename, "r") as f:
                rawstr = f.read()
                f.close()
            tmplist = rawstr.split(",")
            TmpListBin = list()
            for item in tmplist:
                TmpListBin.append(item.encode(encoding='utf-8'))
            PlainList.append(TmpListBin)
            log.log.debug("Plainlist is ", str(PlainList))
        # Ready for symmetric encryption
        f = Fernet(k2)
        EncryptList = list()  # To save encrypted words.[[file1],[file2],...]
        for i in range(len(PlainList)):  # For each file
            WordList = PlainList[i]
            seed = SeedList[i]  # Select seed
            tmplist = list()  # NOTE Base-64 decoded, for division
            for j in range(len(WordList)):  # For each word, main loop
                plain = WordList[j]

                ciphertext = f.encrypt(plain)  # Base-64 encoded

                # Base64 decoded chipertext,should be byte and length is 74
                FlatChipertext = base64.urlsafe_b64decode(ciphertext)+b"\x00"
                LeftChipertext, RightCHipertext = [
                    FlatChipertext[:CHIPER_LEN/2], FlatChipertext[CHIPER_LEN/2:]]

                # Generate key ki, using hmac-md5,ki=f(L,k')
                k = hmac.new(k1, LeftChipertext,
                             digestmod='MD5').digest()  # k is byte
                log.log.debug("Generate k is", k)

                # Seed stream
                # Use LSFR, but bin string?

                log.log.debug("Encrypt finish,%s->%s",
                              str(plain), str(ciphertext))
            log.log.debug("One file encrypt finished")

        pass


if __name__ == "__main__":

    menu = Menu()
    menu.run()
