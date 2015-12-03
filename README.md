# lambda-ja-analyzer

## Virtualenv
```bash
$ virtualenv $HOME/.virtualenv/lambda
$ source $HOME/.virtualenv/lambda/bin/activate
$ pip fabric
$ pip python-lambda-local
```

## Clone
```bash
$ git clone https://github.com/KunihikoKido/lambda-ja-analyzer.git lambda-ja-analyzer
```

## Install MeCab
```bash
$ tar zvxf mecab-0996.tar.gz
$ cd mecab-0996
$ ./configure --prefix=$HOME/lambda-ja-analyzer/local
$ make check
$ make
$ make install
```

```bash
export PATH=$HOME/lambda-ja-analyzer/local/bin:$PATH
$ tar zvxf mecab-ipadic-2.7.0-20070801.tar.gz
$ cd mecab-ipadic-2.7.0-20070801
$ ./configure --prefix=$HOME/lambda-ja-analyzer/local --with-charset=utf-8
$ make
$ make install
```

```bash
$ fab init
```

```bash
$ fab run
```

```bash
$ fab bundle
```
