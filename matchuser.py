#!/usr/bin/env python
# coding: utf-8
import sys, json, re
import collections as cl
import codecs
from os.path import join, dirname, abspath, exists
from twitter import Twitter, OAuth
from watson_developer_cloud import PersonalityInsightsV3
import config

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

# jsonファイル格納場所、名前定義
json_folder = join(dirname(abspath('__file__')), 'tmp/')

def get_file_name(type, user):
    if type == 'tw':
        return 'tweets-' + user + '.json'
    elif type == 'an':
        return 'analyzed-' + user + 'json'
    else:
        try:
            raise ValueError("ファイル形式は tw/an で指定してください")
        except ValueError as e:
            print(e)

# ユーザー定義
users = []

# APIからツイートを取ってくる
def get_user_tweets(screen_name):
    number_of_tweets = 0
    count = 200
    max_id = ''
    tweets = []
    a_timeline = twitter.statuses.user_timeline(
        screen_name=screen_name,
        count=count,
        include_rts='false',
        tweet_mode='extended'
    )
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
        a_timeline = twitter.statuses.user_timeline(
            screen_name=screen_name,
            count=count,
            max_id=max_id,
            include_rts='false',
            tweet_mode='extended'
        )
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
def tweets_conv_json(tweets_list, user):
    tweets_json = {}
    tweets_json['contentItems'] = []
    for tweet in tweets_list:
        data = cl.OrderedDict()
        data['content'] = tweet
        data['contenttype'] = 'text/plain'
        data['language'] = 'ja'
        tweets_json['contentItems'].append(data)
    with codecs.open(join(json_folder, get_file_name('tw', user)), 'w', 'utf-8') as fw:
        json.dump(tweets_json, fw, indent=4 ,ensure_ascii=False)
    print(get_file_name('tw', user) + 'が生成されました')

# 生成したtweets.jsonをもとにWatsonAPI呼び出し
def get_insights_analytics(user):
    with open(join(json_folder, get_file_name('tw', user)), encoding='utf-8_sig') as tweets_json:
        profile = personality_insights.profile(
            tweets_json.read(),
            content_type='application/json',
            raw_scores=True,
            consumption_preferences=True
        )
        with open(join(json_folder, get_file_name('an', user)), 'w') as fw:
            json.dump(profile, fw, indent=2)
        print(get_file_name('an', user) + 'が生成されました')

# big5のpercentileだけ抽出
def get_big5(user):
    with open(join(json_folder, get_file_name('an', user)), 'r') as analyzed_json:
        json_data = json.load(analyzed_json)
        big5 = {}
        for data in json_data['personality']:
            big5[data['name']] = data['percentile']
    return big5

# big5の差を取り出す
def get_big5_diff(data, users):
    diffs = {}
    for status in data[users[0]].keys():
        diffs[status] = abs(data[users[0]][status] - data[users[1]][status])
    return diffs

# big5の差をわかりやすい数値に
def diff_conv_percent(data):
    diff_percents = {}
    for status in data.keys():
        diff_percents[status] = str(round(100 - data[status] * 100)) + '%'
    return diff_percents

# メイン処理
def display_result():
    big5 = {}
    for user in users:
        if exists(join(json_folder, get_file_name('tw', user))) == False:
            tweets = get_user_tweets(user)
            tweets = get_shaped_tweets(tweets)
            tweets_conv_json(tweets, user)
        else:
            print(get_file_name('tw', user) + 'が存在します。既存のファイルで処理を続行します。')

        if exists(join(json_folder, get_file_name('an', user))) == False:
            get_insights_analytics(user)
        else:
            print(get_file_name('an', user) + 'が存在します。既存のファイルで処理を続行します。')
        big5[user] = get_big5(user)

    big5_diff = get_big5_diff(big5, users)
    big5_result = diff_conv_percent(big5_diff)