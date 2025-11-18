import math,time
import requests,re
from get_danmu.utils import dm_pb2
from google.protobuf import text_format

my_seg = dm_pb2.DmSegMobileReply()
# video_id='BV13oWgztEaC'
# start_time='0.0'
# end_time='9.20'
# add_num=360000

# segment_index=1
id_pattern = re.compile(r'^id:\s+(\d+)$', re.MULTILINE)
progress_pattern = re.compile(r'^progress:\s+(\d+)$', re.MULTILINE)
content_pattern = re.compile(r'^content:\s+"([^"]+)"$', re.MULTILINE)
color_pattern = re.compile(r'^color:\s+(\d+)$', re.MULTILINE)
mode_pattern = re.compile(r'^mode:\s+(\d+)$', re.MULTILINE)

 




class BilibiliFetcher():
    """爱奇艺弹幕抓取器"""
    MAX_DURATION = 7200  # 2小时，单位: 秒


    def __init__(self, url:str,proxy:str,cookie:str=''):
        super().__init__()
        self.url = url
        self.proxy=proxy
        self.proxies = {
"http": self.proxy,
"https": self.proxy,
} if proxy else None
        self.headers={
            'user-agent':'''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'''
            ,'cookie':''
            }
        self.headers['cookie']=cookie

    def get_video_info(self):
        """
        获取视频的 cid (弹幕 ID)
        """
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(self.url, headers=self.headers,proxies=self.proxies)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch video page: {response.status_code}")
        html = response.text

        # 提取 cid
        cid_match = re.search(r'"cid":(\d+),', html)
        cid = cid_match.group(1) if cid_match else None

        # 提取标题
        title_match = re.search(r'<meta itemProp="name" content="([^"]+)"', html)
        title = title_match.group(1) if title_match else ""

        time_length=re.search(r'"timelength":(\d+)', html)
        time_length = int(time_length.group(1)) if time_length else 0
        
        video_data = {"cid": cid, "title": title,'time_length':time_length}
        return video_data
    


# oid='1110706533'

# url = 'https://api.bilibili.com/x/v2/dm/wbi/web/seg.so'
# ?type=1&oid=1110706533&pid=560622601&segment_index=1

    def run(self,start_second:int=None,end_second:int=None,progress_callback:object=None):
        video_data = self.get_video_info()
        cid=video_data.get('cid')
        title=video_data.get('title')
        time_length=video_data.get('time_length')

        segment_index=math.ceil(time_length/360000)
        current_segment_index=1

        if start_second:
            current_segment_index=start_second//360+1
        if end_second:
            segment_index=math.ceil(end_second/360)
        # print(segment_index,time_length)
        id=0
        data_upload=[]

        while True:
            params = {
                'type':1,         #弹幕类型
                'oid':cid,    #cid
                'segment_index':current_segment_index #弹幕分段
            }
            
            resp = requests.get('https://api.bilibili.com/x/v2/dm/wbi/web/seg.so',params,headers=self.headers,proxies=self.proxies)
            
            if resp.status_code!=200:
                break
            data = resp.content
            my_seg.ParseFromString(data)
            
            

            for i in my_seg.elems:
                id+=1
                parse_data = text_format.MessageToString(i, as_utf8=True)
                # id_match = id_pattern.search(parse_data)
                progress_match = progress_pattern.search(parse_data)
                content_match = content_pattern.search(parse_data)
                color_match = color_pattern.search(parse_data)
                mode_match = mode_pattern.search(parse_data)
                if not progress_match:
                    continue
                if not content_match:
                    continue
                data_upload.append({
                        "time_offset": int(progress_match.group(1)),
                        "mode": mode_match.group(1),
                        "font_size": 25,
                        "color": color_match.group(1),
                        "timestamp": int(time.time()),
                        "content": content_match.group(1)
                    })

            # print(parse_data)
            if progress_callback:
                progress_callback(current_segment_index,segment_index)
            # print(current_segment_index)

            current_segment_index+=1
            if current_segment_index>segment_index:
                break
            
        return data_upload,time_length,title


# def bili(url,set_cookie=''):
#     if set_cookie!='':
#         headers['cookie']=set_cookie
#     data_upload,time_length,file_name=run(url)
#     if file_name=='':
#         file_name=input('输入需要存储的文件名:')
#         episodeTitle=file_name
#         number=None
#     else:
#         match=re.search(r'第(\d+)话|第(\d+)集',file_name)
#         file_name=file_name.replace('&amp;nbsp;',' ')
#         try:
#             number = match.group(1) if match.group(1) else match.group(2)
#             episodeTitle=f'第{number}集'
#         except:number=None
#         if match:file_name=file_name.split(match.group(0))[0]
#         else:
#             file_name=input('输入需要存储的文件名:')
#             number=None
#             episodeTitle=file_name

    # animeTitle=file_name
    # if not number:
    #     file_name=animeTitle
    # else:
    #     file_name=animeTitle+f' S1E{number}'
    
    # df = pd.DataFrame(data_upload)
    # del data_upload
    # df.to_csv(f'./danmu_data/{file_name}.csv', encoding='utf-8-sig', index=False)
    # return animeTitle,number,f'{time_length/1000/60:.2f}',file_name,episodeTitle
            

   


# if __name__ == "__main__":
#     video_url = input("请输入 B 站视频链接: ")
#     cookie=input('输入Cookie以便获取更多的弹幕:')
#     headers['cookie']=cookie
#     animeTitle,number,duration_minutes,file_name,episodeTitle=bili(url=video_url)

#     from sqlite_orm import SQLiteORM
#     db_orm = SQLiteORM(db_name='anime_files')
#     episodeId=int(db_orm.get_lang_id())+1

#     db_orm.add_episode(animeTitle=animeTitle,fileName=file_name
#                        ,animeId=episodeId,episodeId=episodeId,episodeTitle=episodeTitle,file=f"./danmu_data/{file_name}.csv"
#                        ,imageUrl='',api='BiliBili',api_info={"id":video_url,"start_time":"0.0",'end_time':duration_minutes})
