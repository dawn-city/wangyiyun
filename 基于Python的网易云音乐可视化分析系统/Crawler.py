import pymysql
import re
import requests
from pyncm import apis
import threading
import queue

lock=threading.Lock()


headers={
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5',
    'cookie': 'NMTID=00O7d_3nlhUItTBAkzApP2Zf9_fQI8AAAF7xhimXA; _ntes_nnid=5fd86f335684818723aed2ecdec97222,1631165504713; _ntes_nuid=5fd86f335684818723aed2ecdec97222; WEVNSM=1.0.0; WNMCID=xwidqh.1631236735123.01.0; WM_TID=NAd%2BPIDOY%2F1EFUUABEI%2F3uCnZJcf0NFY; nts_mail_user=cyx2012scut@163.com:-1:1; NTES_CMT_USER_INFO=91459384%7C%E6%9C%89%E6%80%81%E5%BA%A6%E7%BD%91%E5%8F%8B05sUYU%7Chttp%3A%2F%2Fcms-bucket.nosdn.127.net%2F2018%2F08%2F13%2F078ea9f65d954410b62a52ac773875a1.jpeg%7Cfalse%7CY3l4MjAxMnNjdXRAMTYzLmNvbQ%3D%3D; Qs_lvt_382223=1633076165; Qs_pv_382223=1315540341041694200%2C4570867357934815000; MUSIC_R_T=1630769723983; MUSIC_A_T=1630769658380; __oc_uuid=8e8a7900-3243-11ec-9257-3b8b46cf2acf; ntes_kaola_ad=1; __root_domain_v=.163.com; _qddaz=QD.399235936529813; OUTFOX_SEARCH_USER_ID_NCOO=775123359.3579957; mp_MA-BFF5-63705950A31C_hubble=%7B%22sessionReferrer%22%3A%20%22https%3A%2F%2Fke.study.163.com%2Fcourse%2Fdetail%2F100096107%3FinLoc%3Dweb_sy_zdymk_1%26Pdt%3DydkWeb%22%2C%22updatedTime%22%3A%201637465397473%2C%22sessionStartTime%22%3A%201637465397467%2C%22sendNumClass%22%3A%20%7B%22allNum%22%3A%202%2C%22errSendNum%22%3A%200%7D%2C%22deviceUdid%22%3A%20%221b854929-4192-41fd-962e-331ac8c969a0%22%2C%22persistedTime%22%3A%201637465397463%2C%22LASTEVENT%22%3A%20%7B%22eventId%22%3A%20%22da_screen%22%2C%22time%22%3A%201637465397474%7D%2C%22sessionUuid%22%3A%20%22facf15e8-fb22-494b-a16c-b21297eb3692%22%7D; NTES_P_UTID=TXoq5J2oabD9kes1mqBrVZeUMXRGuOoP|1637986478; P_INFO=cyx2012scut@163.com|1637986478|1|mail163|00&99|null&null&null#gud&440400#10#0#0|&0||cyx2012scut@163.com; vjuids=-f65b9742.17d60b7b1b8.0.6a31ebc577479; vjlast=1638005191.1638351613.13; vinfo_n_f_l_n3=1de80eaa726a81af.1.8.1634007293550.1638351815972.1638354063495; _iuqxldmzr_=32; JSESSIONID-WYYY=lcaQnWOJhrr4PqsdNV2o0h23eFDcQDSO%2FYvokw2gtDBOIQhAZPhgM6FkHQ%2BQso9lbF83%2BD%5CPXhI%5CQIWy4Imsdhb1336r69ecbnzi%2F8HoCBou%5Ch%5Cum7GH2t%2FYnXIOKqblFpQduO%5CXej7My07YRrzN47sec5W6J9qE4DhAFao12d%2BB1tjB%3A1644191501987; WM_NI=kedPt41wqq4FpwZfPMoLxHxyIF8nuwmmJrVRAsd4eF0Mn%2FK3VS57FVpTqKNlL2I42Fq%2F4fpsnK2sSsVG2oQ8TW292gdUIjvlnLF9Me%2Fi3Q0MyKUg6tz4%2Fc2b%2F2cdkPK%2Ba0M%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eeb0c47bbc99ac84ee3bf7928ab3d44e969e8ebaf8258d928dafe97ef7bb8bd9ae2af0fea7c3b92aa9bbacb1f740f3a9bf92b74eb4a99687d347ad94b8a9fb738b9af88ff87dafb38693d55a83adacd5e84ef493a2d0ca39968dfbd8c55eb48cbfaccd6890ee87d5b14eb3f1fc87f379ae95fe94d2799699fe90d4349889fedab16da88b878bf568ae948adad06fedb7fdb2b347bb959b88b580baece184b16aedeead85ea5c89f5afd1d037e2a3',
    'dnt': '1',
    'referer': 'https://music.163.com/',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Microsoft Edge";v="98"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'iframe',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.43',
}

mysql_info=dict(
    host='localhost',
    port=3306,
    user='wyy_web',
    password='wyy_web',
    database='wyy_web',
)
db=pymysql.connect(**mysql_info)
cursor=db.cursor()
cursor.execute('''
create table if not exists playlists(
    id varchar(20) primary key,
    name varchar(100) not null,
    createtime varchar(20) not null,
    track_count int not null,
    play_count int not null,
    share_count int not null,
    description varchar(100) not null,
    tags varchar(100),
    track_ids text
);
''')
cursor.execute('''
create table if not exists tracks(
    id varchar(20) primary key,
    name varchar(100) not null,
    artists varchar(100) not null,
    publishTime varchar(20) not null,
    is_original int not null,
    original_id varchar(20) not null,
    original_name varchar(100) not null,
    original_artists varchar(100) not null,
    comment_count int not null
);
'''
)
cursor.execute('''
create table if not exists hot_comments(
    id varchar(20) primary key,
    track_id varchar(20) not null,
    content varchar(255) not null,
    create_time varchar(20) not null,
    likedCount int not null
);
''')
cursor.execute('''
create table if not exists numbers(
    number int primary key
);
''')
for i in range(1,20):
    cursor.execute(f'insert ignore into numbers(number) values({i});')
db.commit()

def playlist_exists(playlist_id):
    cursor.execute('select track_ids from playlists where id=%s', playlist_id)
    track_ids=cursor.fetchone()
    if track_ids is None:
        return False
    else:
        return True


def get_playlist(page=1):
    url=f'https://music.163.com/discover/playlist/?order=hot&cat=%E5%85%A8%E9%83%A8&limit=35&offset={(page-1)*35}'
    res=requests.get(url,headers=headers)
    playlists=re.findall('<a title="(.*?)" href="/playlist\?id=(\d+)"',res.text)
    for title,playlist_id in playlists:
        print(f'[歌单]{title}--正在获取信息')
        playlist_info=apis.playlist.GetPlaylistInfo(playlist_id)
        info=playlist_info['playlist']
        id=info['id']
        exists=playlist_exists(id)
        if exists:
            continue
        name=info['name']
        createtime=info['createTime']
        track_count=info['trackCount']
        play_count=info['playCount']
        share_count=info['shareCount']
        description=info['description']
        tags=','.join(info['tags'])
        track_ids=','.join([str(i['id']) for i in info['trackIds']])
        sql='''
        insert ignore into playlists(id,name,createtime,track_count,play_count,share_count,description,tags,track_ids)
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s)
        '''
        cursor.execute(sql,(id,name,createtime,track_count,play_count,share_count,description,tags,track_ids))
        db.commit()
        print(f'[歌单]{title}--获取信息完成')
        print(f'[歌单]{title}--正在获取歌曲信息')
        for track_id in track_ids.split(','):
            sql=f'''
            insert ignore into tracks(id)
            values('{track_id}')
            '''
            cursor.execute(sql)
            db.commit() 
        print(f'[歌单]{title}--获取歌曲信息完成')
    print(f'[歌单]第{page}页获取完成')


def get_track_info(track_id):
    track_info=apis.track.GetTrackDetail(track_id)['songs'][0]
    track_comments=apis.track.GetTrackComments(track_id)
    id=track_info['id']
    name=track_info['name']
    publishTime=track_info['publishTime']
    artists=','.join([i['name'] for i in track_info['ar']])
    is_original=1 if track_info.get('originSongSimpleData') is None else 0
    original_id,original_name,original_artists='','',''
    comment_count=track_comments['total']
    if is_original==0:
        originSongSimpleData=track_info['originSongSimpleData']
        original_id=originSongSimpleData['songId']
        original_name=originSongSimpleData['name']
        original_artists=','.join([i['name'] for i in originSongSimpleData['artists']])
    
    # artists_id=','.join([str(i['id']) for i in track_info['ar']])
    del_sql='''
    delete from tracks where id=%s
    '''
    lock.acquire()
    cursor.execute(del_sql,id)
    db.commit()
    sql='''
    insert ignore into tracks(id,name,artists,is_original,original_id,original_name,original_artists,comment_count,publishTime)
    values(%s,%s,%s,%s,%s,%s,%s,%s,%s)
    '''
    cursor.execute(sql,(id,name,artists,is_original,original_id,original_name,original_artists,comment_count,publishTime))
    db.commit()
    lock.release()
    for comment in track_comments['hotComments']:
        id=comment['commentId']
        content=comment['content']
        create_time=comment['time']
        likedCount=comment['likedCount']
        sql='''
        insert ignore into hot_comments(id,track_id,content,create_time,likedCount)
        values(%s,%s,%s,%s,%s)
        '''
        lock.acquire()
        cursor.execute(sql,(id,track_id,content,create_time,likedCount))
        db.commit()
        lock.release()
    print(f'歌曲{name}--获取信息完成')

class MyThread(threading.Thread):
    def __init__(self,queue):
        super().__init__()
        self.queue=queue

    def run(self):
        while True:
            if self.queue.empty():
                break
            track_id=self.queue.get()
            get_track_info(track_id)

def main():
    # for i in range(1,100):
    #     get_playlist(i)
    q=queue.Queue()
    cursor.execute('select id from tracks where publishTime is null order by rand()')
    tracks=cursor.fetchall()
    for track in tracks:
        q.put(track[0])
    threads=[]
    for i in range(50):
        t=MyThread(q)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    db.close()


get_track_info(298213)
# if __name__=='__main__':
#     # for i in range(8,100):
#     #     get_playlist(i)
    # main()
#     # print(apis.track.GetTrackDetail(254485))