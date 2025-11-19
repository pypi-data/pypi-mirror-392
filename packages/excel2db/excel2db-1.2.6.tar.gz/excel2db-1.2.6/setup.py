#!/usr/bin/env python
# coding: utf-8

import setuptools

setuptools.setup(
    name='excel2db', ##项目名
    version='1.2.6', ##项目版本
    author='endlessdesert', ##作者
    author_email='endlessdesert73@gmail.com', ##作者邮箱
    url='https://github.com',
    description='用于将excle文件转为数据库',
    packages=setuptools.find_packages(),
    install_requires=["openpyxl", "pandas", "xlrd", "msoffcrypto-tool"], ##所依赖的其他库，使用 pip 等工具安装时，会自动安装所依赖的包
)