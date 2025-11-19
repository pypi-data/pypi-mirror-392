#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 注意：要使用此文件的'上传'功能，你必须：
#   $ pipenv install twine --dev

import io
import os
import sys
from shutil import rmtree  # 用于删除目录

from setuptools import find_packages, setup, Command  # 导入setuptools的函数和类

# 包的元数据。
NAME = 'nonebot_plugin_game_tools'  # 包名
DESCRIPTION = '游戏工具插件.'  # 包的简短描述
URL = 'https://github.com/snowrabbit-top/nonebot_plugin_game_tools'  # 项目的URL
EMAIL = 'snowrabbit@snowrabbit.top'  # 作者的邮箱
AUTHOR = 'SnowRabbit'  # 作者名
REQUIRES_PYTHON = '>=3.9.0'  # 需要的Python版本
VERSION = '1.0.11'  # 版本号

# 执行此模块需要哪些包？
REQUIRED = [
    'nonebot2',
]

# 哪些包是可选的？
EXTRAS = {
}

# 剩下的你不应该需要太多地触碰 :)
# ------------------------------------------------

here = os.path.abspath(os.path.dirname(__file__))  # 获取当前文件的绝对路径

# 导入README并使用它作为长描述。
# 注意：这只会在你的MANIFEST.in文件中存在'README.md'时工作！
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# 加载包的__version__.py模块作为一个字典。
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


# 上传命令类
class UploadCommand(Command):
    """支持setup.py上传。"""
    description = '构建和发布包。'
    user_options = []

    @staticmethod
    def status(s):
        """打印粗体字。"""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


# 魔法发生的地方：
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',  # 长描述的类型
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*", "*.egg-info"]),  # 查找包
    install_requires=REQUIRED,  # 安装所需的包
    extras_require=EXTRAS,  # 可选包
    include_package_data=True,  # 包含包数据
    license='MIT',  # 许可证
    classifiers=[  # 分类器
        # Trove分类器
        # 完整列表：https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    # $ setup.py publish支持。
    cmdclass={
        'upload': UploadCommand,  # 注册上传命令
    },
)
