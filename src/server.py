#------------------------------------------------------
# Project commom section
#
# Message type codes (m_type) variable
# 0x - Messages with confirmation
# 01 - user input
# 02 - file
# 03 - confirmation / close message
# 2x - Messages without confirmation (requests)
#
# Received messages should starts as below
# 02 char of message type
# 14 char for message length
# 64 char for message hash (SHA-512)
# 
#------------------------------------------------------

#Import section
import queue
import socket
import select
from Crypto.Hash import SHA512
from Crypto.Random import random
import sys


class Network():
    def __init__(self, host=None, port=None):
        #Variable and constants definition
        if host is None:
            self.HOST = "localhost"
        else:
            self.HOST = host

        if port is None:
            self.PORT = 65440
        else:
            self.PORT = port

        #Network constants
        self.FORMAT = "utf-8"        
        self.HEADER = 16
        self.PARTICIPANTS = 100 #Be aware with system max of file descriptors
        self.MSG_CONFIRMED = b"![MESSAGE CONFIRMED]!"
        self.MSG_CORRUPTED = b"![MESSAGE CORRUPTED]!"
