#!/usr/bin/env python
#-*- coding:utf-8 -*-

from setuptools import setup, find_packages            #这个包没有的可以pip一下

setup(
    name = "print437437",      #这里是pip项目发布的名称
    version = "0.0.1",  #版本号，数值大的会优先被pip
    keywords = ["pip", "print437437"],			# 关键字
    description = "chuan's private utils.",	# 描述
    long_description = "chuan's private utils.",
    license = "MIT Licence",		# 许可证

    url = "https://github.com/chuan",     #项目相关文件地址，一般是github项目地址即可
    author = "chuan",			# 作者
    author_email = "wangchuan437@126.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["numpy", "pillow"]          #这个项目依赖的第三方库
    
    )