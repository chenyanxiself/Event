#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/7/13 4:50 下午
# @Author  : yxChen
from typing import List
from models.db_model.model import (
    AtpProjectTestReport,
    AtpProjectTestReportDetail
)
from models.db_model.db import Db
import requests,logging
from requests.exceptions import ConnectTimeout
from consts.log_name import EXECUTE_SUITE
from datetime import datetime
import json,traceback
logger = logging.getLogger(EXECUTE_SUITE)

def execute_suite_request(
        request_list: List[dict],
        report_id: int
):
    session=Db.get_session()
    report_db_item=session.query(AtpProjectTestReport).filter(AtpProjectTestReport.id==report_id)
    report_db_item.update({
        AtpProjectTestReport.status:1
    })
    is_save_cookie=report_db_item.first().is_save_cookie
    session.commit()
    request_session=requests.session()
    success_count = 0
    failed_count = 0
    try:
        for request_item in request_list:
            request_arg = {
                'url':request_item.get('host')+request_item.get('path'),
                'method':request_item.get('method'),
                'params':request_item.get('params'),
                'headers':request_item.get('headers'),
            }
            is_json_body=False
            for k,v in request_item.get('headers',{}).items():
                if k.lower()=='content-type' and v.lower()=='application/json':
                    is_json_body=True
                    break
            if is_json_body:
                request_arg.setdefault('json',request_item.get('body'))
            else:
                request_arg.setdefault('data', request_item.get('body'))
            status_code = 0
            is_success=0
            try:
                if is_save_cookie:
                    res = request_session.request(**request_arg)
                else:
                    res = requests.request(**request_arg)
                status_code = res.status_code
                if not str(status_code).startswith('2'):
                    is_success = 0
                else:
                    is_success = 1
                response = res.content.decode('utf-8')
            except ConnectTimeout as e:
                logger.error(e)
                response='TimeOut!'
            except Exception as e:
                logger.error(e)
                response=str(e)
            if is_success == 1:
                success_count+=1
            else:
                failed_count+=1
            report_detail_item = AtpProjectTestReportDetail(
                report_id=report_id,
                case_id=request_item.get('case_id'),
                status=status_code,
                response=response,
                is_success=is_success
            )
            session.add(report_detail_item)
            report_db_item.update({
                AtpProjectTestReport.success_case_num: success_count,
                AtpProjectTestReport.failed_case_num: failed_count,
            })
            session.commit()
        report_db_item.update({
            AtpProjectTestReport.status: 2,
            AtpProjectTestReport.finish_time: datetime.now(),
        })
        session.commit()
    except Exception:
        logger.error(traceback.format_exc())
        report_db_item.update({
            AtpProjectTestReport.status: 3,
            AtpProjectTestReport.finish_time: datetime.now(),
        })
        session.commit()



