#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/12 3:04 下午
# @Author  : yxChen


from pydantic import BaseModel
from typing import Any


class BaseRes(BaseModel):
    code: str = 200
    status: int = 1
    data: Any = ''
    error: str = ''
