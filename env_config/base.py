#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/12 1:18 下午
# @Author  : yxChen

from pydantic import BaseSettings
import os


class BaseSetting(BaseSettings):
    static_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/static/'
    archive_host = 'http://localhost:8900/static/'
    config = {
        "host": "0.0.0.0",
        "port": 8900,
        "access_log": True,
        "use_colors": True,
        "log_config": {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s"
                },
                "access": {
                    "()": "uvicorn.logging.AccessFormatter",
                    "fmt": "[%(asctime)s] [%(client_addr)s] [%(name)s] [%(levelname)s]: %(request_line)s %(status_code)s"
                }
            },
            "handlers": {
                "file": {
                    "formatter": "default",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "./log.txt",
                    "level": "INFO"
                },
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr"
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout"
                }
            },
            "loggers": {
                "": {"handlers": ["default", "file"], "level": "INFO"},
                "uvicorn.access": {"handlers": ["access", "file"], "level": "INFO", "propagate": False}
            }
        },
    }
