#以下为引用
import socket
import pymysql
import datetime
import sys
import datetime

#以下为函数
def Get_IP():       #获取服务器名称和服务器IP地址的函数
    hostname=socket.gethostname()
    ipaddr=socket.gethostbyname(hostname)
    print("服务器的名称为：",hostname,",服务器的IP地址为：",ipaddr)

def Send_Data(send_data,ip='192.168.0.7',port=8080,users=10):     #数据发送函数
    try:
        conn,addr=web.accept()
        conn.sendall(send_data.encode())
        print("数据发送成功")
    except Exception as error:
        print(str(error))
        Log_Writing(error)

def Log_Writing(data_writing):      #日志记录函数
    DT=datetime.datetime.now()
    Log=open(sys.path[0]+'\Log.txt','a',encoding='utf-8')
    Log.write('##' + str(DT) + '##' + '\0\0\0' + str(data_writing)+'\n')
    Log.close

def Data_Process(data_to_storage):     #数据处理函数
    db=pymysql.connect(host="localhost",user="Jameswu",password="Wygwyg_123",database="main_database",charset='utf8')
    cursor=db.cursor()
    Front_Identifying_Code=data_to_storage[:3]
    Behind_Identifying_Code=data_to_storage[len(data_to_storage)-3:]
    if Front_Identifying_Code=="<<<" and Behind_Identifying_Code==">>>":        #传感器数据处理
        True_Code=data_to_storage[3:len(data_to_storage)-3]
        Data_List=True_Code.split(',')
        try:
            cursor.execute("SELECT DevCode FROM devid WHERE DevID ="+Data_List[0])
            results=cursor.fetchall()
            for row in results:
                DevCode_Check=row[0]
        except Exception as error:
            print(str(error))
            db.rollback()
        if DevCode_Check==Data_List[1]:
            print("正在存储来自设备号为："+Data_List[0]+"的单片机的数据")
            try:
                cursor.execute("INSERT INTO data (DevID,Temperature,Humidity,Dirt_Humidity,illumination,OTime) VALUES (" + Data_List[0] + "," + Data_List[2] + ","+Data_List[3] + ","+Data_List[4] + ","+Data_List[5] + ",now())")
                db.commit()
            except Exception as error:
                print(str(error))
                Log_Writing(error)
                db.rollback()
            db.close
        else:
            Send_Data("[[[DevID_Error]]]")      #向单片机发送DevID错误的错误码
    elif Front_Identifying_Code=="[[[" and Behind_Identifying_Code=="]]]":      #单片机错误码数据处理
        True_Error_Code=data_to_storage[2:len(data_to_storage)-3]
        Error_Code_List=True_Error_Code.split(',')
        try:
            error_DevCode_Check=cursor.execute("SELECT DevCode FROM devid where DevID="+Error_Code_List[0])
            db.commit()
        except Exception as error:
            print(str(error))
            Log_Writing(error)
            db.rollback()
        if error_DevCode_Check==Error_Code_List[1]:
            print("正在存储来自设备号为："+Error_Code_List[0]+"的单片机的错误码")
        else:
            Send_Data("[[[DevID_Error]]]")      #向单片机发送DevID错误的错误码
    else:
        Send_Data("[[[Repeat]]]")       #接收到不符合规范的数据，请求单片机重新发送

#以下为主程序
raw_data=""
Get_IP()
web=socket.socket()
web.bind(('192.168.0.7',8080))
web.listen(10) 
print("开始侦听，等待单片机连接...")
while raw_data=="":  
    conn,addr=web.accept()
    raw_data=conn.recv(1024).decode()
    if raw_data!="":
        Data_Process(raw_data)
        raw_data=""