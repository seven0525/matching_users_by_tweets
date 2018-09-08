
# coding: utf-8

# In[ ]:


#!//usr/bin/env/python

# -*- coding:utf-8 -*-
import sys, json, time, calendar, re
import urllib
from twitter import Twitter, OAuth
from janome.tokenizer import Tokenizer
from requests_oauthlib import OAuth1Session
from collections import Counter, defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
import config

# ツイートを取得する
CK = config.get_consumer_key()
CS = config.get_consumer_secret()
AT = config.get_access_token()
AS = config.get_access_secret()
t = Twitter(auth=OAuth(AT, AS, CK, CS))

#twitter = OAuth1Session(CK, CS, AT, AS)
url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
user_tweets = []
shaped_user_tweets = []

def get_user_tweets(screen_name):
    number_of_tweets = 0
    count = 200
    max_id = ''
    a_timeline = t.statuses.user_timeline(screen_name=screen_name, count=count, include_rts='false')
    # 取得件数を設定
    while number_of_tweets <= 500:
        for tweet in a_timeline:
            number_of_tweets += 1
            user_tweets.append(tweet['text'])
            max_id = tweet['id']
        # 取得件数より指定ユーザーのツイートが少ない場合の処理
        if user_tweets[-1] == user_tweets[-2]:
            del user_tweets[-1]
            break
        a_timeline = t.statuses.user_timeline(screen_name=screen_name, count=count, max_id=max_id, include_rts='false')

# 余計な文字を省く & 実体参照を文字に戻す
def shape_tweets(tweets_list):
    rm_replie = re.compile(r"@([A-Za-z0-9_]+)")
    rm_url = re.compile(r"https?://t.co/([A-Za-z0-9_]+)")
    rm_hashtag = re.compile(r"#(\w+)")
    for tweet in tweets_list:
        shape = rm_replie.sub('', tweet)
        shape = rm_url.sub('', shape)
        shape = rm_hashtag.sub('', shape)
        shape = shape.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&").replace("\n", " ")
        shaped_user_tweets.append(shape)
    
target_user_id = str(input("どのアカウントIDのTLを取得しますか？: "))
get_user_tweets(target_user_id)
shape_tweets(user_tweets)
print(shaped_user_tweets)
print('取得ツイート数: ', len(shaped_user_tweets))

