#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/12 1:18 下午
# @Author  : yxChen

from pydantic import BaseSettings
import os


class BaseSetting(BaseSettings):
    static_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/static/'
    archive_host = 'http://10.212.42.107:8900/static/'
