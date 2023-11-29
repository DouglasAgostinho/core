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


    def network_initialization(self):
        pass
        # issue - (create auto message to inform network ingress and request peers info feedback)

    def message_proccessing(self, msg_type, message, rcv_hash=None):
        #If rcv_hash is available then message received, if is None then send message

        msg_hash = SHA512.new(message).digest()
        msg_header = str(len(message))
        msg_header = msg_header.rjust(self.HEADER - 2, "0")                
        msg_header = msg_type + msg_header.encode(self.FORMAT) + msg_hash                
        send_msg = msg_header + message
        
        #If text
        if msg_type == b"01":            

            print(f"\n{message=}")

            #Check hash and confirm message integrity
            
            if rcv_hash:
                if msg_hash == rcv_hash:
                    print(self.MSG_CONFIRMED) 
                    return(self.MSG_CONFIRMED)
                else:
                    print(self.MSG_CORRUPTED) 
                    return(self.MSG_CORRUPTED)
            else:                
                return (send_msg)

        #If file
        elif msg_type == b"02":

            salt = str(random.randint(1, 9999))
            #salt = salt.decode(self.FORMAT)

            salt = salt + "_Linux_rcv.pdf" 

            #Check hash and confirm message integrity
            msg_hash = SHA512.new(message).digest()
            if rcv_hash:
                if msg_hash == rcv_hash:
                    print(self.MSG_CONFIRMED)                 
                    with open(salt, "wb") as f: #issue - (verify if file already exists and change name if necessary)
                        f.write(message)

                    return(self.MSG_CONFIRMED)
                else:
                    print(self.MSG_CORRUPTED) 
                    return(self.MSG_CORRUPTED)
            else:
                return (send_msg)                

        
