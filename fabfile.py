# coding=utf-8
import base64
import json
import os
import platform
import zipfile

from fabric.api import lcd
from fabric.api import local
from fabric.api import shell_env
from fabric.api import task
from fabric.api import path
from fabric.contrib.console import confirm

BASE_PATH = os.getcwd()
LIB_PATH = os.path.join(BASE_PATH, 'lib')
TEMP_DIR = os.path.join(BASE_PATH, 'tmp')

ZIP_FILE = os.path.join(BASE_PATH, 'lambda_function.zip')
ZIP_EXCLUDE_FILE = os.path.join(BASE_PATH, 'exclude.lst')

LAMBDA_HANDLER = 'lambda_handler'
LAMBDA_FILE = 'lambda_function.py'
LAMBDA_EVENT = 'event.json'
LAMBDA_FUNCTION_NAME = os.path.basename(BASE_PATH)

INSTALL_PREFIX = os.path.join(BASE_PATH, 'local')


# MeCab
def install_mecab():
    pkg_name = 'mecab-0.996'

    with lcd(TEMP_DIR):
        if not os.path.exists(os.path.join(TEMP_DIR, pkg_name)):
            local('wget http://mecab.googlecode.com/files/{}.tar.gz'.format(pkg_name))
            local('tar zvxf {}.tar.gz'.format(pkg_name))
        with lcd(pkg_name):
            local('./configure --prefix={} --enable-utf8-only'.format(INSTALL_PREFIX))
            local('make && make install')


def install_mecab_ipadic():
    pkg_name = 'mecab-ipadic-2.7.0-20070801'

    with lcd(TEMP_DIR):
        if not os.path.exists(os.path.join(TEMP_DIR, pkg_name)):
            local('wget http://mecab.googlecode.com/files/{}.tar.gz'.format(pkg_name))
            local('tar zvxf {}.tar.gz'.format(pkg_name))
            local('nkf --overwrite -Ew {}/*'.format(pkg_name))
        with lcd(pkg_name), path(os.path.join(INSTALL_PREFIX, 'bin'), behavior='prepend'):
            local('{}/libexec/mecab/mecab-dict-index -f utf-8 -t utf-8'.format(INSTALL_PREFIX))
            local('./configure')
            local('make install')

def install_python_modules():
    if platform.system() == 'Linux':
        local('echo -e "[install]\ninstall-purelib=\$base/lib64/python" > setup.cfg')

    with lcd(BASE_PATH), path(os.path.join(INSTALL_PREFIX, 'bin'), behavior='prepend'):
        local('pip install --upgrade -r requirements.txt -t {}'.format(LIB_PATH))

def install_mecab_neologd():
    pkg_name = 'mecab-ipadic-neologd'
    ipadic_pkg_name = 'mecab-ipadic-2.7.0-20070801'

    with lcd(TEMP_DIR):
        if not os.path.exists(os.path.join(TEMP_DIR, pkg_name)):
            local('git clone --depth 1 https://github.com/neologd/{}.git'.format(pkg_name))
            local('xz -dkv {}/seed/mecab-user-dict-seed.*.csv.xz'.format(pkg_name))
            local('mv {}/seed/mecab-user-dict-seed.*.csv {}/'.format(pkg_name, ipadic_pkg_name))
        with lcd(ipadic_pkg_name), path(os.path.join(INSTALL_PREFIX, 'bin'), behavior='prepend'):
            local('{}/libexec/mecab/mecab-dict-index -f utf-8 -t utf-8'.format(INSTALL_PREFIX))
            local('make install')


@task
def setup():
    """
    Setup on local machine.
    """
    if not os.path.exists(TEMP_DIR):
        local('mkdir {}'.format(TEMP_DIR))

    install_mecab()
    install_mecab_ipadic()
    install_python_modules()

    if confirm('Do you want to install mecab-ipadic-neologd?', default=False):
        install_mecab_neologd()

@task
def clean():
    """
    Clean up lambda_function.zip, lib, local and tmp.
    """
    local('rm -f lambda_function.zip')
    local('rm -rf {}'.format(LIB_PATH))
    local('rm -rf {}'.format(INSTALL_PREFIX))
    local('rm -rf {}'.format(TEMP_DIR))

@task
def invoke(eventfile=LAMBDA_EVENT):
    """
    Invoke lambda function on local machine.
    """
    with shell_env(PYTHONPATH=LIB_PATH):
        local("python-lambda-local -l {} -f {} {} {}".format(
            LIB_PATH, LAMBDA_HANDLER, LAMBDA_FILE, eventfile))

@task
def makezip():
    """
    Make bundle zip file.
    """
    with lcd(BASE_PATH):
        local('rm -f {}'.format(ZIP_FILE))
        local('zip -r9 {} * -x @{}'.format(ZIP_FILE, ZIP_EXCLUDE_FILE))

    with lcd(LIB_PATH):
        local('zip -r9 {} * -x@{}'.format(ZIP_FILE, ZIP_EXCLUDE_FILE))

@task
def awsupdate(function_name=LAMBDA_FUNCTION_NAME):
    """
    Update function code on AWS Lambda.
    """
    if confirm('Do you want to update function code on AWS Lambda?: {}'.format(function_name)):
        if not os.path.exists(ZIP_FILE):
            makezip()

        local("""
        aws lambda update-function-code \
            --function-name {} \
            --zip-file fileb://{}
        """.format(function_name, ZIP_FILE))

@task
def awsinvoke(function_name=LAMBDA_FUNCTION_NAME):
    """
    Invoke function on AWS Lambda.
    """
    outputfile = 'output.txt'

    result = local("""
    aws lambda invoke \
        --invocation-type RequestResponse \
        --function-name {} \
        --log-type Tail \
        --payload file://{} \
        {}
    """.format(function_name, LAMBDA_EVENT, outputfile), capture=True)

    result = json.loads(result)
    print(base64.b64decode(result.get('LogResult', '')))

    with open(outputfile) as f:
        result = json.dumps(json.loads(f.read()), ensure_ascii=False, indent=2)
        print(result)
