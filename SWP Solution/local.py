'''
Author: I-Hsien
Date: 2021-01-28 20:02:50
LastEditTime: 2021-01-31 20:36:02
LastEditors: I-Hsien
Description: Client Program
FilePath: \Searchable-Encryption-Demos\SWP Solution\local.py
Comments: None
'''
import network
import pprint
import os
import random
import string
import Log as log


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
            "2": "",
            "0": self.quit
        }

    def display_menu(self)->None:
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
        os._exit()  # Exit Now


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


if __name__ == "__main__":

    menu = Menu()
    menu.run()
