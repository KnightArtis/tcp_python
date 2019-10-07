import socket
from threading import Thread
import argparse
sockets=[]

parser = argparse.ArgumentParser(description='Chat application')
parser.add_argument('--host',default='127.0.0.1',help='绑定IP地址')
parser.add_argument('--port',type=int,default=5678,help='绑定端口')
args = parser.parse_args()

addr = ''                   #客户端连接的地址,定义全局变量为空便于重置地址
Dict = dict()                #存放key和value的字典
def Dict_write():
    global Dict
    with open(str(args.host),'a+') as file:      #创建服务器文件存放客户端的key和value字典
        dic = file.read()
        if dic != "":
            Dict = eval(dic)
        file.write('\n'+str(Dict))       #将内存中的字典保存在文件中
def main():
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind((args.host, args.port))
    server_socket.listen(5)
    while True:
        global addr
        client_socket,addr = server_socket.accept()
        Readmsg=Thread(target=readmsg,args=(client_socket,))         #为客户端开启线程
        Readmsg.start()
        Dict_write()
        sockets.append(client_socket)
        print(addr,'连接成功,目前在线人数为',len(sockets))

def readmsg(client_socket):          #定义readmsg函数,接受来自客户端的命令
    try:
        while True:
            command = client_socket.recv(1024).decode("utf-8")
            print(addr,"操作",command)
            with open(str(args.host),'r+') as file:
                dic = file.read()
            table = command.split(" ")
            #print(table,'\n',Dict)
            if 'SET' in command[:3] and ' ' in command[:4]:                    
                try:                                                            
                    Dict[table[1]]=table[2]                                     
                    Dict_write()                                                
                    msg = ''                                                    
                except IndexError:                                              
                    msg = "\nSET指令应符合(SET)空格(key)空格(value)"
            elif 'GET' in command[:3] and ' ' in command[:4]:
                if Dict.get(table[1]):
                    msg = Dict[table[1]]
                else:
                    msg = "\n"
            elif command == 'q':
                sockets.remove(client_socket)
                print(addr,'已下线,目前在线人数为',len(sockets))                  #客户端正常退出
                client_socket.close()
                break
            else:
                msg = '\n请输入正确的操作.'
            client_socket.send(msg.encode('utf-8'))
    except:
        sockets.remove(client_socket)
        print(addr,'连接中断,目前在线人数为',len(sockets))                     #客户端异常离线
        client_socket.close()
if __name__=="__main__":
    main()
