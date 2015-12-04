import os
print os.getcwd()
import zipfile

from fabric.api import local, shell_env, lcd, env, task, settings, path

BASE_DIR = os.getcwd()
TEMP_DIR = os.path.join(BASE_DIR, '.tmp')

ZIP_FILE = os.path.join(BASE_DIR, 'lambda_function.zip')
ZIP_EXCLUDE_FILE = os.path.join(BASE_DIR, 'exclude.lst')

LAMBDA_HANDER = 'lambda_handler'
LAMBDA_FILE = 'lambda_function.py'
LAMBDA_EVENT = 'event.json'

MECAB_INSTALL_PREFIX = os.path.join(BASE_DIR, 'local')


# MeCab
def install_mecab():
    with lcd(TEMP_DIR):
        if not os.path.exists(os.path.join(TEMP_DIR, 'mecab-0.996')):
            local('wget http://mecab.googlecode.com/files/mecab-0.996.tar.gz')
            local('tar zvxf mecab-0.996.tar.gz')
        with lcd('mecab-0.996'):
            local('./configure --prefix={}'.format(MECAB_INSTALL_PREFIX))
            local('make && make install')


def install_mecab_ipadic():
    with path(os.path.join(MECAB_INSTALL_PREFIX, 'bin'), behavior='prepend'), lcd(TEMP_DIR):
        if not os.path.exists(os.path.join(TEMP_DIR, 'mecab-ipadic-2.7.0-20070801')):
            local('wget http://mecab.googlecode.com/files/mecab-ipadic-2.7.0-20070801.tar.gz')
            local('tar zvxf mecab-ipadic-2.7.0-20070801.tar.gz')
        with lcd('mecab-ipadic-2.7.0-20070801'):
            local('./configure --prefix={} --with-charset=utf-8'.format(MECAB_INSTALL_PREFIX))
            local('make && make install')

def install_python_modules():
    with path(os.path.join(MECAB_INSTALL_PREFIX, 'bin'), behavior='prepend'), lcd(BASE_DIR):
        local('pip install -r requirements.txt')

@task
def setup():
    if not os.path.exists(TEMP_DIR):
        local('mkdir {}'.format(TEMP_DIR))

    install_mecab()
    install_mecab_ipadic()
    install_python_modules()

@task
def run(eventfile=LAMBDA_EVENT):
    with lcd(BASE_DIR):
        local("python-lambda-local -f {} {} {}".format(LAMBDA_HANDER, LAMBDA_FILE, eventfile))

@task
def bundle():
    with lcd(BASE_DIR):
        local('rm -f {}'.format(ZIP_FILE))
        local('zip -r9 {} * -x @{}'.format(ZIP_FILE, ZIP_EXCLUDE_FILE))

    with settings(warn_only=True), lcd('$VIRTUAL_ENV/lib/python2.7/dist-packages'):
        local('zip -r9 {} * -x @{}'.format(ZIP_FILE, ZIP_EXCLUDE_FILE))

    with settings(warn_only=True), lcd('$VIRTUAL_ENV/lib/python2.7/site-packages'):
        local('zip -r9 {} * -x @{}'.format(ZIP_FILE, ZIP_EXCLUDE_FILE))
