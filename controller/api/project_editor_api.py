#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/17 6:43 下午
# @Author  : yxChen


from fastapi import APIRouter, Body, Depends, UploadFile, File, Query, BackgroundTasks
from consts.log_name import API_EDITOR
from models.response_model.base_resm import BaseRes
from models.db_model.model import *
from models.db_model.db import Db
from models.request_model.user_reqm import TokenUser
from models.request_model.project_reqm import *
from util.jwt_util import auth_token
import logging, hashlib, time, os, datetime, json
from env_config.settings import get_settings
from typing import List, Optional, Any
from util.project_verify import verify_project_deleted, verify_project_filed, verify_project_member, \
    verify_project_owner
import traceback
from sqlalchemy import func

router = APIRouter()
logger = logging.getLogger(API_EDITOR)


@router.get('/getAllEditor/', response_model=BaseRes)
async def get_all_editor(
        project_id: int = Query(...),
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_deleted(project_id)
    if error:
        return error
    session = Db.get_session()
    try:
        editors: List[AtpProjectEditor] = session.query(AtpProjectEditor).filter(*[
            AtpProjectEditor.is_delete == 2,
            AtpProjectEditor.project_id == project_id
        ]).order_by(AtpProjectEditor.update_time.desc()).all()
        return BaseRes(data=editors)
    except Exception as e:
        logger.error(traceback.format_exc())
        return BaseRes(status=0, error=str(e))
    finally:
        session.close()


@router.get('/getEditorById/', response_model=BaseRes)
async def get_editor(
        id: int = Query(...),
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    session = Db.get_session()
    try:
        editor: AtpProjectEditor = session.query(AtpProjectEditor).get(id)
        if not editor:
            return BaseRes(status=0, error="Can't find editor by the id: " + str(id))
        _, error = verify_project_deleted(editor.project_id)
        if error:
            return error
        return BaseRes(data=editor)
    except Exception as e:
        logger.error(traceback.format_exc())
        return BaseRes(status=0, error=str(e))
    finally:
        session.close()


@router.post('/updateEditor/', response_model=BaseRes)
async def update_editor(
        id: int = Body(..., embed=True),
        project_id: int = Body(..., embed=True),
        title: str = Body(None, embed=True),
        data: str = Body(None, embed=True),
        is_delete: int = Body(None, embed=True),
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
        editor: AtpProjectEditor = session.query(AtpProjectEditor).get(id)
        editor.updator = token_user.user_id
        editor.update_time = datetime.datetime.now()
        if is_delete:
            editor.is_delete = is_delete
        if title:
            editor.title = title
        if data:
            editor.data = data
        session.commit()
        return BaseRes(data={'id': id})
    except Exception as e:
        logger.error(traceback.format_exc())
        return BaseRes(status=0, error=str(e))
    finally:
        session.close()


@router.post('/createEditor/', response_model=BaseRes)
async def update_editor(
        project_id: int = Body(..., embed=True),
        title: str = Body(..., embed=True),
        type: int = Body(..., embed=True),
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
        editor = AtpProjectEditor(
            project_id=project_id,
            title=title,
            type=type,
            creator=token_user.user_id,
            create_time=datetime.datetime.now(),
            updator=token_user.user_id,
            update_time=datetime.datetime.now()
        )
        session.add(editor)
        session.commit()
        return BaseRes(data={'id': editor.id})
    except Exception as e:
        logger.error(traceback.format_exc())
        return BaseRes(status=0, error=str(e))
    finally:
        session.close()
