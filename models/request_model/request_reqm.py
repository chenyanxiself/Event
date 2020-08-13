#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/22 5:53 下午
# @Author  : yxChen


from pydantic import BaseModel
from fastapi import Body
from typing import List


class RequestHost(BaseModel):
    env_host: int = Body(None)
    is_user_env: bool = Body(...)
    request_host: str = Body(None)

class Args(BaseModel):
    arg:str=Body(...)
    value:str=Body(...)

class ApiCase(BaseModel):
    request_path: str = Body(None)
    request_host: RequestHost = Body(...)
    request_method: int = Body(...)
    request_headers:dict = Body(None)
    request_query: dict = Body(None)
    request_body: dict = Body(None)

