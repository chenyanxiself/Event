#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/7/14 7:11 下午
# @Author  : yxChen


from fastapi import APIRouter, Body, Depends, UploadFile, File, Query
from consts.log_name import API_REPORT
from models.response_model.base_resm import BaseRes
from models.db_model.model import *
from models.db_model.db import Db
from util.jwt_util import auth_token
from models.request_model.user_reqm import TokenUser
import logging, datetime,json,traceback
from typing import List
from copy import deepcopy
from util.project_verify import verify_project_filed,verify_project_deleted,verify_project_member

router = APIRouter()
logger = logging.getLogger(API_REPORT)


@router.get('/getAllReport/', response_model=BaseRes, dependencies=[Depends(auth_token)])
async def get_all_report(project_id: int = Query(...)) -> BaseRes:
    _, error = verify_project_deleted(project_id)
    if error:
        return error
    try:
        report_list: List[AtpProjectTestReport] = Db.select_by_condition(
            AtpProjectTestReport,
            [
                AtpProjectTestReport.is_delete == '2',
                AtpProjectTestReport.project_id == project_id
            ],
            AtpProjectTestReport.create_time.desc()
        )
        for report in report_list:
            report.cname = Db.select_by_primary_key(SysUser, report.creator).cname
        return BaseRes(data=report_list)
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/deleteReportById/', response_model=BaseRes)
async def delete_report_by_id(
        id: int = Body(..., embed=True),
        project_id: int = Body(..., embed=True),
        token_user: TokenUser = Depends(auth_token)
):
    _, error = verify_project_filed(project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, project_id)
    if error:
        return error
    try:
        update_count: int = Db.update_by_condition(
            AtpProjectTestReport,
            [
                AtpProjectTestReport.id == id,
                AtpProjectTestReport.is_delete == '2',
            ],
            {
                AtpProjectTestReport.is_delete: '1',
                AtpProjectTestReport.updator: token_user.user_id,
                AtpProjectTestReport.update_time: datetime.datetime.now()
            }
        )
        return BaseRes(data=update_count)
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.get('/getReportDetail/', response_model=BaseRes, dependencies=[Depends(auth_token)])
async def get_report_detail(
        report_id: int = Query(...),
        project_id: int = Query(...),
) -> BaseRes:
    _, error = verify_project_deleted(project_id)
    if error:
        return error
    try:
        report_detail_list: List[AtpProjectTestReportDetail] = Db.select_by_condition(
            AtpProjectTestReportDetail,
            [
                AtpProjectTestReportDetail.is_delete == '2',
                AtpProjectTestReportDetail.report_id == report_id
            ],
            AtpProjectTestReportDetail.id
        )
        report: AtpProjectTestReport = Db.select_by_primary_key(AtpProjectTestReport, report_id)
        suite: AtpProjectApiSuite = Db.select_by_primary_key(AtpProjectApiSuite, report.suite_id)
        project: AtpProject = Db.select_by_primary_key(AtpProject, report.project_id)
        user:SysUser=Db.select_by_primary_key(SysUser,report.creator)
        status_code_distribution = {}
        for report_detail in report_detail_list:
            case:AtpProjectApiCase=Db.select_by_primary_key(AtpProjectApiCase,report_detail.case_id)
            report_detail.case_name=case.name
            if report.global_host:
                report_detail.host=report.global_host
            else:
                if case.is_use_env:
                    report_detail.host=Db.select_by_primary_key(AtpProjectEnv,case.env_host).host
                else:
                    report_detail.host=case.request_host
            report_detail.path = case.request_path
            if report.global_headers:
                init_header = json.loads(deepcopy(case.request_headers))
                if init_header is None:
                    report_detail.headers = json.loads(report.global_headers)
                else:
                    init_header.update(json.loads(report.global_headers))
                    report_detail.headers = init_header
            else:
                report_detail.headers=json.loads(case.request_headers)
            report_detail.params=json.loads(case.request_query)
            report_detail.body=json.loads(case.request_body)
            if status_code_distribution.get(report_detail.status,None):
                status_code_distribution[report_detail.status] = status_code_distribution[report_detail.status] + 1
            else:
                status_code_distribution.setdefault(report_detail.status, 1)
        res = {
            'report_id': report_id,
            'report_name':report.report_name,
            'suite_id': report.suite_id,
            'suite_name': suite.name,
            'project_id': report.project_id,
            'project_name': project.name,
            'global_host': report.global_host,
            'global_headers': report.global_headers,
            'is_save_cookie': report.is_save_cookie,
            'total_case_num': report.total_case_num,
            'success_case_num': report.success_case_num,
            'failed_case_num': report.failed_case_num,
            'status_code_distribution': status_code_distribution,
            'cname':user.cname,
            'detail': report_detail_list
        }
        return BaseRes(data=res)
    except Exception as e:
        logger.error(traceback.format_exc())
        return BaseRes(status=0, error=str(e))
