import socket
import threading
import argparse

parser = argparse.ArgumentParser(description='Chat application')
parser.add_argument('--host',default='127.0.0.1',help='监听IP地址')
parser.add_argument('--port',type=int,default=5678,help='监听端口')
args = parser.parse_args()

client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((args.host, args.port))

state = True

def readmsg(client_socket):
    global state
    while state:
        recv_data=client_socket.recv(1024)
        if recv_data == '':
            pass
        else:
            print(recv_data.decode('utf-8'))

def writemsg(client_socket):
    global state
    while state:
        msg=input("请输入命令:")
        client_socket.send(msg.encode('utf-8'))
        if msg.endswith("q"):
            state = False
            break
Readmsg=threading.Thread(target=readmsg,args=(client_socket,))
Writemsg=threading.Thread(target=writemsg,args=(client_socket,))
Writemsg.start()
Readmsg.start()

Writemsg.join()
Readmsg.join()
client_socket.close()
