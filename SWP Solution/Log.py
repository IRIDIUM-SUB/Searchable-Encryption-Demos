'''
Author: I-Hsien
Date: 2021-01-29 20:00:24
LastEditTime: 2021-01-29 20:54:56
LastEditors: I-Hsien
Description: Common Logging Module
FilePath: \Searchable-Encryption-Demos\SWP Solution\Log.py
Comments: None
'''
import logging as log

log.basicConfig(level="DEBUG",format="%(asctime)s-[%(levelname)s]:%(message)s")
        