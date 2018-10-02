# matching_users_by_tweets
指定したユーザーと自分の性格的相性が良いのかどうかをそれぞれの過去のツイートから分析してくれるWebアプリケーション  
Demo : [Twitter相性診断](https://matching-users-by-tweets.herokuapp.com/)
  
アイデア主・責任者 : 渡辺大智 (seven0525)  
共同開発者 : @mimizukmsk

## Requirements
このアプリには  

- Twitter API
- IBM Watson Personality Insights API

を使用しています。  
事前にそれぞれへのトークン取得が必要です。  
  
## Install & Run

1. Python3.6 をインストール
2. `$ pip install pipenv`
3. git からリポジトリをクローン
```bash
$ git clone git@github.com:seven0525/matching_users_by_tweets.git
$ cd matching_users_by_tweets
```
4. config-test.pyに自身のAPIトークン情報を書き込んでリネーム
```bash
$ [YOUR TEXT EDITOR] config-sample.py
$ mv config-sample.py config.py
```
5. `$ pipenv install`
6. `$ pipenv shell`
7. `$ python main.py` (Run at localhost)
  
## Built With

- Python 3.6
- pipenv
- Flask
- [sixohsix/twitter](https://github.com/sixohsix/twitter)
- [watson-developer-cloud/python-sdk](https://github.com/watson-developer-cloud/python-sdk) ver.1.7.1
- Chart.js
- jQuery
- Bootstrap
