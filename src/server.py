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
from tools import Logger
import queue
import socket
import select
from Crypto.Hash import SHA512
from Crypto.Random import random
import sys

log = Logger()

class Network():
    def __init__(self, host=None, port=None):
        #Variable and constants definition
        if host is None:
            self.HOST = "localhost"
        else:
            self.HOST = host

        if port is None:
            net_init = True
            while net_init:
                for port in range(10, 100, 10):
                    try:
                        self.PORT = 65400 + port
                        net_init = False
                    except Exception as e:
                        log.to_file("error", str(e))
        else:
            self.PORT = port

        #Network constants
        self.FORMAT = "utf-8"        
        self.HEADER = 16
        self.PARTICIPANTS = 100 #Be aware with system max of file descriptors
        self.MSG_CONFIRMED = b"![MESSAGE CONFIRMED]!"
        self.MSG_CORRUPTED = b"![MESSAGE CORRUPTED]!"


    def network_initialization(self):

        message = f"{self.PORT}"

        self.message_proccessing(msg_type=b"00", message=message)
        pass
        # issue - (create auto message to inform network ingress and request peers info feedback)

    def message_proccessing(self, msg_type, message, rcv_hash=None):
        #If rcv_hash is available then message received, if is None then send message

        msg_hash = SHA512.new(message).digest()
        msg_header = str(len(message))
        msg_header = msg_header.rjust(self.HEADER - 2, "0")                
        msg_header = msg_type + msg_header.encode(self.FORMAT) + msg_hash                
        send_msg = msg_header + message

        #If initialization message
        if msg_type == b"00":
            if rcv_hash:    # issue - Create initialization message receive method
                pass
            else:
                return (send_msg)
        
        #If text
        elif msg_type == b"01":            

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

        
class Client(Network):
    def __init__(self, host=None, port=None):
        super().__init__(host, port)
    
    def client_send_message(self):
        client = socket.socket()
        #self.conn.connect(("localhost", 65434))
        client.connect((self.HOST, self.PORT))
        msg = input("Digite sua mensagem").encode(self.FORMAT)
        client.send(msg)
        client.close()
        

class Server(Network):
    def __init__(self, host=None, port=None):
        super().__init__(host, port)    
            

    def server_run(self):
        #Server configuration and initialization     
         
        #(I/O) variables for select to monitor
        inputs = []
        outputs = []
        #Dictionary for output messages by connection
        message_queues = {}           

        #Create Non-Blocking IPV4 / TCP socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(False)

        #Set server to listen on defined PORT and IP address
        server.bind((self.HOST, self.PORT))
        server.listen()
        print(f"{server=} Listening")

        #Insert configurated server to be monitored for income connections
        inputs.append(server)
        inputs.append(sys.stdin)

        #Lists to receive data from various connections (index by id from fileno() method)
        bytes_to_rcv, bytes_rcvd, package_length, data_bytes = [], [], [], []

        for _ in range(self.PARTICIPANTS):
            bytes_to_rcv.append(0)
            bytes_rcvd.append(b"")
            data_bytes.append(b"")

            # bytes to receive per conn.recv
            package_length.append(2048)                            

        while inputs:

            #Lists of monitored system IO
            readable, writable, exceptional = select.select(inputs, outputs, inputs, 3)

            for s in readable:
                #Iterate through inputs and verify if is server or connection

                if s is server:
                    
                    #If server accept new connection
                    conn, addr = s.accept()
                    conn.setblocking(False)

                    #Insert new connection in inputs list
                    inputs.append(conn)
                    print(f"\n Connceted \n{conn=} \n{addr=}\n")

                    #Give this connection a queue for data to reply
                    message_queues[conn] = queue.Queue()

                elif s is sys.stdin:
                    
                    send_msg = sys.stdin.readline()
                    
                    print(f"\n{send_msg=}\n")

                else:
                    #If connection start to receive data
                    data_bytes[s.fileno()] = s.recv(package_length[s.fileno()])                    

                    #If data is available start data segregation
                    if data_bytes[s.fileno()]:
                        
                        # Add output channel for response
                        if s not in outputs:
                            outputs.append(s)
                        
                        #If data is the first batch initiate segregation
                        if bytes_to_rcv[s.fileno()] == 0:

                            #(Check project common section for message HEADER info)
                            message = data_bytes[s.fileno()]
                            msg_header = message[:16]
                            msg_type = msg_header[:2]
                            msg_length = msg_header[2:]
                            msg_hash = message[16:80]
                            message = message[80:(80 + int(msg_length))]

                            #Set the package to receive length in the bytes to receive (speed up transfer)
                            package_length[s.fileno()] = int(msg_length)
                            
                            #Insert bytes received and message len
                            bytes_rcvd.insert(s.fileno(), message)
                            
                            bytes_to_rcv[s.fileno()] += len(message)
                            
                            #Decrease the length of received message from package total
                            package_length[s.fileno()] -= len(message)
                            
                            #If message received is already complete then proceed with message processing
                            if bytes_to_rcv[s.fileno()] >= int(msg_length):
                                
                                #Remove received data with "pop" method returning its value to message variable
                                message = bytes_rcvd.pop(s.fileno())

                                #Set control variables to standard values
                                bytes_to_rcv[s.fileno()] = 0
                                package_length[s.fileno()] = 2048

                                #Proccess received message and return result to sender
                                message_queues[s].put(self.message_proccessing(msg_type, message, msg_hash))
                            
                        
                        #If data is longer than standard package lenght
                        elif bytes_to_rcv[s.fileno()] < int(msg_length):
                            
                            bytes_rcvd[s.fileno()] += data_bytes[s.fileno()]

                            #Update the ammount of data already received
                            bytes_to_rcv[s.fileno()] += len(data_bytes[s.fileno()])
                            package_length[s.fileno()] -= len(data_bytes[s.fileno()])
                            
                            #If transmission completed                            
                            if bytes_to_rcv[s.fileno()] >= int(msg_length):
                            
                                #Remove received data with "pop" method returning its value to message variable
                                message = bytes_rcvd.pop(s.fileno())
                                bytes_rcvd.insert(s.fileno(), b"")
                            
                                #Set control variables to standard values
                                bytes_to_rcv[s.fileno()] = 0
                                package_length[s.fileno()] = 2048
                            
                                #Proccess received message and return result to sender
                                message_queues[s].put(self.message_proccessing(msg_type, message, msg_hash))
                                                        

                    else:
                        #If no data remove from inputs list and close connection
                        print(f"{data_bytes[s.fileno()]=} closing connection")
                        inputs.remove(s)
                        s.close()
                        print(f"Connection closed")

            for s in writable: # issue -- define correct writable method
                #outputs
                try:
                    next_msg = message_queues[s].get_nowait()
                except queue.Empty: 
                    #no messages in queue, stop check for write
                    print(f"Output queue for {s.getpeername()}, is empty")
                    outputs.remove(s)
                else:
                    print(f"Sending {next_msg, s.getpeername()}")                    
                    s.send(next_msg)

            #Exceptional
            for s in exceptional:
                print(f"Handling exceptional condition for {s.getpeername()}")
                #Stop listening for input / output on the connection
                inputs.remove(s)
                if s in outputs:
                    outputs.remove(s)
                s.close()

                #Remove message queue
                del message_queues[s]


if __name__ == "__main__":

    s = Server()

    s.server_run()
