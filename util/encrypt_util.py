#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/12 10:30 上午
# @Author  : yxChen

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'])
def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)

