#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/12 1:18 下午
# @Author  : yxChen

import os
from functools import lru_cache


# 只实例化一次
@lru_cache()
def get_settings():
    sys_env = os.getenv('FASTAPI_ENV')
    if sys_env == 'dev':
        from env_config.dev import Setting as Config
    elif sys_env == 'local':
        from env_config.local import Setting as Config
    elif sys_env == 'prod':
        from env_config.prod import Setting as Config
    else:
        from env_config.local import Setting as Config
    return Config()
