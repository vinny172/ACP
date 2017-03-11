# -*- coding:utf-8 -*-
"""
專案：專輯封面自動抓圖程式
用途：音樂資料庫由資料夾來分不同專輯，資料夾名含歌手名和專輯名，透過資料夾名的資訊去網
　　　路上蒐集其專輯的封面，並存至該資料夾歸檔。
備註：
音樂庫每個專輯資料夾名格式為「歌手.-.[專輯名].專輯.(APE)」，抓到封面圖後丟進該資料夾並
統一命名為Cover.jpg。(再以foobar作為音樂庫管理工具)
版本：0.9
開發環境：Python 2.7
開發人：Colin Lin
時間：2017/03/12
"""
import os
import requests
import urllib2
import urllib
from bs4 import BeautifulSoup
import json
import lxml

dofolder = u"E:\音樂\"  #執行目錄
PIC_NAME = 'Cover'
HTML_PARSER = "html.parser"
ROOT_URL = 'http://www.kkbox.com/' #設定目標網站
SEARCH_URL = 'http://www.kkbox.com/tw/tc/search.php?search=artist&word='


###############網路爬取封面圖###################
## 1)進KKBOX官網搜尋歌手 找到正確結果進入歌手專頁
def get_artist_page(performer, album_name):
      
    content = requests.get(SEARCH_URL + performer)
    
    soup = BeautifulSoup(content.content, HTML_PARSER)
    artist_tag = soup.find_all('a', attrs={'class':'cover'})   #尋找條件：標籤<a>並且含屬性class:cover


    #歌手搜尋結果頁面所有符合尋找條件的連結
    artist_links = [] 
    for artists in artist_tag:
        artist_link = ROOT_URL + artists['href']
        #print(artist_link)   #印出歌手頁面連結
        artist_links.append(artist_link)

    
    #選出最相符的歌手名稱 (待開發)
        
    return get_album_page(artist_links[0], album_name)   #選擇其中一個去進一步找專輯


        
## 2)抓出歌手ID作為索引 爬出專輯做搜尋並下載
def get_album_page(artist_link, album_name):

    artist_link=artist_link.rstrip('-index-1.html')
    artist_link=artist_link.lstrip('https://www.kkbox.com/tw/tc/artist/')
    ArtistID = artist_link 
    page = 1

    while True:
        content = urllib2.urlopen('http://www.kkbox.com/tw/tc/ajax/get_artist_extend_data.php?type=album&artist_id=' + ArtistID + '&page=' + str(page) + '&is_mobile=0')
        data = json.loads(content.read())
        
        if len(data) > 0:
            for i in data:
                if album_name in i['album_name']:
                    #print i['album_photo']
                    return i['album_photo']
        else:
            break
        page = page + 1


## 3)抓圖
def download_pic(cover_path, file_name):
    r = requests.get(cover_path)
    with open(file_name,'wb') as f:
        f.write(r.content)

## 4)資料夾名稱過濾
def album_name_filter(album_name):
    album_name = album_name.replace('[','')
    album_name = album_name.replace(']','')
    album_name = album_name.replace('.','')
    album_name = album_name.replace(u'專輯','')
    album_name = album_name.replace('(APE)','')
    album_name = album_name.replace('(MP3)','')
    album_name = album_name.replace('(FLAC)','')
    album_name = album_name.replace('(WAV)','')
    album_name = album_name.replace('(ape)','')
    album_name = album_name.replace('(mp3)','')
    album_name = album_name.replace('(flac)','')
    album_name = album_name.replace('(wav)','')
    return album_name


############主程式################
if __name__ == '__main__':
    
    for root, dirs, files in os.walk(dofolder):
        #print root
        for name in files:
            if os.path.splitext(name)[-1]  == ".ape" or ".flac" or ".wav" or ".mp3": #只要資料夾內有特定副檔名之檔案(音樂檔)
                #print os.path.basename(root)   #測試用：擷取資料夾名
                album_info = os.path.basename(root).split('.-.')
                try:
                    #album_info[1] = album_info[1].upper()
                    album_info[1] = album_name_filter(album_info[1])
                    album_info[0] = album_info[0].replace('.',' ')
                    print '---擷取中---'
                    print album_info[0] + "-" + album_info[1]  #測試用：擷取專輯資訊

                    try:
                        cover_link = get_artist_page(album_info[0],album_info[1]).replace('300x300.jpg','500x500.jpg')   #呼叫網路爬蟲抓圖
                        print cover_link
                        download_pic(cover_link,'Covers\\' + album_info[0] + "-" + album_info[1] +'.jpg')  #下載封面
                        download_pic(cover_link,root + '\\' + PIC_NAME + '.jpg')  #下載封面
                        print '---擷取成功---'
                        print root + '\\' + PIC_NAME + '.jpg'
                        print '--------------'
                    except:
                        print '---擷取失敗---'

           
                except:
                    continue
                break
                

#####################GUI########################

