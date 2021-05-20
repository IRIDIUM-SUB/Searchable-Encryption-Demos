'''
Author: I-Hsien
Date: 2021-01-29 20:00:24
LastEditTime: 2021-05-18 12:09:59
LastEditors: I-Hsien
Description: Common Logging Module
FilePath: \Searchable-Encryption-Demos\SWP Solution\Log.py
Comments: None
'''
import logging as log

log.basicConfig(level="INFO",format="%(asctime)s-[%(levelname)s]:%(message)s")
        