#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/7/30 11:09 上午
# @Author  : yxChen


from fastapi import APIRouter, Body, Depends, UploadFile, File, Query
from consts.log_name import API_WORKSTATION
from models.response_model.base_resm import BaseRes
from models.request_model.project_reqm import Module, UpdateModule
from models.db_model.model import *
from models.db_model.db import Db
from util.jwt_util import auth_token
from models.request_model.user_reqm import TokenUser
import logging, datetime, json, traceback
from typing import List
from models.request_model.project_reqm import *
from copy import deepcopy
from util.project_verify import verify_project_filed, verify_project_deleted, verify_project_member
import controller.domain.project_case_domain as domain
from config.settings import get_settings

router = APIRouter()
logger = logging.getLogger(API_WORKSTATION)


@router.get('/getWorkstationProjects', response_model=BaseRes, dependencies=[Depends(auth_token)])
async def get_workstation_projects(token_user: TokenUser = Depends(auth_token)) -> BaseRes:
    try:
        project_list: List[AtpProject] = Db.select_by_condition(AtpProject,
                                                                [AtpProject.type == 1, AtpProject.is_delete == 2],
                                                                AtpProject.create_time.desc())
        parted_project_list = []
        for project in project_list:
            is_part_in = Db.select_by_condition(
                AtpProjectMember,
                [
                    AtpProjectMember.is_delete == 2,
                    AtpProjectMember.project_id == project.id,
                    AtpProjectMember.member_id.in_([token_user.user_id])
                ],
            )
            if is_part_in:
                parted_project_list.append(project)
            if project.img:
                file: AtpFileSystemFile = Db.select_by_primary_key(AtpFileSystemFile, project.img)
                project.img = {
                    'id': file.id,
                    'url': get_settings().archive_host + file.name
                }
            else:
                project.img = {
                    'id': 0,
                    'url': 'https://zos.alipayobjects.com/rmsportal/jkjgkEfvpUPVyRjUImniVslZfWPnJuuZ.png'
                }
        session = Db.get_session()
        report_list: List[AtpProjectTestReport] = session.query(AtpProjectTestReport).join(
            AtpProject,
            AtpProject.id == AtpProjectTestReport.project_id
        ).filter(
            AtpProjectTestReport.is_delete == 2,
            AtpProjectTestReport.creator == token_user.user_id,
            AtpProject.is_delete == 2
        ).limit(10).all()
        total_projects_num = Db.select_count_by_condition(AtpProject.id, [AtpProject.is_delete == 2])
        return BaseRes(data={
            'underway_projects': project_list[:6],
            'parted_projects': parted_project_list[:6],
            'my_reports': report_list,
            'total_projects_num': total_projects_num,
            'total_underway_projects_num': len(project_list)
        })
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))
