#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/12 1:18 下午
# @Author  : yxChen

from env_config.base import BaseSetting


class Setting(BaseSetting):
    archive_host = 'http://47.100.70.151:8900/static/'
    mysql_config = {
        'host': 'localhost',
        'port': 3306,
        'username': 'root',
        'password': 'root',
        'database': 'auto_test_frame'
    }
