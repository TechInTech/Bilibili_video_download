# !/user/bin/env python
# -*- coding:utf-8 -*- 
# time: 2018/10/23--20:12
__author__ = 'Henry'

'''
项目: B站视频下载
'''

import requests,time,hashlib,urllib.request,re
from xml.dom.minidom import parseString
from moviepy.editor import *
import os, sys, json

#用户输入av号或者视频链接地址
print('*'*30 + 'B站视频下载小助手' + '*'*30)
start = input('请输入您要下载的B站av号或者视频链接地址:')
if start.isdigit() == True: #如果输入的是av号
    start_url = 'https://www.bilibili.com/video/av' + start
else:
    start_url = start

#视频质量
# <accept_format><![CDATA[flv,flv720,flv480,flv360]]></accept_format>
# <accept_description><![CDATA[高清 1080P,高清 720P,清晰 480P,流畅 360P]]></accept_description>
# <accept_quality><![CDATA[80,64,32,15]]></accept_quality>
quality = input('请输入您要下载视频的清晰度(1080p:80;720p:64;480p:32;360p:15)(填写80或64或32或15):')

#获取视频的cid,title
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
}
html = requests.get(start_url,headers=headers).text
cid = re.search(r'cid=(\d+)&',html).group(1)
title = re.search(r'<h1 title="(.*?)" class="video-title"',html).group(1)
print('[下载视频的cid]:' +cid)
print('[下载视频的标题]:' + title)
# 清洗一下标题名称(不能有\ / : * ? " < > |)
title = re.sub(r'[\/\\:*?"<>|]', '', title)  # 替换为空的

#访问API地址
entropy = 'rbMCKn@KuamXWlPMoJGsKcbiJKUfkPF_8dABscJntvqhRSETg'
appkey, sec = ''.join([chr(ord(i) + 2) for i in entropy[::-1]]).split(':')
params = 'appkey=%s&cid=%s&otype=json&qn=%s&quality=%s&type=' % (appkey, cid, quality, quality)
chksum = hashlib.md5(bytes(params + sec, 'utf8')).hexdigest()
url_api = 'https://interface.bilibili.com/v2/playurl?%s&sign=%s' % (params, chksum)
headers = {
    'Referer':start_url,  #注意加上referer
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
}
# print(url_api)
html = requests.get(url_api,headers=headers).json()
# print(json.dumps(html))
video_list = [html['durl'][0]['url']]
# print(video_list)

#下载视频
'''
 urllib.urlretrieve 的回调函数：
def callbackfunc(blocknum, blocksize, totalsize):
    @blocknum:  已经下载的数据块
    @blocksize: 数据块的大小
    @totalsize: 远程文件的大小
'''


def Schedule_cmd(blocknum, blocksize, totalsize):
    speed = (blocknum * blocksize) / (time.time() - start_time)
    # speed_str = " Speed: %.2f" % speed
    speed_str = " Speed: %s" % format_size(speed)
    recv_size = blocknum * blocksize

    # 设置下载进度条
    f = sys.stdout
    pervent = recv_size / totalsize
    percent_str = "%.2f%%" % (pervent * 100)
    n = round(pervent * 50)
    s = ('#' * n).ljust(50, '-')
    f.write(percent_str.ljust(8, ' ') + '[' + s + ']' + speed_str)
    f.flush()
    # time.sleep(0.1)
    f.write('\r')


def Schedule(blocknum, blocksize, totalsize):
    speed = (blocknum * blocksize) / (time.time() - start_time)
    # speed_str = " Speed: %.2f" % speed
    speed_str = " Speed: %s" % format_size(speed)
    recv_size = blocknum * blocksize

    # 设置下载进度条
    f = sys.stdout
    pervent = recv_size / totalsize
    percent_str = "%.2f%%" % (pervent * 100)
    n = round(pervent * 50)
    s = ('#' * n).ljust(50, '-')
    print(percent_str.ljust(6, ' ') + '-'+ speed_str)
    f.flush()
    time.sleep(2)
    # print('\r')

# 字节bytes转化K\M\G
def format_size(bytes):
    try:
        bytes = float(bytes)
        kb = bytes / 1024
    except:
        print("传入的字节格式不对")
        return "Error"
    if kb >= 1024:
        M = kb / 1024
        if M >= 1024:
            G = M / 1024
            return "%.3fG" % (G)
        else:
            return "%.3fM" % (M)
    else:
        return "%.3fK" % (kb)

print('[正在下载,请稍等...]:' + title)
num = 1
for i in video_list:
    opener = urllib.request.build_opener()
    # 请求头
    opener.addheaders = [
        # ('Host', 'upos-hz-mirrorks3.acgvideo.com'),  #注意修改host,不用也行
        ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0'),
        ('Accept', '*/*'),
        ('Accept-Language', 'en-US,en;q=0.5'),
        ('Accept-Encoding', 'gzip, deflate, br'),
        ('Range', 'bytes=0-'),  # Range 的值要为 bytes=0- 才能下载完整视频
        ('Referer', start_url),  #注意修改referer,必须要加的!
        ('Origin', 'https://www.bilibili.com'),
        ('Connection', 'keep-alive'),
    ]
    urllib.request.install_opener(opener)
    #创建文件夹存放下载的视频
    if not os.path.exists(r'F:\bilibili_video\{}'.format(title)):
        os.makedirs(r'F:\bilibili_video\{}'.format(title))
    #开始下载
    start_time = time.time()
    urllib.request.urlretrieve(url=i,filename=r'F:\bilibili_video\{}\{}-{}.flv'.format(title,title,num), reporthook=Schedule_cmd)  #写成mp4也行  title + '-' + num + '.flv'
    num +=1

#合并视频
if len(video_list) >= 2:
    #视频大于一段才要合并
    print('[下载完成,正在合并视频]')
    # 定义一个数组
    L = []
    # 访问 video 文件夹 (假设视频都放在这里面)
    for root, dirs, files in os.walk(r'F:\bilibili_video\{}'.format(title)):
        # 遍历所有文件
        for file in sorted(files, key=lambda x: int(x[x.rindex("-")+1:x.rindex(".")])):
            # 如果后缀名为 .mp4/.flv
            if os.path.splitext(file)[1] == '.flv':
                # 拼接成完整路径
                filePath = os.path.join(root, file)
                # 载入视频
                video = VideoFileClip(filePath)
                # 添加到数组
                L.append(video)
    # 拼接视频
    final_clip = concatenate_videoclips(L)
    # 生成目标视频文件
    final_clip.to_videofile(r'F:\bilibili_video\{}\{}.mp4'.format(title,title), fps=24, remove_temp=False)
    print('[视频合并完成]')

else:
    #视频只有一段则直接打印下载完成
    print('[下载完成]:' + title)

#拓展:分P视频:url相同,只是cid不同,通过url?p=1,2..分别找出每个分P的cid,带入请求得到下载地址
