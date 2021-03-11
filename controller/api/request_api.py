#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/22 5:49 下午
# @Author  : yxChen


from fastapi import APIRouter, Body, Depends, UploadFile, File, Query
from consts.log_name import API_REQUEST
from models.response_model.base_resm import BaseRes
from models.db_model.model import AtpProject, AtpProjectEnv
from models.db_model.db import Db
from models.request_model.request_reqm import ApiCase
from util.jwt_util import auth_token
import logging, hashlib, time, os, datetime
from env_config.settings import get_settings
from typing import List
import consts.request_consts as reqest_consts
import requests,time
from requests.exceptions import ConnectTimeout

router = APIRouter()
logger = logging.getLogger(API_REQUEST)


@router.post('/singleCaseDebug/', response_model=BaseRes, dependencies=[Depends(auth_token)])
async def single_case_debug(apiCase: ApiCase) -> BaseRes:
    request_host: str
    if apiCase.request_host.is_user_env:
        request_host_item: AtpProjectEnv = Db.select_by_primary_key(AtpProjectEnv, int(apiCase.request_host.env_host))
        request_host = request_host_item.host
    else:
        request_host = apiCase.request_host.request_host
    request_path: str = apiCase.request_path
    is_json_data: bool = False
    if apiCase.request_headers:
        for k,v in apiCase.request_headers.items():
            if k.lower() == 'content-type' and v.lower() == 'application/json':
                is_json_data = True
    request_method: int = apiCase.request_method
    try:
        if request_method == reqest_consts.GET_METHOD:
            res = requests.get(
                url=request_host + request_path,
                headers=apiCase.request_headers,
                params=apiCase.request_query,
                timeout=reqest_consts.TIMEOUT
            )
        elif request_method == reqest_consts.POST_METHOD:
            if is_json_data:
                res = requests.post(
                    url=request_host + request_path,
                    headers=apiCase.request_headers,
                    params=apiCase.request_query,
                    json=apiCase.request_body,
                    timeout=reqest_consts.TIMEOUT
                )
            else:
                res = requests.post(
                    url=request_host + request_path,
                    headers=apiCase.request_headers,
                    params=apiCase.request_query,
                    data=apiCase.request_body,
                    timeout=reqest_consts.TIMEOUT
                )
        else:
            return BaseRes(status=0, error='request method error' )
        duration_time = res.elapsed.seconds * 1000 + int(res.elapsed.microseconds/(1000))
        return_data={
            'response':res.text,
            'status':res.status_code,
            'time':duration_time,
            'assert':0 if str(res.status_code).startswith('4') else 1
        }
        return BaseRes(data=return_data)
    except ConnectTimeout as e:
        logger.error(e)
        return_data = {
            # 'response': f'Timeout! url : {request_host + request_path}!',
            'response':str(e),
            'status': 0,
            'time': 0,
            'assert': 0
        }
        return BaseRes(data=return_data)
    except Exception as e:
        logger.error(e)
        return_data = {
            # 'response': f'There was an error connecting to {request_host + request_path} !',
            'response':str(e),
            'status': 0,
            'time': 0,
            'assert': 0
        }
        return BaseRes(data=return_data)
