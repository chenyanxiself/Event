#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/17 6:43 下午
# @Author  : yxChen


from fastapi import APIRouter, Body, Depends, UploadFile, File, Query, BackgroundTasks
from consts.log_name import API_OVERVIEW
from models.response_model.base_resm import BaseRes
from models.db_model.model import *
from models.db_model.db import Db
from models.request_model.user_reqm import TokenUser
from models.request_model.project_reqm import *
from util.jwt_util import auth_token
import logging, hashlib, time, os, datetime, json
from config.settings import get_settings
from typing import List, Optional
from util.project_verify import verify_project_deleted, verify_project_filed, verify_project_member, \
    verify_project_owner

router = APIRouter()
logger = logging.getLogger(API_OVERVIEW)


@router.get('/getTaskByCondition/', response_model=BaseRes, dependencies=[Depends(auth_token)])
async def get_task_by_condition(
        project_id: int = Query(...),
        keyword: str = Query(None),
        type: int = Query(default=None),
) -> BaseRes:
    _, error = verify_project_deleted(project_id)
    if error:
        return error
    try:
        task_list_condition: list = [
            AtpOverviewList.isDelete == 2,
            AtpOverviewList.projectId == project_id
        ]
        task_list: List[AtpOverviewList] = Db.select_by_condition(AtpOverviewList, task_list_condition,
                                                                  AtpOverviewList.sort)
        for l in task_list:
            task_condition: list = [
                AtpOverviewTask.isDelete == 2,
                AtpOverviewTask.projectId == project_id,
                AtpOverviewTask.listId == l.id
            ]
            if keyword:
                task_condition.append(AtpOverviewTask.title.like(f'%{keyword}%'))
            if type in [0, 1]:
                task_condition.append(AtpOverviewTask.status == type)
            tasks: List[AtpOverviewTask] = Db.select_by_condition(AtpOverviewTask, task_condition, AtpOverviewTask.sort)
            l.taskList = tasks
            for t in tasks:
                user: SysUser = Db.select_by_primary_key(SysUser, int(t.creator))
                t.creator = {
                    'id': user.id if user else 0,
                    'cname': user.cname if user else ''
                }
            l.taskList = tasks
        return BaseRes(data=task_list)
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/deleteTaskList/', response_model=BaseRes)
async def get_task_by_condition(
        project_id: int = Body(..., embed=True),
        id: int = Body(..., embed=True),
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_filed(project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, project_id)
    if error:
        return error
    try:
        Db.update_by_condition(AtpOverviewList, [AtpOverviewList.id == id], {
            AtpOverviewList.isDelete: 1,
            AtpOverviewList.updator: token_user.user_id,
            AtpOverviewList.updateTime: datetime.datetime.now()
        })
        return BaseRes()
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/deleteTask/', response_model=BaseRes)
async def delete_task(
        project_id: int = Body(..., embed=True),
        id: int = Body(..., embed=True),
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_filed(project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, project_id)
    if error:
        return error
    session = Db.get_session()
    try:
        delete_item: AtpOverviewTask = session.query(AtpOverviewTask).get(id)
        if delete_item:
            delete_item.isDelete = 1
            delete_item.updator = token_user.user_id,
            delete_item.updateTime = datetime.datetime.now()
            session.query(AtpOverviewTask).filter(AtpOverviewTask.sort > delete_item.sort).update(
                {
                    AtpOverviewTask.sort: AtpOverviewTask.sort - 1,
                    AtpOverviewTask.updator: token_user.user_id,
                    AtpOverviewTask.updateTime: datetime.datetime.now()
                })
            session.commit()
        return BaseRes()
    except Exception as e:
        session.rollback()
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/updateListSort/', response_model=BaseRes)
async def delete_task(
        project_id: int = Body(..., embed=True),
        start_id: int = Body(..., embed=True),
        end_id: int = Body(..., embed=True),
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_filed(project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, project_id)
    if error:
        return error
    session = Db.get_session()
    try:
        print(start_id)
        print(end_id)
        start_list: AtpOverviewList = session.query(AtpOverviewList).get(start_id)
        end_list: AtpOverviewList = session.query(AtpOverviewList).get(end_id)

        if start_list and end_list:
            temp = start_list.sort
            start_list.sort = end_list.sort
            end_list.sort = temp
            session.commit()
        return BaseRes()
    except Exception as e:
        session.rollback()
        logger.error(e)
        return BaseRes(status=0, error=str(e))
