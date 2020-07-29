#_*_coding:utf-8_*_
import requests
import json
import time
from bs4 import BeautifulSoup
import sqlite3

def get_activity_data():
    user_name=input('请输入郁金香运动登录用户名：')
    password=input('请输入郁金香运动登录密码：')
    user_agent=r'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
    referer=r'http://www.tulipsport.com/loginpage?next=http%3A%2F%2Fwww.tulipsport.com%2Fdashboard'

    index_url=r'http://www.tulipsport.com/dashboard'
    activity_data_url=r'http://www.tulipsport.com/getfeeds?feedtype=mine&&pi='

    header = {'User-Agent':user_agent,'Referer':referer}
    v_session=requests.Session()

    #f=v_session.get(index_url,headers=header)

    #首先登陆获取cookice
    login_url='http://www.tulipsport.com/login'
    login_data={'email':user_name,'password':password,'rememberme':'0'}

    r=v_session.post(login_url,login_data,headers=header)
    login_stauts=r.json()
    if login_stauts['success']=='true':
        print('登陆成功！')
        #然后通过cookice 使用get请求 获取activity 数据

        conn=sqlite3.connect('tulipsport.db')
        cur=conn.cursor()
        cur.execute('SELECT runtime FROM run_date ORDER BY id DESC LIMIT 1')
        last_rundate=cur.fetchone()[0]
        nextPage='1'

        while(True):

            activity_data=v_session.get(activity_data_url+nextPage,headers=header)
            activityData_dic=activity_data.json()
            nextPage=activityData_dic['nextpage']
            feadlist=activityData_dic['feedlist']

            if len(feadlist)==0:
                print('没有更多')
                break

            # print(activityData_dic['feedlist'])
            for vid in feadlist:
                activity_id=vid['activities'][0]['activity_id']
                #根据activity数据遍历得到activity id 拼接url 获取最终的数据。
                activity_info_url='http://www.tulipsport.com/activity/'+activity_id
                r=v_session.get(activity_info_url,headers=header)
                # print(type(r))
                bsObj=BeautifulSoup(r.text,"html.parser")
                activity_date_time=bsObj.find("time").get_text()



                activity_date=activity_date_time.split(' ')[0].replace('年', '-').replace('月', '-')[:-1]
                activity_start_time=activity_date_time.split(' ')[1]
                activity_week=activity_date_time.split(' ')[2]

                print(last_rundate+'    '+activity_date)
                if time.mktime(time.strptime(last_rundate,"%Y-%m-%d"))>=time.mktime(time.strptime(activity_date,"%Y-%m-%d")):
                    print('已经记录过')
                    break
                activity_type=bsObj.find("div",{"class":"name"}).contents[3].strip()
                print(activity_type)
                print(activity_date_time)

                ul_root=bsObj.find("ul",{"class":"inline-stats section"})
                li_list=ul_root.findAll("li")
                op_dic={}
                for li in li_list:
                    _strip = li.div.get_text().replace('\n', '').strip()
                    _value = li.strong.get_text().replace('\n', '').strip().replace('  ', '')
                    op_dic[_strip]= _value

                print(op_dic)
                #全部距离
                try:
                    total_distance=op_dic['距离'][:-2]
                except KeyError:
                    total_distance =''

                #运动时间
                try:
                    activity_time=op_dic['运动时间']
                except KeyError:
                    activity_time =''

                #运动总用时
                try:
                    total_time=op_dic['总时间']
                except KeyError:
                    total_time =''

                #累计爬升
                try:
                    cumulative_climb=op_dic['累计爬升'][:-1]
                except KeyError:
                    cumulative_climb=''

                #累计下降
                try:
                    cumulative_decline=op_dic['累计爬升']
                except KeyError:
                    cumulative_decline=''

                #平均配速
                try:
                    average_speed=op_dic['平均配速'][:-3]
                except KeyError:
                    average_speed=op_dic['平均时速'][:-3]

                #消耗卡路里
                try:
                    calorie_consumption=op_dic['消耗卡路里'][:-3]
                except KeyError:
                    calorie_consumption =''

                #运动设备
                activity_device=op_dic['运动设备']

                sql='''insert into activity(
                        activity_date,activity_start_time,activity_week,total_distance,activity_type,activity_time,total_time,
                        cumulative_climb,cumulative_decline,average_speed,calorie_consumption,activity_device
                        )values(?,?,?,?,?,?,?,?,?,?,?,?)'''
                para=(activity_date,activity_start_time,activity_week,total_distance,activity_type,activity_time,total_time,
                      cumulative_climb,cumulative_decline,average_speed,calorie_consumption,activity_device)

                cur.execute(sql,para)
                time.sleep(3)
        date_now = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        run_date_sql='insert into run_date(runtime)values(?)'

        cur.execute(run_date_sql,(date_now,))


        conn.commit()
        cur.close()
        conn.close()

        print('运动数据采集成功')

    else:
        print('登陆失败')
        exit(0)

import pandas as pd
def show_data():
    conn=sqlite3.connect('tulipsport.db')
    cur=conn.cursor()
    cur.execute('''SELECT sum(total_distance) as '总路程KM' \
                FROM activity WHERE activity_type='走路' and cumulative_climb<100''')
    walk_total_distance=cur.fetchone()[0]

    cur.execute('''SELECT sum(total_distance) as '总路程KM' FROM activity WHERE activity_type='跑步';''')
    running_total_distance=cur.fetchone()[0]

    cur.execute('''SELECT sum(total_distance) as '总路程KM',sum(cumulative_climb) as '总爬升M' \
                FROM activity WHERE activity_type='走路' and cumulative_climb>='100';''')
    mountaineering_total=cur.fetchone()

    print('散步总路程{0}'.format(int(walk_total_distance)))
    print('跑步总路程{0}'.format(int(running_total_distance)))
    print('爬山总路程{0}\n总爬升{1}'.format(int(mountaineering_total[0]),mountaineering_total[1]))


    cur.close()
    conn.close()


if __name__ == '__main__':
    w=int(input('请选择功能：\n1获取数据\n2展示数据'))
    if w==1:
         get_activity_data()

    else:

        show_data()





