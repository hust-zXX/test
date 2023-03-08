import os

import openai
from flask import Flask, redirect, render_template, request, make_response,url_for
from flask_limiter import Limiter
import requests,tenacity
import base64

# os.environ["http_proxy"] = "http://127.0.0.1:10809"
# os.environ["https_proxy"] = "https://127.0.0.1:10809"

app = Flask(__name__)
limiter = Limiter(
    app,
    #key_func=get_remote_address,  # 根据访问者的IP记录访问次数
    default_limits=["200000 per day", "30000 per hour"]  # 默认限制，一天最多访问200次，一小时最多访问50次
)

rd = os.urandom(66)
app.secret_key = base64.b64encode(rd)

# app.secret_key = 'u2jksidjflsduwerjl'
app.debug = True

openai.api_key = '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'#os.getenv("OPENAI_API_KEY")
openai.api_key = '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'

prompt ='Introduce the application scenarios of the intelligent manufacturing system of industrial Internet and AI technology'
prompt ='Introduce the application scenarios of cloud-edge collaborative computing in discrete manufacturing'
#response = openai.Completion.create(model="text-davinci-003",prompt=prompt,temperature=0.2,max_tokens=200,)
#x =url_for("index", result=response.choices[0].text)

#print(response.choices[0].text)


class EasyTranslation:
    def __init__(self,url = 'http://luckwax.com:3080/t'):
        self.url = url
        self.http = requests.Session()
        http_retry_wrapper = tenacity.retry(wait=tenacity.wait_fixed(1), stop=tenacity.stop_after_attempt(10),
                                            retry=tenacity.retry_if_exception_type(requests.RequestException),reraise=True)
        self.http.get = http_retry_wrapper(self.http.get)
        self.http.post = http_retry_wrapper(self.http.post)

    def translate(self,msg,src='auto',dest = 'en'):
        post_data = {'msg': msg, 'src': src,'dest': dest}
        resp = self.http.post(self.url , json=post_data)
        resp = resp.json()['msg']

        return resp

g_easyTranslation =EasyTranslation(url = 'http://luckwax.com:3080/t')

import random

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        text = request.form["text"]
        number = request.form["number"]
        prompt = g_easyTranslation.translate(text,src='zh-CN',dest='en')
        print('中-英翻译完成:',prompt)

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.2,
            max_tokens=int(number))

        print('gpt-chat 执行完成:',response.choices[0].text)
        resp = g_easyTranslation.translate(response.choices[0].text,src='en',dest='zh-CN')
        print('英-中翻译完成:', resp)

        resp=resp.strip('\n')
        resp=resp.strip('\r')
        return  make_response(resp,200)

        return redirect(url_for("index", result=resp))

    result = request.args.get("result")
    return render_template("index.html", result=result)


def generate_prompt(animal):
    return """Suggest three names for an animal that is a superhero.

Animal: Cat
Names: Captain Sharpclaw, Agent Fluffball, The Incredible Feline
Animal: Dog
Names: Ruff the Protector, Wonder Canine, Sir Barks-a-Lot
Animal: {}
Names:""".format(
        animal.capitalize()
    )

if __name__ == '__main__':
    import sys
    print(sys.argv)
    app.run(host='0.0.0.0', port=8080)