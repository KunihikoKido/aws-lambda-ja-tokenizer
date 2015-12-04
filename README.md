# Japanese tokenizer for AWS Lambda
AWS Lambdaで日本語形態素解析（MeCab）を使うためのサンプルプロジェクトです。
MeCabはコードにネイティブバイナリを使用している為、以下のリンク先を参考にLambda実行環境と同じ環境でコンパイルしてください。(Amazon Linux)

※ 参考: [Lambda 実行環境と利用できるライブラリ](http://docs.aws.amazon.com/ja_jp/lambda/latest/dg/current-supported-versions.html)

## About lambda function
#### Runtime
Python 2.7

#### Lambda Hander
lambda_function.lambda_handler

#### Input event

* ``sentence``: 形態素解析対象の文字列
* ``stoptags``: 解析結果から除外したい品詞タグ（※ 複数設定する場合はカンマ区切りで指定可能）

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
      "reading": "ハ",
      "pos": "助詞-係助詞",
      "baseform": "は",
      "surface": "は",
      "feature": "助詞,係助詞,*,*,*,*,は,ハ,ワ"
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
# 1. Create a virtualenv
virtualenv env
# 2. Activate the virtualenv
source ~/env/bin/activate
# 3. Install fabric and python-lambda-local
pip install fabric
pip install python-lambda-local
# 4. Clone repository
git clone https://github.com/KunihikoKido/lambda-ja-analyzer.git
# 5. Install requirements modules
cd lambda-ja-analyzer
fab setup
```

## Run lambda function on local machine
ローカルでLambda関数を実行するには、``fab run``コマンドを実行します。

```bash
# 1. Activate virtualenv
source ~/env/bin/activate
cd lambda-ja-analyzer
# 2. Run lambda function on local machine
fab run
```

通常はインプットイベントに``event.json``が使用されますが、他のファイルを使用することも可能です。

以下の例は、新たに作成した``custom-event.json``をインプットイベントに指定して実行する例です。

```bash
fab run:custom-event.json
```


## Make bundle zip
以下のステップで、AWS Lambda に登録可能な ``lambda_function.zip`` ファイルが作成されます。

```bash
# 1. Activate virtualenv
source ~/env/bin/activate
cd lambda-ja-analyzer
# 2 Make bundle zip for Lambda function
fab bundle
```
