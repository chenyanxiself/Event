#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/12 10:24 上午
# @Author  : yxChen

from pydantic import BaseModel
from fastapi import Body
from typing import List


class TokenUser(BaseModel):
    user_id: int
    user_cname: str


class LoginUser(BaseModel):
    user_name: str
    password: str = Body(...)


class AddUser(BaseModel):
    user_name: str = Body(...)
    password: str = Body(...)
    user_cname: str = Body(...)
    email: str = Body(None)
    phone: str = Body(None)
    role_ids: List[int] = Body(None)


class UpdatePassword(BaseModel):
    old_password: str = Body(...)
    new_password: str = Body(...)


class UpdateUserInfo(BaseModel):
    user_id: int = Body(...)
    user_cname: str = Body(...)
    email: str = Body(None)
    phone: str = Body(None)
    role_ids: List[int] = Body(None)
