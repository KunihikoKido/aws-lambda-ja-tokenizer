import os
import platform
print os.getcwd()
import zipfile

from fabric.api import local, shell_env, lcd, env, task, settings, path
from fabric.contrib.console import confirm

BASE_PATH = os.getcwd()
LIB_PATH = os.path.join(BASE_PATH, 'lib')
TEMP_DIR = os.path.join(BASE_PATH, '.tmp')

ZIP_FILE = os.path.join(BASE_PATH, 'lambda_function.zip')
ZIP_EXCLUDE_FILE = os.path.join(BASE_PATH, 'exclude.lst')

LAMBDA_HANDLER = 'lambda_handler'
LAMBDA_FILE = 'lambda_function.py'
LAMBDA_EVENT = 'event.json'

MECAB_INSTALL_PREFIX = os.path.join(BASE_PATH, 'local')


# MeCab
def install_mecab():
    pkg_name = 'mecab-0.996'

    with lcd(TEMP_DIR):
        if not os.path.exists(os.path.join(TEMP_DIR, pkg_name)):
            local('wget http://mecab.googlecode.com/files/{}.tar.gz'.format(pkg_name))
            local('tar zvxf {}.tar.gz'.format(pkg_name))
        with lcd(pkg_name):
            local('./configure --prefix={} --enable-utf8-only'.format(MECAB_INSTALL_PREFIX))
            local('make && make install')


def install_mecab_ipadic():
    pkg_name = 'mecab-ipadic-2.7.0-20070801'

    with lcd(TEMP_DIR):
        if not os.path.exists(os.path.join(TEMP_DIR, pkg_name)):
            local('wget http://mecab.googlecode.com/files/{}.tar.gz'.format(pkg_name))
            local('tar zvxf {}.tar.gz'.format(pkg_name))
            local('nkf --overwrite -Ew {}/*'.format(pkg_name))
        with lcd(pkg_name), path(os.path.join(MECAB_INSTALL_PREFIX, 'bin'), behavior='prepend'):
            local('{}/libexec/mecab/mecab-dict-index -f utf-8 -t utf-8'.format(MECAB_INSTALL_PREFIX))
            local('./configure')
            local('make install')

@task
def install_python_modules():
    if platform.system() is 'Linux':
        local('echo -e "[install]\ninstall-purelib=\$base/lib64/python" > setup.cfg')

    with lcd(BASE_PATH), path(os.path.join(MECAB_INSTALL_PREFIX, 'bin'), behavior='prepend'):
        local('pip install --upgrade -r requirements.txt -t {}'.format(LIB_PATH))

@task
def install_mecab_neologd():
    pkg_name = 'mecab-ipadic-neologd'
    ipadic_pkg_name = 'mecab-ipadic-2.7.0-20070801'

    with lcd(TEMP_DIR):
        if not os.path.exists(os.path.join(TEMP_DIR, pkg_name)):
            local('git clone --depth 1 https://github.com/neologd/{}.git'.format(pkg_name))
            local('xz -dkv {}/seed/mecab-user-dict-seed.*.csv.xz'.format(pkg_name))
            local('mv {}/seed/mecab-user-dict-seed.*.csv {}/'.format(pkg_name, ipadic_pkg_name))
        with lcd(ipadic_pkg_name), path(os.path.join(MECAB_INSTALL_PREFIX, 'bin'), behavior='prepend'):
            local('{}/libexec/mecab/mecab-dict-index -f utf-8 -t utf-8'.format(MECAB_INSTALL_PREFIX))
            local('make install')


@task
def setup():
    if not os.path.exists(TEMP_DIR):
        local('mkdir {}'.format(TEMP_DIR))

    install_mecab()
    install_mecab_ipadic()
    install_python_modules()

    if confirm('Do you want to install mecab-ipadic-neologd?', default=False):
        install_mecab_neologd()

@task
def clean():
    local('rm -f lambda_function.zip')
    local('rm -rf lib')
    local('rm -rf local')
    local('rm -rf .tmp')

@task
def run(eventfile=LAMBDA_EVENT):
    with lcd(BASE_PATH):
        local("python-lambda-local -l {} -f {} {} {}".format(
            LIB_PATH, LAMBDA_HANDLER, LAMBDA_FILE, eventfile))

@task
def bundle():
    with lcd(BASE_PATH):
        local('rm -f {}'.format(ZIP_FILE))
        local('zip -r9 {} * -x @{}'.format(ZIP_FILE, ZIP_EXCLUDE_FILE))

    with lcd(LIB_PATH):
        local('zip -r9 {} * -x@{}'.format(ZIP_FILE, ZIP_EXCLUDE_FILE))
