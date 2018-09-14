#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# !//usr/bin/env/python

# -*- coding:utf-8 -*-
import sys, json, time, calendar, re
import urllib
import collections as cl
import codecs
from os.path import join, dirname, abspath, exists
from datetime import datetime
from twitter import Twitter, OAuth
from watson_developer_cloud import PersonalityInsightsV3
from requests_oauthlib import OAuth1Session
import config


# In[ ]:


# Twitter API 初期設定
CK = config.get_consumer_key()
CS = config.get_consumer_secret()
AT = config.get_access_token()
AS = config.get_access_secret()
twitter = Twitter(auth=OAuth(AT, AS, CK, CS))

# Watson Personality Insights API 初期設定
UN = config.get_username()
PS = config.get_password()
personality_insights = PersonalityInsightsV3(version='2017-10-13', username=UN, password=PS)


def get_user_tweets(screen_name):
    number_of_tweets = 0
    count = 200
    max_id = ''
    tweets = []
    a_timeline = twitter.statuses.user_timeline(screen_name=screen_name, count=count, include_rts='false', tweet_mode='extended')
    # 取得件数500
    while number_of_tweets <= 500:
        for tweet in a_timeline:
            number_of_tweets += 1
            tweets.append(tweet['full_text'])
            max_id = tweet['id']
        # 取得件数より指定ユーザーのツイートが少ない場合
        if tweets[-1] == tweets[-2]:
            del tweets[-1]
            break
        a_timeline = twitter.statuses.user_timeline(screen_name=screen_name, count=count, max_id=max_id, include_rts='false', tweet_mode='extended')
    return tweets

# 余計な文字を省く・実体参照を文字に戻す
def get_shaped_tweets(tweets_list):
    shaped_tweets = []
    rm_replie = re.compile(r'@([A-Za-z0-9_]+)')
    rm_url = re.compile(r'https?://t.co/([A-Za-z0-9_]+)')
    rm_hashtag = re.compile(r'#(\w+)')
    for tweet in tweets_list:
        shape = rm_replie.sub('', tweet)
        shape = rm_url.sub('', shape)
        shape = rm_hashtag.sub('', shape)
        shape = shape.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&').replace('\n', ' ')
        shaped_tweets.append(shape)
    return shaped_tweets

# P.I.に突っ込む体裁を整えてjson形式"tweets.json"に
def tweets_trans_json(tweets_list, user):
    file_name = 'tweets-' + user +'.json'
    tweets_json = {}
    tweets_json['contentItems'] = []
    for tweet in tweets_list:
        data = cl.OrderedDict()
        data['content'] = tweet
        data['contenttype'] = 'text/plain'
        data['language'] = 'ja'
        tweets_json['contentItems'].append(data)
    with codecs.open(file_name, 'w', 'utf-8') as fw:
        json.dump(tweets_json, fw, indent=4 ,ensure_ascii=False)
    print(file_name + 'が生成されました')

# 生成したtweets.jsonをもとにWatsonAPI呼び出し
def get_insights_analytics(user):
    in_file_name = 'tweets-' + user + '.json'
    ex_file_name = 'analyzed-' + user + '.json'
    with open(join(dirname(abspath('__file__')), in_file_name), encoding='utf-8_sig') as tweets_json:
        profile = personality_insights.profile(
            tweets_json.read(),
            content_type='application/json',
            raw_scores=True,
            consumption_preferences=True
        )
        with codecs.open(ex_file_name, 'w', 'utf-8') as fw:
            json.dump(profile, fw, indent=2)
        print(ex_file_name + 'が生成されました')

# big5 の成分だけ抽出
def get_big5(user):
    file_name = 'analyzed-' + user + '.json'
    with open(join(dirname(abspath('__file__')), file_name), 'r') as analyzed_json:
        json_data = json.load(analyzed_json)
        big5 = []
        for data in json_data['personality']:
            rm_key = ['trait_id', 'category', 'significant', 'children']
            data = {key: data[key] for key in data if key not in rm_key}
            big5.append(data)
    return big5

users = []   
users.append(input('あなたのTwitter IDは？: '))
users.append(input('どのTwitter IDとの相性を診断しますか？: '))
print(users)


for user in users:
    file_name = 'big5-' + user + '.json'
    shaped_user_tweets = get_shaped_tweets(get_user_tweets(user))
    tweets_trans_json(shaped_user_tweets, user)
    if exists('./' + file_name)  == False:
        get_insights_analytics(user)
        with codecs.open(file_name, 'w', 'utf-8') as fw:
            json.dump(get_big5(user), fw, indent=2)
    print(get_big5(user))

# print('取得ツイート数: ', len(shaped_user_tweets))


# 以下、上記で受け取ったbig5\-\[user\].jsonに関して操作を行う(P.I.の使用回数の節約のため)

# In[ ]:


users = ['fu_wo_msk', 'mi_so_ka']
user_and_big5 = {}

# big5データ整形(後ほど上の項に組み込む)
for user in users:
    file_name = 'big5-' + user +'.json'
    shaped_data = {}
    with open('./' + file_name, 'r') as fr:
        data_list = json.load(fr)
        for data in data_list:
            shaped_data[data['name']] = data['percentile'] 
    user_and_big5[user] = shaped_data 
    
# big5の生の値の差を取り出す
def get_big5_diff(data):
    diffs = {}
    for status in data[users[0]].keys():
        diffs[status] = abs(data[users[0]][status] - data[users[1]][status])
    return diffs

# big5の差をわかりやすい数値に
def diff_trans_percent(data):
    diff_percents = {}
    for status in data.keys():
        diff_percents[status] = str(100 - round(data[status] * 100)) + '%'
    return diff_percents

diff = get_big5_diff(user_and_big5)
print(diff_trans_percent(diff))

