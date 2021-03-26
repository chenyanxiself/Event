#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/7/22 5:17 下午
# @Author  : yxChen


from fastapi import APIRouter, Body, Depends, UploadFile, File, Query
from consts.log_name import API_PROJECT_CASE
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

router = APIRouter()
logger = logging.getLogger(API_PROJECT_CASE)


@router.post('/createModule/', response_model=BaseRes)
async def create_module(
        request: Module,
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_deleted(request.project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, request.project_id)
    if error:
        return error
    try:
        if request.parent_id != 0:
            parent_module: AtpProjectModule = Db.select_by_primary_key(AtpProjectModule, request.parent_id)
            if not parent_module:
                return BaseRes(status=0, error='父模块不存在')
        Db.insert(AtpProjectModule(
            name=request.name,
            parent_id=request.parent_id,
            project_id=request.project_id,
            creator=token_user.user_id,
            create_time=datetime.datetime.now()
        ))
        return BaseRes()
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.get('/getAllModule/', response_model=BaseRes, dependencies=[Depends(auth_token)])
async def get_all_module(
        project_id: int = Query(...)
) -> BaseRes:
    _, error = verify_project_deleted(project_id)
    if error:
        return error
    try:
        return_data: List[AtpProjectModule] = Db.select_by_condition(
            AtpProjectModule,
            [AtpProjectModule.is_delete == 2, AtpProjectModule.project_id == project_id]
        )
        return BaseRes(data=return_data)
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/updateModule/', response_model=BaseRes)
async def update_module(
        request: UpdateModule,
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_deleted(request.project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, request.project_id)
    if error:
        return error
    try:
        Db.update_by_condition(
            AtpProjectModule,
            [AtpProjectModule.is_delete == 2, AtpProjectModule.id == request.id],
            {AtpProjectModule.name: request.name}
        )
        return BaseRes()
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/deleteModule/', response_model=BaseRes)
async def delete_module(
        id_list: List[int] = Body(..., embed=True),
        project_id: int = Body(..., embed=True),
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_deleted(project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, project_id)
    if error:
        return error
    session = Db.get_session()
    try:
        session.query(AtpProjectModule).filter(
            AtpProjectModule.is_delete == 2, AtpProjectModule.id.in_(id_list)
        ).update({
            AtpProjectModule.is_delete: 1
        }, synchronize_session=False)
        session.commit()
        return BaseRes()
    except Exception as e:
        session.rollback()
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/getCaseByModuleId/', response_model=BaseRes, dependencies=[Depends(auth_token)])
async def get_case_by_module_id(
        project_id: int = Body(..., embed=True),
        module_id: int = Body(None, embed=True),
        keyword: str = Body(None, embed=True)
) -> BaseRes:
    _, error = verify_project_deleted(project_id)
    if error:
        return error
    condition = [
        AtpProjectCase.is_delete == 2, AtpProjectCase.project_id == project_id
    ]
    if module_id:
        condition.append(AtpProjectCase.module_id == module_id)
    if keyword:
        condition.append(AtpProjectCase.name.like(f'%{keyword}%'))
    try:
        case_list: List[AtpProjectCase] = Db.select_by_condition(
            AtpProjectCase,
            condition,
            AtpProjectCase.id.desc()
        )
        index = 1
        for case in case_list:
            case.index = index
            index += 1
            case.steps = Db.select_by_condition(
                AtpProjectCaseStep,
                [AtpProjectCaseStep.is_delete == 2, AtpProjectCaseStep.case_id == case.id]
            )
            case.cname = Db.select_by_primary_key(SysUser, case.creator).cname
            case.module_name = Db.select_by_primary_key(AtpProjectModule, case.module_id).name
        return BaseRes(data=case_list)
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.get('/getCaseById/', response_model=BaseRes, dependencies=[Depends(auth_token)])
async def get_case_by_id(
        id: int = Query(...),
        project_id: int = Query(...),
) -> BaseRes:
    _, error = verify_project_deleted(project_id)
    if error:
        return error
    session = Db.get_session()
    try:
        case: AtpProjectCase = session.query(AtpProjectCase).filter(*[
            AtpProjectCase.is_delete == 2,
            AtpProjectCase.id == id
        ]).first()
        create_user: SysUser = session.query(SysUser).filter(*[
            SysUser.is_delete == 2,
            SysUser.id == case.creator
        ]).first()
        module_list: List[AtpProjectModule] = session.query(AtpProjectModule).filter(*[
            AtpProjectModule.is_delete == 2,
            AtpProjectModule.project_id == project_id
        ]).all()
        module_breakcrumb = []
        target_module: AtpProjectModule or None = None
        for i in module_list:
            if case.module_id == i.id:
                target_module = i
        module_breakcrumb.append(target_module.name)
        steps: List[AtpProjectCaseStep] = session.query(AtpProjectCaseStep).filter(*[
            AtpProjectCaseStep.is_delete == 2,
            AtpProjectCaseStep.case_id == id
        ]).all()
        while True:
            if not target_module.parent_id:
                break
            m: AtpProjectModule = session.query(AtpProjectModule).filter(*[
                AtpProjectModule.is_delete == 2,
                AtpProjectModule.id == target_module.parent_id
            ]).first()
            target_module = m
            module_breakcrumb.append(m.name)
        return BaseRes(data={
            'id': case.id,
            'name': case.name,
            'modules': module_breakcrumb,
            'priority': case.priority,
            'precondition': case.precondition,
            'remark': case.remark,
            'steps': steps,
            'creator':create_user.cname
        })
    except Exception as e:
        session.rollback()
        logger.error(traceback.format_exc())
        return BaseRes(status=0, error=str(e))
    finally:
        session.close()


@router.post('/createProjectCase/', response_model=BaseRes)
async def create_project_case(
        request: ProjectCase,
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_filed(request.project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, request.project_id)
    if error:
        return error
    session = Db.get_session()
    try:
        case = AtpProjectCase(
            name=request.name,
            module_id=request.module_id,
            project_id=request.project_id,
            priority=request.priority,
            precondition=request.precondition,
            remark=request.remark,
            creator=token_user.user_id,
            create_time=datetime.datetime.now()
        )
        session.add(case)
        session.commit()
        for step in request.steps:
            session.add(AtpProjectCaseStep(
                case_id=case.id,
                step=step.step,
                exception=step.exception,
                creator=token_user.user_id,
                create_time=datetime.datetime.now()
            ))
        session.commit()
        return BaseRes()
    except Exception as e:
        session.rollback()
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/updateProjectCase/', response_model=BaseRes)
async def update_project_case(
        request: UpdateProjectCase,
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_filed(request.project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, request.project_id)
    if error:
        return error
    session = Db.get_session()
    now_time = datetime.datetime.now()
    try:
        session.query(AtpProjectCase).filter(
            AtpProjectCase.is_delete == 2,
            AtpProjectCase.id == request.id
        ).update({
            AtpProjectCase.name: request.name,
            AtpProjectCase.priority: request.priority,
            AtpProjectCase.precondition: request.precondition,
            AtpProjectCase.remark: request.remark,
            AtpProjectCase.module_id: request.module_id,
            AtpProjectCase.updator: token_user.user_id,
            AtpProjectCase.update_time: now_time
        })
        current_step_ids = []
        for step in request.steps:
            if step.id:
                current_step_ids.append(step.id)
                session.query(AtpProjectCaseStep).filter(
                    AtpProjectCaseStep.is_delete == 2,
                    AtpProjectCaseStep.id == step.id
                ).update({
                    AtpProjectCaseStep.step: step.step,
                    AtpProjectCaseStep.exception: step.exception,
                    AtpProjectCaseStep.updator: token_user.user_id,
                    AtpProjectCaseStep.update_time: now_time
                })
            else:
                session.add(AtpProjectCaseStep(
                    case_id=request.id,
                    step=step.step,
                    exception=step.exception,
                    creator=token_user.user_id,
                    create_time=now_time
                ))
        session.query(AtpProjectCaseStep).filter(
            AtpProjectCaseStep.is_delete == 2,
            AtpProjectCaseStep.id.notin_(current_step_ids)
        ).update({
            AtpProjectCaseStep.is_delete: 1,
            AtpProjectCaseStep.updator: token_user.user_id,
            AtpProjectCaseStep.update_time: now_time
        }, synchronize_session=False)
        session.commit()
        return BaseRes()
    except Exception as e:
        session.rollback()
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/deleteProjectCase/', response_model=BaseRes)
async def create_project_case(
        project_id: int = Body(..., embed=True),
        case_id_list: List[int] = Body(..., embed=True),
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_filed(project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, project_id)
    if error:
        return error
    session = Db.get_session()
    now_time = datetime.datetime.now()
    try:
        session.query(AtpProjectCase).filter(
            AtpProjectCase.is_delete == 2,
            AtpProjectCase.id.in_(case_id_list)
        ).update({
            AtpProjectCase.is_delete: 1,
            AtpProjectCase.updator: token_user.user_id,
            AtpProjectCase.update_time: now_time
        }, synchronize_session=False)
        session.query(AtpProjectCaseStep).filter(
            AtpProjectCaseStep.is_delete == 2,
            AtpProjectCaseStep.case_id.in_(case_id_list)
        ).update({
            AtpProjectCaseStep.is_delete: 1,
            AtpProjectCaseStep.updator: token_user.user_id,
            AtpProjectCaseStep.update_time: now_time
        }, synchronize_session=False)
        session.commit()
        return BaseRes()
    except Exception as e:
        session.rollback()
        logger.error(e)
        return BaseRes(status=0, error=str(e))
