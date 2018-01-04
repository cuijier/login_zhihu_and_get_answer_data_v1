#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Required
- requests (必须)
- pillow (可选)
Info
- author : "xchaoinfo"
- email  : "xchaoinfo@qq.com"
- date   : "2016.2.4"
Update
- name   : "wangmengcn"
- email  : "eclipse_sv@163.com"
- date   : "2016.4.21"
'''
import requests
import chardet
from requests.auth import HTTPBasicAuth
import json
try:
    import cookielib
except:
    import http.cookiejar as cookielib
import re
import time
import os.path
import  os
import html2text
from bs4 import BeautifulSoup
try:
    from PIL import Image
except:
    pass


# 构造 Request headers
agent = 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
headers = {
    "Host": "www.zhihu.com",
    "Referer": "https://www.zhihu.com/",
    'User-Agent': agent
}
headers2 = {
    "Host": "www.zhihu.com",
    "Referer": "https://www.zhihu.com/question/24871100",
    "authorization":"Bearer 2|1:0|10:1509860850|4:z_c0|92:Mi4xblI3d0FRQUFBQUFBa0VLczM3NmNEQ1lBQUFCZ0FsVk44dlByV2dBUXh6Z3kwcTUtU284dTRpQW1YWW1GajRNSVdB|86aaf837a9ce3c7fe55f980a8e277c813799b11c64a37b1643cef6503a2232c3",
    #"authorization":("18872269901","qw1990070605"),
    'User-Agent': agent
}

# 使用登录cookie信息
session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print("Cookie 未能加载")
'''
def HtmltoMarkdown(string):

    string.replace('<h1>', r'# ')
    string.replace('</h1>', r'')
    string.replace('<h2>', r'## ')
    string.replace('<h3>', r'### ')
    string.replace('<h4>', r'#### ')
    string.replace('<h5>', r'##### ')
    string.replace('<h6>', r'###### ')
    soup = BeautifulSoup(string, 'html.parser')
    soup.a["href"]
'''

def get_xsrf():
    '''_xsrf 是一个动态变化的参数'''
    index_url = 'https://www.zhihu.com/'
    # 获取登录时需要用到的_xsrf
    index_page = session.get(index_url, headers=headers)
    #soup = BeautifulSoup(index_page.text, 'html.parser')
    #soup
    pattern = r'name="_xsrf" value="(.*?)"'
    # 这里的_xsrf 返回的是一个list
    _xsrf = re.findall(pattern, index_page.text)
    return _xsrf[0]

def get_question_answer(question_id):
    is_end = False
    url = 'https://www.zhihu.com/question/'+str(question_id)
    t = "data[*].is_normal,admin_closed_comment,reward_info,is_collapsed," \
        "annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by," \
        "suggest_edit,comment_count,can_comment,content,editable_content,voteup_count," \
        "reshipment_settings,comment_permission,created_time,updated_time,review_info,question," \
        "excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,upvoted_followees;" \
        "data[*].mark_infos[*].url;data[*].author.follower_count,badge[?(type=best_answerer)].topics"
    offset = 0
    data = {
        'sort_by': "default",
        'include': t,
        'limit': 20,
        'offset': offset
    }
    answer = session.get(url, headers=headers)
    soup = BeautifulSoup(answer.text, 'html.parser')
    # 问题title
    title = soup.title.string.split('\n')
    # 问题描述
    description = soup.find('span', {'class': 'RichText'}).string
    get_url = 'https://www.zhihu.com/api/v4/questions/'+str(question_id)+'/answers'
    headers2["Referer"] = "https://www.zhihu.com/question/"+str(question_id)
    answer = requests.get(get_url,headers=headers2,params=data)

    # 问题答案数量
    answer_js = answer.json()
    #print(answer_js)
    title = answer_js['data'][1]['question']['title']
    total_answer = answer_js['paging']['totals']
    f = open('E:/code/Python/project/' + str(title) + '.md', 'w')
    f.write("## "+title+"\n")
    f.write(("---\n"))
    f.write("###### description:%s\n" % description)
    f.write("###### total answer:%d\n" % total_answer)
    f.write(("---\n\n"))
    num = 0
    while False == is_end:
        try:
            next_url_js = answer_js['paging']['next']
            is_end = answer_js['paging']['is_end']
            answer_list = answer_js['data']
            for ans in answer_list:
                try:
                    num = num+1
                    author = ans['author']['name']
                    create_time = time.strftime("%y-%m-%d %H:%M:%S",time.localtime(ans['created_time']))
                    vote_up = ans["voteup_count"]
                    f.write("%d.<br>" % num)
                    print("it\'s spider  %d answer" % num)
                    f.write("**anuther:%s     create time:%s     voteup_count:%d**   \n" % (author,create_time,vote_up))
                    content = html2text.html2text(ans['content'].strip())
                    f.write(content+'---   \n   \n')
                except:
                    continue
            time.sleep(2)
        except:
            pass
        finally:
            answer = requests.get(next_url_js, headers=headers2)
            answer_js = answer.json()
    print("all of answer have been spidered")
    f.close()
    '''
    answer = session.get(url, headers=headers)
    #print(answer.text)
    soup = BeautifulSoup(answer.text, 'html.parser')
    # 问题title
    title = soup.title.string.split('\n')
    # 问题描述
    description = soup.find('span', {'class':'RichText'}).string
    # 问题答案数量
    answer_num = int(soup.find('h4',{'class':'List-headerText'}).string.split(' ')[0])  # 答案数量
    for link in soup.find_all('a',{'target':'_blank'}):
        answer_url = 'https://www.zhihu.com'+link.get('href')
    for answer in soup.find_all('div',{'class':'RichContent-inner'}):
        print(answer.get_text())
    for i in range(1,answer_num/20):
        offset = i * 20
        if(i%2)
    '''



# 获取验证码
def get_captcha():
    t = str(int(time.time() * 1000))
    #print(time, time(), t)
    captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
    r = session.get(captcha_url, headers=headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()
    # 用pillow 的 Image 显示验证码
    # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
    captcha = input("please input the captcha\n>")
    return captcha


def isLogin():
    # 通过查看用户个人信息来判断是否已经登录
    url = "https://www.zhihu.com/settings/profile"
    login_code = session.get(url, headers=headers, allow_redirects=False).status_code
    if login_code == 200:
        return True
    else:
        return False


def login(secret, account):
    _xsrf = get_xsrf()
    headers["X-Xsrftoken"] = _xsrf
    headers["X-Requested-With"] = "XMLHttpRequest"
    # 通过输入的用户名判断是否是手机号
    if re.match(r"^1\d{10}$", account):
        print("手机号登录 \n")
        post_url = 'https://www.zhihu.com/login/phone_num'
        postdata = {
            '_xsrf': _xsrf,
            'password': secret,
            'phone_num': account
        }
    else:
        if "@" in account:
            print("邮箱登录 \n")
        else:
            print("你的账号输入有问题，请重新登录")
            return 0
        post_url = 'https://www.zhihu.com/login/email'
        postdata = {
            '_xsrf': _xsrf,
            'password': secret,
            'email': account
        }
    print(postdata['_xsrf'])
    # 不需要验证码直接登录成功，这个地方有问题，需要调试 #
    login_page = session.post(post_url, data=postdata, headers=headers)
    login_code = login_page.json()
    if login_code['r'] == 1:
        # 不输入验证码登录失败
        # 使用需要输入验证码的方式登录
        postdata["captcha"] = get_captcha()
        login_page = session.post(post_url, data=postdata, headers=headers)
        login_code = login_page.json()
        print(login_code['msg'])
    # 保存 cookies 到文件，
    # 下次可以使用 cookie 直接登录，不需要输入账号和密码
    session.cookies.save()

try:
    input = input
except:
    pass


if __name__ == '__main__':
    if isLogin():
        print('您已经登录')
    else:
        account = input('请输入你的用户名\n>  ')
        secret = input("请输入你的密码\n>  ")
        login(secret, account)
    question_id = input("请输入问题ID\n>  ")
    get_question_answer(question_id)
