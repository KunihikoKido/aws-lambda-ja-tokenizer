import os
print os.getcwd()
import zipfile

from fabric.api import local, shell_env, run, lcd, env
from fabric.context_managers import path

BASE_PATH = os.getcwd()
LIB_PATH = os.path.join(BASE_PATH, 'lib')
DIST_DIR = os.path.join(BASE_PATH, 'dist')
ZIP_FILE = os.path.join(BASE_PATH, 'bundle.zip')
ZIP_EXCLUDE_FILE = os.path.join(BASE_PATH, 'exclude.lst')

LAMBDA_HANDER = 'lambda_handler'
LAMBDA_FILE = 'lambda_function.py'
LAMBDA_EVENT = 'event.json'

MECAB_HOME = os.path.join(BASE_PATH, 'local')
MECAB_LIB = os.path.join(MECAB_HOME, 'lib')

# MeCab
def install_mecab():
    with lcd(DIST_DIR):
        local('wget http://mecab.googlecode.com/files/mecab-0.996.tar.gz')
        local('tar zvxf mecab-0.996.tar.gz')
        with lcd(os.path.join(DIST_DIR, 'mecab-0.996')):
            local('./configure --prefix={}'.format(MECAB_HOME))
            local('make && make install')

def install_mecab_ipadic():
    with path(os.path.join(MECAB_HOME, 'bin'), behavior='prepend'), lcd(DIST_DIR):
        local('wget http://mecab.googlecode.com/files/mecab-ipadic-2.7.0-20070801.tar.gz')
        local('tar zvxf mecab-ipadic-2.7.0-20070801.tar.gz')
        with lcd(os.path.join(DIST_DIR, 'mecab-ipadic-2.7.0-20070801')):
            local('./configure --prefix={} --with-charset=utf-8'.format(MECAB_HOME))
            local('make && make install')

def install_requirements():
    with path(os.path.join(MECAB_HOME, 'bin'), behavior='prepend'):
        local('pip install -r requirements.txt')

# def install_mecab_python():
#     with path(os.path.join(MECAB_HOME, 'bin'), behavior='prepend'), lcd(DIST_DIR):
#         local('wget https://mecab.googlecode.com/files/mecab-python-0.996.tar.gz')
#         local('tar zvxf mecab-python-0.996.tar.gz')
#         with lcd(os.path.join(DIST_DIR, 'mecab-python-0.996')):
#             local('python setup.py install --install-lib={}'.format(LIB_PATH))

    # with path(os.path.join(MECAB_HOME, 'bin'), behavior='prepend'):
    #     local('pip install --upgrade -r requirements.txt -t {}'.format(LIB_PATH))

# fab commands
def setup():
    if not os.path.exists(DIST_DIR):
        local('mkdir {}'.format(DIST_DIR))

    install_mecab()
    install_mecab_ipadic()
    install_requirements()
    # install_mecab_python()

def invoke():
    local("python-lambda-local -l {} -f {} {} {}".format(
        LIB_PATH, LAMBDA_HANDER, LAMBDA_FILE, LAMBDA_EVENT))

def bundle():
    with lcd(BASE_PATH):
        local('rm -f {}'.format(ZIP_FILE))
        local('zip -r9 {} * -x @{}'.format(ZIP_FILE, ZIP_EXCLUDE_FILE))

    if os.path.exists('$VIRTUAL_ENV/lib/python2.7/dist-packages'):
        with lcd('$VIRTUAL_ENV/lib/python2.7/dist-packages'):
            local('zip -r9 {} * -x @{}'.format(ZIP_FILE, ZIP_EXCLUDE_FILE))

    if os.path.exists('$VIRTUAL_ENV/lib/python2.7/site-packages'):
        with lcd('$VIRTUAL_ENV/lib/python2.7/site-packages'):
            local('zip -r9 {} * -x @{}'.format(ZIP_FILE, ZIP_EXCLUDE_FILE))
