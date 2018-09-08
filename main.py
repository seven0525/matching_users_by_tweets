#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!//usr/bin/env/python

# -*- coding:utf-8 -*-
import sys, json, time, calendar, re
import urllib
from os.path import join, dirname
from twitter import Twitter, OAuth
from watson_developer_cloud import PersonalityInsightsV3
from requests_oauthlib import OAuth1Session
from datetime import datetime
import config

# Twitter API
CK = config.get_consumer_key()
CS = config.get_consumer_secret()
AT = config.get_access_token()
AS = config.get_access_secret()
twitter = Twitter(auth=OAuth(AT, AS, CK, CS))
url = "https://api.twitter.com/1.1/statuses/user_timeline.json"

# Watson Personality Insights API 
UN = config.get_username()
PS = config.get_password()
personality_insights = PersonalityInsightsV3(version='2017-10-13', username=UN, password=PS)


def get_user_tweets(screen_name):
    number_of_tweets = 0
    count = 200
    max_id = ''
    tweets = []
    a_timeline = twitter.statuses.user_timeline(screen_name=screen_name, count=count, include_rts='false')
    # 取得件数を設定
    while number_of_tweets <= 500:
        for tweet in a_timeline:
            number_of_tweets += 1
            tweets.append(tweet['text'])
            max_id = tweet['id']
        # 取得件数より指定ユーザーのツイートが少ない場合の処理
        if tweets[-1] == tweets[-2]:
            del tweets[-1]
            break
        a_timeline = twitter.statuses.user_timeline(screen_name=screen_name, count=count, max_id=max_id, include_rts='false')
    return tweets

# 余計な文字を省く & 実体参照を文字に戻す
def get_shaped_tweets(tweets_list):
    shaped_tweets = []
    rm_replie = re.compile(r"@([A-Za-z0-9_]+)")
    rm_url = re.compile(r"https?://t.co/([A-Za-z0-9_]+)")
    rm_hashtag = re.compile(r"#(\w+)")
    for tweet in tweets_list:
        shape = rm_replie.sub('', tweet)
        shape = rm_url.sub('', shape)
        shape = rm_hashtag.sub('', shape)
        shape = shape.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&").replace("\n", " ")
        shaped_tweets.append(shape)
    return shaped_tweets

# def 
    
user_id = str(input("あなたのTwitter IDは？: "))
#target_id = str(input("どのTwitter IDとの相性を診断しますか？: "))

shaped_user_tweets = get_shaped_tweets(get_user_tweets(user_id))
#shaped_target_tweets = get_shaped_tweets(get_user_tweets(target_id))

print(shaped_user_tweets)
print('取得ツイート数: ', len(shaped_user_tweets))


