# Japanese Tokenizer for AWS Lambda
AWS Lambdaで日本語形態素解析（MeCab）を使うためのサンプルプロジェクトです。
MeCabはコードにネイティブバイナリを使用している為、以下のリンク先を参考にLambda実行環境と同じ環境でコンパイルしてください。(Amazon Linux)

※ 参考: [Lambda 実行環境と利用できるライブラリ](http://docs.aws.amazon.com/ja_jp/lambda/latest/dg/current-supported-versions.html)

## About lambda function
Amazon API Gateway + Lambda でサーバーレスの形態素解析API作ったりとか、他のLambdaから呼び出して、形態素解析用のファンクションとして使うとか、とかとか。。

#### Runtime
Python 2.7

#### Lambda Hander
lambda_function.lambda_handler

#### Input event

* ``sentence``: 形態素解析対象の文字列
* ``stoptags``: 解析結果から除外したい品詞タグ（※ 複数設定する場合はカンマ区切りで指定可能）
* ``unk_feature``: 未知語を表示する。このフラグを ``true`` にすると未知語の品詞推定をやめ、未知語は常に "未知語" 品詞を出力します。default to ``false``

Input event sample:
```python
{
  "sentence": "今日は良い天気です",
  "stoptags": "助詞-係助詞"
}
```

#### Execution result

* ``reading``: 読み
* ``pos``: 品詞（品詞-品詞細分類1-品詞細分類2-品詞細分類3）
* ``baseform``: 原型
* ``surface``: 形態素の文字列情報
* ``feature``:  CSVで表記された素性情報
* ``stat``: 形態素の種類
  * 0: MECAB_NOR_NODE
  * 1: MECAB_UNK_NODE
  * 2: MECAB_BOS_NODE
  * 3: MECAB_EOS_NODE


Execution result sample:
```python
{
  "tokens": [
    {
      "reading": "キョウ",
      "pos": "名詞-副詞可能",
      "baseform": "今日",
      "surface": "今日",
      "feature": "名詞,副詞可能,*,*,*,*,今日,キョウ,キョー"
    },
    {
      "reading": "ヨイ",
      "pos": "形容詞-自立",
      "baseform": "良い",
      "surface": "良い",
      "feature": "形容詞,自立,*,*,形容詞・アウオ段,基本形,良い,ヨイ,ヨイ"
    },
    {
      "reading": "テンキ",
      "pos": "名詞-一般",
      "baseform": "天気",
      "surface": "天気",
      "feature": "名詞,一般,*,*,*,*,天気,テンキ,テンキ"
    },
    {
      "reading": "デス",
      "pos": "助動詞",
      "baseform": "です",
      "surface": "です",
      "feature": "助動詞,*,*,*,特殊・デス,基本形,です,デス,デス"
    },
    {
      "reading": "。",
      "pos": "記号-句点",
      "baseform": "。",
      "surface": "。",
      "feature": "記号,句点,*,*,*,*,。,。,。"
    }
  ]
}
```

## Setup on local machine
ローカルでLambda関数を実行するには、最初に以下のステプで環境をセットアップしてください。
なお、MeCab本体とIPA辞書は、``./local``配下にインストールされます。

```bash
# 1. Clone this repository with AWS Lambda function name.
git clone https://github.com/KunihikoKido/aws-lambda-ja-tokenizer.git ja-tokenizer

# 2. Create and Activate a virtualenv
cd ja-tokenizer
virtualenv env
source env/bin/activate

# 3. Install python modules for local machine.
pip install -r requirements/local.txt

# 4. Compile and Install MeCab and etc.
fab setup
```

> **注意**
> mecab-ipadic-neologd をシステム辞書に含める場合は、``fab setup`` 以下の問いで``y``を入力してください。
>
> ``Do you want to install mecab-ipadic-neologd? [y/N] ``
>
> ただし、サイズが大きいためLambdaのパッケージサイズ制限を超えてしまいます。。


## Run lambda function on local machine
ローカルでLambda関数を実行するには、``fab invoke``コマンドを実行します。

```bash
fab invoke
```

#### Custom event
通常はインプットイベントに``event.json``が使用されますが、他のファイルを使用することも可能です。

以下の例は、新たに作成した``custom-event.json``をインプットイベントに指定して実行する例です。

```bash
fab invoke:custom-event.json
```


## Make bundle zip
以下のステップで、AWS Lambda に登録可能な ``lambda_function.zip`` ファイルが作成されます。

```bash
fab makezip
```
※ ZIPファイルは10MB超えるので、S3経由アップロードしてください。

## Update function code on AWS Lambda

```bash
fab aws-updatecode
```

## Invoke function on AWS Lambda

```bash
fab aws-invoke
```

## Get function configuration on AWS Lambda

```bash
fab aws-getconfig
```

## Snapshot Builds
ビルド済みの``lambda_function.zip``は以下のURLを参照してください。

https://github.com/KunihikoKido/aws-lambda-ja-tokenizer/releases

## with Amazon API Gateway
### _Example Settings_

_Method and Resources:_
```
GET /tokenize
```
_Query Strings:_
* ``sentence``: センテンス
* ``stoptags``: 除外品詞タグ

_Request mapping template:_
```json
{
  "sentence": "$util.urlDecode($input.params('sentence'))",
  "stoptags": "$util.urlDecode($input.params('stoptags'))"
}
```

_Example Request:_
```bash
GET /tokenize?sentence=%E4%BB%8A%E6%97%A5%E3%81%AF%E8%89%AF%E3%81%84%E5%A4%A9%E6%B0%97%E3%81%A7%E3%81%99
```
