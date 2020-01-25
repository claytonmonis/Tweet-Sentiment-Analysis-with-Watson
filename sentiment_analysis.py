import json
import urllib.request
import requests
from requests.auth import HTTPBasicAuth
from TwitterAPI import TwitterAPI
from textblob import TextBlob
import sys

# Dict to handle non-BMP characters
nonBmpMap = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

# Twitter authentication variables
consumerKey = ''
consumerSecret = ''
accessKey = ''
accessSecret = ''

# Watson authentication variables
wUN = ''
wPW = ''
wHD = {'Content-Type': 'application/json'}

# Aggregate analysis of a tweet stream on selected topic
topic = ""
pos, neu, neg, cnt = [0 for x in range(4)]

twapi = TwitterAPI(consumerKey, consumerSecret, accessKey, accessSecret)
stream = twapi.request('statuses/filter', {'track':topic})
for tweet in stream.get_iterator():
    if 'extended_tweet' in tweet: wTX = tweet['extended_tweet']['full_text'].encode('latin-1', 'ignore').decode('latin-1')
    elif 'text' in tweet: wTX = tweet['text'].encode('latin-1', 'ignore').decode('latin-1')
    else: continue

    wDT = '{"text": "' + wTX + '", "features": {"sentiment": {}}}'
    rqst = requests.post('https://gateway.watsonplatform.net/natural-language-understanding/api/v1/analyze?version=2017-02-27', auth=(wUN, wPW), headers = wHD, data = wDT)
    rspn = json.loads(rqst.text)
    if 'sentiment' in rspn:
        score = rspn['sentiment']['document']['score']
        
        if score > 0.15: pos += 1
        elif score < -0.15: neg += 1
        else: neu += 1

        cnt += 1
        print(wTX, score, sep=': ')
        if cnt == 10: break
    else: print(rspn)
  
print("Positive: " + str(pos) + ", " + str(100*pos/cnt) + "%")
print("Negative: " + str(neg) + ", " + str(100*neg/cnt) + "%")
print("Neutral: " + str(neu) + ", " + str(100*neu/cnt) + "%")
