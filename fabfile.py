import os
print os.getcwd()
import zipfile

from fabric.api import local, shell_env, run, lcd

BASE_PATH = os.getcwd()
LIB_PATH = os.path.join(BASE_PATH, 'lib')
ZIP_FILE = os.path.join(BASE_PATH, 'bundle.zip')

def init():
    local("""
    pip install \
        --upgrade \
        -r requirements.txt \
        -t {lib_path}
    """.format(lib_path=LIB_PATH))

def run():

    local("""
    python-lambda-local \
        -l {lib_path} \
        -f lambda_handler \
        lambda_function.py \
        event.json
    """.format(lib_path=LIB_PATH))

def bundle():
    init()

    local('rm -f {zip_file}'.format(zip_file=ZIP_FILE))

    local("""
    zip -r9 {zip_file} * \
        -x \*.pyc \*.zip .gitignore .git\* \
        lib\* dist\* event.json local_settings.py
    """.format(zip_file=ZIP_FILE))

    with lcd(LIB_PATH):
        local('zip -r9 {zip_file} * -x *.pyc'.format(zip_file=ZIP_FILE))
