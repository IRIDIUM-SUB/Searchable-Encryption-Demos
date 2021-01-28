'''
Author: I-Hsien
Date: 2021-01-28 20:02:50
LastEditTime: 2021-01-28 22:09:52
LastEditors: I-Hsien
Description: Client Program
FilePath: \Searchable-Encryption-Demos\SWP Solution\local.py
Comments: None
'''
import network
import pprint
import os
import random
FUNCTIONS=['Test Connection']
if __name__=="__main__":
    
    menu=Menu()
    menu.run()
class Menu(object):
    '''
    处理菜单事务，并且这里调用事务类。
    '''
    def __init__(self):
        self.pp = pprint.PrettyPrinter(indent=4,width=41, compact=True)
        self.choices = {
            "1": self.Events.connection_test,
            "2": self.thing.clean_dir1,
            "3": self.thing.clean_dir2,
            "0": self.quit
        }
    def display_menu(self):
        self.pp.pprint("SMP Demo")
        self.pp.pprint("1. Connection Test")
        self.pp.pprint("2. Generate Wordlist")
        self.pp.pprint("3. Encrypt and Upload")
        self.pp.pprint("4. Query")
        self.pp.pprint("0. Exit")
        self.pp.pprint("-----------------------")
    def run(self):
        while True:#Main Loop
            os.system("cls")
            self.display_menu()
            try:
                choice = input("Enter an option: ")
            except Exception as e:
                print("Please input a valid option!")
                continue
            choice = str(choice).strip()
            action = self.choices.get(choice)#在self.choice中查找对应的方法
            if action:
                action()
            else:
                print("{0} is not a valid choice".format(choice))
    def quit(self):
        print("\nThank you for using this script!\n")
        os._exit() #Exit Now       
class Events(object):
    '''
    事务处理接口
    '''
    def __init__(self):
        self.connection=network.connection()# initialize connection class
    def connection_test(self):
        '''
        Test Connection by sending test json
        {
            "type":"test",
            
            "test":1+2//使用eval()检验
        }
        '''
        
        data=dict()# Preparing data
        data["type"]="test"
        num1=random.randint(0,1000)
        num2=random.randint(0,1000)
        data["test"]=str(num1)+"+"+str(num2)
        rcvdict=self.connection.send(data)
        if rcvdict['result']==num1+num2:
            print("Ping Success")
        else:
            print("Ping Failed")
        