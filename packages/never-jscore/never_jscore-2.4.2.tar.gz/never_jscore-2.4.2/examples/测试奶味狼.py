import json
import re
import subprocess
import time

from lxml import etree
from never_primp import Client
import never_jscore


ctx = never_jscore.Context(enable_logging=False)  # Disable logging to avoid massive timer output
with open('备份.js',encoding='utf-8')as f:
    data = f.read()

ctx.compile(data)




def dict_to_cookie(cookie_dict):
    return '; '.join([f"{k}={v}" for k, v in cookie_dict.items()])


def tr_test():
    session = Client(impersonate='chrome_140', impersonate_os='windows', split_cookies=True)
    session.proxies = "http://127.0.0.1:7890"
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7,zh-HK;q=0.6",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "origin": "https://booking.jal.co.jp",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://booking.jal.co.jp",
        "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    }
    url = "https://www.jal.co.jp"
    response = session.get(url, headers=headers)
    tree = etree.HTML(response.text)
    currentScriptSrc = tree.xpath('//script/@src')[-1]

    key = re.findall('v=(.*)', currentScriptSrc)[0]
    sbsd_url = f'https://www.jal.co.jp{currentScriptSrc}'
    xhr_src = f"https://www.jal.co.jp{currentScriptSrc.replace(f'v={key}', f'')}"
    response = session.get(sbsd_url, headers=headers)
    cookies = session.cookies
    bm_so = cookies.get('bm_so')
    bm_lso = bm_so + '^' + str(int(time.time() * 1000))
    cookies.update({'bm_lso': bm_lso})
    cookies = dict_to_cookie(cookies)

    t = time.time()

    stdout = ctx.call('get_sbsd_body', [cookies,response.text])

    print(f'耗时：{time.time() - t}s')
    body = json.loads(stdout.replace('Error:', '').strip())
    # process = subprocess.Popen(
    #     ["node", 'test_js.js'],  # 调用 Node.js 脚本
    #     stdin=subprocess.PIPE,  # 允许 Python 传递数据
    #     stdout=subprocess.PIPE,  # 允许 Python 获取返回值
    #     stderr=subprocess.PIPE,
    #     text=True,
    #     encoding='utf-8'
    # )

    # 发送 JSON 数据给 Node.js，并关闭输入流


    # stdout, stderr = process.communicate(
    #     cookies + 'fuckfuckfuck' + response.text + 'fuckfuckfuck' + currentScriptSrc+ 'fuckfuckfuck' + url)
    # body = json.loads(stdout.replace('Error:', '').strip())
    print(body)
    json_data = body
    response = session.post(xhr_src, headers=headers, json=json_data)
    print(response.text)
    print(response.cookies)


if __name__ == '__main__':
    tr_test()