# -*- coding: utf-8 -*-
import os
import platform
from fabric.api import local
from fabric.api import task
from fabric.api import lcd
from fabric.api import path
from fabric.contrib.console import confirm

from fabric_aws_lambda import SetupTask as BaseSetupTask
from fabric_aws_lambda import InvokeTask
from fabric_aws_lambda import MakeZipTask
from fabric_aws_lambda import AWSLambdaInvokeTask
from fabric_aws_lambda import AWSLambdaGetConfigTask
from fabric_aws_lambda import AWSLambdaUpdateCodeTask

BASE_PATH = os.path.dirname(__file__)

LIB_PATH = os.path.join(BASE_PATH, 'lib')
INSTALL_PREFIX = os.path.join(BASE_PATH, 'local')

REQUIREMENTS_TXT = os.path.join(BASE_PATH, 'requirements.txt')

LAMBDA_FUNCTION_NAME = os.path.basename(BASE_PATH)
LAMBDA_HANDLER = 'lambda_handler'
LAMBDA_FILE = os.path.join(BASE_PATH, 'lambda_function.py')

EVENT_FILE = os.path.join(BASE_PATH, 'event.json')

ZIP_FILE = os.path.join(BASE_PATH, 'lambda_function.zip')
ZIP_EXCLUDE_FILE = os.path.join(BASE_PATH, 'exclude.lst')

MECAB_PKG = 'mecab-0.996'
MECAB_IPADIC_PKG = 'mecab-ipadic-2.7.0-20070801'
MECAB_NEOLOGD_PKG = 'mecab-ipadic-neologd'

class SetupTask(BaseSetupTask):
    def install_python_modules(self):
        if platform.system() == 'Linux':
            local('echo -e "[install]\ninstall-purelib=\$base/lib64/python" > setup.cfg')

        options = dict(requirements=self.requirements, lib_path=self.lib_path)
        with lcd(BASE_PATH), path(os.path.join(self.install_prefix, 'bin'), behavior='prepend'):
            local('pip install --upgrade -r {requirements} -t {lib_path}'.format(**options))

    def pre_task(self):
        with lcd(self.tempdir):
            local('rm -rf *')
            self.install_mecab(pkg_name=MECAB_PKG)
            self.install_mecab_ipadic(pkg_name=MECAB_IPADIC_PKG)

    def post_task(self):
        if confirm('Do you want to install mecab-ipadic-neologd?', default=False):
            with lcd(self.tempdir):
                self.install_mecab_neologd(MECAB_NEOLOGD_PKG, MECAB_IPADIC_PKG)

    def install_mecab(self, pkg_name):
        local('wget -O mecab-0.996.tar.gz "https://drive.google.com/uc?export=download&id=0B4y35FiV1wh7cENtOXlicTFaRUE"')
        local('tar zvxf {}.tar.gz'.format(pkg_name))
        with lcd(pkg_name):
            local('./configure --prefix={} --enable-utf8-only'.format(self.install_prefix))
            local('make && make install')

    def install_mecab_ipadic(self, pkg_name):
        local('wget -O mecab-ipadic-2.7.0-20070801.tar.gz "https://drive.google.com/uc?export=download&id=0B4y35FiV1wh7MWVlSDBCSXZMTXM"')
        local('tar zvxf {}.tar.gz'.format(pkg_name))
        local('nkf --overwrite -Ew {}/*'.format(pkg_name))
        with lcd(pkg_name), path(os.path.join(self.install_prefix, 'bin'), behavior='prepend'):
            local('{}/libexec/mecab/mecab-dict-index -f utf-8 -t utf-8'.format(self.install_prefix))
            local('./configure')
            local('make install')

    def install_mecab_neologd(self, pkg_name, mecab_ipadic):
        local('git clone --depth 1 https://github.com/neologd/{}.git'.format(pkg_name))
        local('xz -dkv {}/seed/mecab-user-dict-seed.*.csv.xz'.format(pkg_name))
        local('mv {}/seed/mecab-user-dict-seed.*.csv {}/'.format(pkg_name, mecab_ipadic))
        with lcd(mecab_ipadic), path(os.path.join(self.install_prefix, 'bin'), behavior='prepend'):
            local('{}/libexec/mecab/mecab-dict-index -f utf-8 -t utf-8'.format(self.install_prefix))
            local('make install')



@task
def clean():
    for target in [ZIP_FILE, LIB_PATH, INSTALL_PREFIX]:
        local('rm -rf {}'.format(target))

task_setup = SetupTask(
    requirements=REQUIREMENTS_TXT,
    lib_path=LIB_PATH,
    install_prefix=INSTALL_PREFIX
)

task_invoke = InvokeTask(
    lambda_file=LAMBDA_FILE,
    lambda_handler=LAMBDA_HANDLER,
    event_file=EVENT_FILE,
    lib_path=LIB_PATH
)
task_makezip = MakeZipTask(
    zip_file=ZIP_FILE,
    exclude_file=ZIP_EXCLUDE_FILE,
    lib_path=LIB_PATH
)

task_aws_invoke = AWSLambdaInvokeTask(
    function_name=LAMBDA_FUNCTION_NAME,
    payload='file://{}'.format(EVENT_FILE)
)

task_aws_getconfig = AWSLambdaGetConfigTask(
    function_name=LAMBDA_FUNCTION_NAME,
)

task_aws_updatecode = AWSLambdaUpdateCodeTask(
    function_name=LAMBDA_FUNCTION_NAME,
    zip_file='fileb://{}'.format(ZIP_FILE)
)
