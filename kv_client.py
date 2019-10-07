import socket
import argparse

parser = argparse.ArgumentParser(description='Chat application')
parser.add_argument('--host',default='127.0.0.1',help='监听IP地址')
parser.add_argument('--port',type=int,default=5678,help='监听端口')
args = parser.parse_args()

client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((args.host, args.port))
while True:
    msg=input("请输入命令:")
    client_socket.send(msg.encode('utf-8'))
    if msg == "q":
        break
    recv_data=client_socket.recv(1024)
    if recv_data == '':
        pass
    else:
        print(recv_data.decode('utf-8'))

client_socket.close()
