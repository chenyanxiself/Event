#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/12 10:24 上午
# @Author  : yxChen

from pydantic import BaseModel
from fastapi import Body

class TokenUser(BaseModel):
    user_id: int
    user_cname: str

class LoginUser(BaseModel):
    user_name:str
    password:str=Body(...)

class AddUser(LoginUser):
    user_cname:str
    email:str = ''
    phone:str = ''

class UpdatePassword(BaseModel):
    old_password:str=Body(...)
    new_password:str=Body(...)

class UpdateUserInfo(BaseModel):
    user_cname:str=Body(...)
    email:str=Body(None)
    phone:str=Body(None)
