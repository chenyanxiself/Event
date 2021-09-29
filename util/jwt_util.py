#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/11 9:42 下午
# @Author  : yxChen

from datetime import datetime, timedelta
from typing import Optional

import jwt
from jwt import PyJWTError
from fastapi import Depends, status
from fastapi.websockets import WebSocketDisconnect, WebSocket
from fastapi.security import OAuth2PasswordBearer
from starlette.exceptions import HTTPException
from models.request_model.user_reqm import TokenUser

SECRET_KEY = "ahsdkjhdf443hdhufjds89u839074ounfls556dsd5f5gd4fgdr"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", scheme_name="TOKEN")


def create_access_token(*, data: dict, expires_delta: timedelta = timedelta(days=3)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def auth_token(*, token: str = Depends(oauth2_scheme)) -> TokenUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        user_cname: str = payload.get("cname")
        if user_id is None or user_cname is None:
            raise credentials_exception
        user = TokenUser(user_id=user_id, user_cname=user_cname)
    except PyJWTError:
        raise credentials_exception
    return user


async def auth_websocket_token(
        websocket: WebSocket,
):
    token: str = websocket.headers.get("Authorization")
    try:
        token = token.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        user_cname: str = payload.get("cname")
        if user_id is None or user_cname is None:
            return None
        user = TokenUser(user_id=user_id, user_cname=user_cname)
    except PyJWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
    return user
