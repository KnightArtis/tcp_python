import os
import socket
from threading import Thread
import argparse
import requests
sockets=[]                          #存放已登录客户端的列表

parser = argparse.ArgumentParser(description='Chat application')
parser.add_argument('--host',default='127.0.0.1',help='绑定IP地址')
parser.add_argument('--port',type=int,default=5678,help='绑定端口')
args = parser.parse_args()

addr = ''                           #客户端的连接地址,定义全局变量为空便于重置地址
Dict = dict()                       #存放key和value的字典
State = dict()                      #存放客户端name和password的字典
command = ''
msg = ''
table = ''
def Dict_write():
    global Dict
    with open(str(args.host),'a+') as file: #创建服务器文件存放客户端的key和value字典
        dic = file.read()
        if dic != "":
            Dict = eval(dic)
        file.write('\n'+str(Dict))      #将内存中的字典保存在服务器文件中
def main():
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind((args.host, args.port))
    server_socket.listen(5)
    while True:
        global addr,State,command,msg,table
        client_socket,addr = server_socket.accept() 
        print(addr,'连接成功')
        Readmsg=Thread(target=readmsg,args=(client_socket,))        #为客户端开启独立的线程
        Readmsg.start()
        Dict_write()
        try:
            with open('auth.txt','r') as file:          #打开存有name和password的auth文件
                    state = file.read()
                    State = eval(state)                         #将name和password提取到State字典中
                    print('auth:',State)
        except FileNotFoundError:
            print("未找到配置文件")
            os._exit(0)

def readmsg(client_socket):          #定义readmsg函数,接受来自客户端的命令
    try:
        while True:
            command = client_socket.recv(1024).decode("utf-8").strip()
            table = command.split(" ")
            print(addr,"操作",command)
            if 'AUTH' in command[:4] and State.get(table[1]) and State[table[1]] == table[2]:       #客户端登录后将其加入sockets列表中,想到一个客户端重复登录多个账号的问题,还没想到解决方案
                if client_socket not in sockets:
                    sockets.append(client_socket)
                    print(addr,'登录成功,目前在线人数为',len(sockets))
                    msg = '登录成功'
                else:
                    msg = "您已登录成功，无需重新登录"
            elif client_socket in sockets:
                with open(str(args.host),'r+') as file:
                    dic = file.read()
                #print(table,'\n',Dict)
                if 'SET' in command[:3] and ' ' in command[:4]:
                    try:
                        Dict[table[1]]=table[2]
                        Dict_write()
                        msg = ""
                    except IndexError:
                        msg = "\nSET指令应符合(SET)空格(key)空格(value)"
                elif 'GET' in command[:3] and ' ' in command[:4]:
                    if Dict.get(table[1]):
                        msg = Dict[table[1]]
                    else:
                        msg = "\n"
                elif 'URL' in command[:3] and ' ' in command[:4]:
                    if Dict.get(table[1]):
                        msg = Dict[table[1]]
                    else:
                        request = requests.get(table[1])                    #拿到网站源代码存到一个以网站命名的文件中                       #这一段有bug
                        with open(table[1],'w+') as web_data:               #把网站文件存入一个文件中,方便获取网站大小                      #requests无法实现
                            web_data.write(request)                                                                                         #运行就报错
                        table[2] = Dict[str(os.path.getsize(table[1]))]     #获取文件大小并作为值与对应的键配对,存到Dict字典中              #没有找到方法修改
                        Dict_write()
                        msg = table[2]
                elif command == 'q' and client_socket in sockets:           #客户端输入为'q'时,将已登录客户端socket从sockets列表中移除
                    sockets.remove(client_socket)
                    print(addr,'已下线,目前在线人数为',len(sockets))
                    client_socket.close()
                else:
                    msg = '请输入正确的操作\n','SET,GET,URL.'
            else:
                msg = '-1'
            client_socket.sendall(msg.encode('utf-8'))
    except:
        if client_socket in sockets:                                    #已登录客户端异常,中断连接时,从已登录列表中移除
            sockets.remove(client_socket)
            print(addr,'连接中断,目前在线人数为',len(sockets))              #未登录客户端异常,中断连接时,打印中断信息
        client_socket.close()
if __name__=="__main__":
    main()

