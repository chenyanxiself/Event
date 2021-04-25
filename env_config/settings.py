#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/12 1:18 下午
# @Author  : yxChen


config = None


def get_settings(env=None):
    global config
    if config:
        return config
    if env == 'dev':
        from env_config.dev import Setting as Config
    elif env == 'local':
        from env_config.local import Setting as Config
    elif env == 'prod':
        from env_config.prod import Setting as Config
    else:
        from env_config.local import Setting as Config
    config = Config()
    return config


if __name__ == '__main__':
    print(get_settings('prod').archive_host)
    print(get_settings().archive_host)
