import sys
import json
import base64
import time
import http.client
import hashlib
import urllib
import random
import pyttsx3

def voice2text(dir):
	IS_PY3 = sys.version_info.major == 3

	if IS_PY3:
	    from urllib.request import urlopen
	    from urllib.request import Request
	    from urllib.error import URLError
	    from urllib.parse import urlencode
	    timer = time.perf_counter
	else:
	    from urllib2 import urlopen
	    from urllib2 import Request
	    from urllib2 import URLError
	    from urllib import urlencode
	    if sys.platform == "win32":
	        timer = time.clock
	    else:
	        # On most other platforms the best timer is time.time()
	        timer = time.time

	API_KEY = 'KSf9iZwHQEbSamq44p4jLz2v'
	SECRET_KEY = 'i2ZqGmDBZ0jhZEHBt3n07KyWbPVp3dkO'

	# 需要识别的文件
	AUDIO_FILE = dir  # 只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式
	# 文件格式
	FORMAT = AUDIO_FILE[-3:]  # 文件后缀只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式

	CUID = '123456PYTHON'
	# 采样率
	RATE = 16000  # 固定值

	# 普通版

	DEV_PID = 1737  # 1537 表示识别普通话，使用输入法模型。根据文档填写PID，选择语言及识别模型
	ASR_URL = 'http://vop.baidu.com/server_api'
	SCOPE = 'audio_voice_assistant_get'  # 有此scope表示有asr能力，没有请在网页里勾选，非常旧的应用可能没有

	class DemoError(Exception):
	    pass


	TOKEN_URL = 'http://openapi.baidu.com/oauth/2.0/token'



	def fetch_token():
	    params = {'grant_type': 'client_credentials',
	              'client_id': API_KEY,
	              'client_secret': SECRET_KEY}
	    post_data = urlencode(params)
	    if (IS_PY3):
	        post_data = post_data.encode('utf-8')
	    req = Request(TOKEN_URL, post_data)
	    try:
	        f = urlopen(req)
	        result_str = f.read()
	    except URLError as err:
	        print('token http response http code : ' + str(err.code))
	        result_str = err.read()
	    if (IS_PY3):
	        result_str =  result_str.decode()

	    #print(result_str)
	    result = json.loads(result_str)
	    #print(result)
	    if ('access_token' in result.keys() and 'scope' in result.keys()):
	        #print(SCOPE)
	        if SCOPE and (not SCOPE in result['scope'].split(' ')):  # SCOPE = False 忽略检查
	            raise DemoError('scope is not correct')
	        #print('SUCCESS WITH TOKEN: %s  EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
	        return result['access_token']
	    else:
	        raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')
	token = fetch_token()

	speech_data = []
	with open(AUDIO_FILE, 'rb') as speech_file:
	    speech_data = speech_file.read()

	length = len(speech_data)
	if length == 0:
	    raise DemoError('file %s length read 0 bytes' % AUDIO_FILE)
	speech = base64.b64encode(speech_data)
	if (IS_PY3):
	    speech = str(speech, 'utf-8')
	params = {'dev_pid': DEV_PID,
	         #"lm_id" : LM_ID,    #测试自训练平台开启此项
	          'format': FORMAT,
	          'rate': RATE,
	          'token': token,
	          'cuid': CUID,
	          'channel': 1,
	          'speech': speech,
	          'len': length
	          }
	post_data = json.dumps(params, sort_keys=False)
	# print post_data
	req = Request(ASR_URL, post_data.encode('utf-8'))
	req.add_header('Content-Type', 'application/json')
	try:
	    begin = timer()
	    f = urlopen(req)
	    result_str = f.read()
	    #print ("Request time cost %f" % (timer() - begin))
	except URLError as err:
	    #print('asr http response http code : ' + str(err.code))
	    result_str = err.read()

	if (IS_PY3):
	    result_str = str(result_str, 'utf-8')
	#print(result_str)
	j = json.loads(result_str)
	text = j['result'][0]
	print(text)
	return text

def translate(text):
	appid = '20200301000390861'
	secretKey = 'n5oINuuzlcEX0BmybesN'  # 填写你的密钥

	httpClient = None
	myurl = '/api/trans/vip/translate'

	fromLang = 'auto'   #原文语种
	toLang = 'zh'   #译文语种
	salt = random.randint(32768, 65536)
	q = text
	sign = appid + q + str(salt) + secretKey
	sign = hashlib.md5(sign.encode()).hexdigest()
	myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
	salt) + '&sign=' + sign

	try:
	    httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
	    httpClient.request('GET', myurl)

	    # response是HTTPResponse对象
	    response = httpClient.getresponse()
	    result_all = response.read().decode("utf-8")
	    result = json.loads(result_all)

	    res = result['trans_result'][0]['dst']
	    print(res)
	    return res

	except Exception as e:
	    print (e)
	finally:
	    if httpClient:
	        httpClient.close()

def read(text):
	engine = pyttsx3.init()
	engine.setProperty('voice', 'com.apple.speech.synthesis.voice.ting-ting')
	engine.say(text)
	engine.runAndWait()


def main():
	dir = '/Users/bondsam/Desktop/test.wav'
	text = voice2text(dir)
	translated_res = translate(text)
	read(translated_res)

if __name__ == '__main__':
	main()




