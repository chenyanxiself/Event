#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/17 6:43 下午
# @Author  : yxChen


from fastapi import APIRouter, Body, Depends, UploadFile, File, Query, BackgroundTasks
from fastapi.websockets import WebSocketDisconnect, WebSocket
from consts.log_name import API_OVERVIEW
from models.response_model.base_resm import BaseRes, BaseWebsocketRes
from models.db_model.model import *
from models.db_model.db import Db
from models.request_model.user_reqm import TokenUser
from models.request_model.project_reqm import *
from util.jwt_util import auth_token, auth_websocket_token
import logging, hashlib, time, os, datetime, json
from env_config.settings import get_settings
from typing import List, Optional, Any
from util.project_verify import verify_project_deleted, verify_project_filed, verify_project_member, \
    verify_project_owner
import traceback
from sqlalchemy import func
from fastapi.encoders import jsonable_encoder

router = APIRouter()
logger = logging.getLogger(API_OVERVIEW)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/projectOverview")
async def websocket_project_overview(
        websocket: WebSocket,
        token_user: Optional[TokenUser] = Depends(auth_websocket_token)
):
    if not token_user:
        return
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if json.loads(data).get('type') == 'getTaskByCondition':
                res = await get_task_by_condition(23, '', 1, 0, token_user)
            elif json.loads(data).get('type') == 'getProjectProgress':
                pass
            elif json.loads(data).get('type') == 'deleteTaskList':
                pass
            elif json.loads(data).get('type') == 'deleteTask':
                pass
            elif json.loads(data).get('type') == 'updateList':
                pass
            elif json.loads(data).get('type') == 'updateTask':
                pass
            elif json.loads(data).get('type') == 'updateListSort':
                pass
            elif json.loads(data).get('type') == 'updateTaskSort':
                pass
            elif json.loads(data).get('type') == 'createTask':
                pass
            elif json.loads(data).get('type') == 'createList':
                pass
            elif json.loads(data).get('type') == 'uploadTaskImg':
                pass
            elif json.loads(data).get('type') == 'getTaskDetail':
                pass
            else:
                pass
            await manager.broadcast(jsonable_encoder(res))
    except AttributeError as e:
        await manager.send_personal_message(str(e), websocket)
        await websocket.close()
        manager.disconnect(websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.get('/getTaskByCondition/', response_model=BaseRes)
async def get_task_by_condition(
        project_id: int = Query(...),
        keyword: str = Query(None),
        relation_type: int = Query(...),
        filter_type: int = Query(...),
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_deleted(project_id)
    if error:
        return error
    try:
        task_list_condition: list = [
            AtpOverviewList.is_delete == 2,
            AtpOverviewList.project_id == project_id
        ]
        task_list: List[AtpOverviewList] = Db.select_by_condition(AtpOverviewList, task_list_condition,
                                                                  AtpOverviewList.sort)
        for l in task_list:
            task_condition: list = [
                AtpOverviewTask.is_delete == 2,
                AtpOverviewTask.project_id == project_id,
                AtpOverviewTask.list_id == l.id
            ]
            if keyword:
                task_condition.append(AtpOverviewTask.title.like(f'%{keyword}%'))
            if filter_type in [1, 2]:
                task_condition.append(AtpOverviewTask.status == filter_type)
            if relation_type == 2:
                task_condition.append(AtpOverviewTask.creator == token_user.user_id)
            tasks: List[AtpOverviewTask] = Db.select_by_condition(AtpOverviewTask, task_condition, AtpOverviewTask.sort)
            # 根据条件找出所有符合条件的, 再筛选我关注的
            if relation_type == 3:
                target_tasks = []
                for t in tasks:
                    if token_user.user_id in json.loads(t.follower):
                        target_tasks.append(t)
                tasks = target_tasks
            l.taskList = tasks
            for t in tasks:
                user: SysUser = Db.select_by_primary_key(SysUser, int(str(t.creator)))
                t.creator = {
                    'id': user.id if user else 0,
                    'cname': user.cname if user else ''
                }
            l.taskList = tasks
        return BaseRes(data=task_list)
    except Exception as e:
        logger.error(traceback.format_exc())
        return BaseRes(status=0, error=str(e))


@router.get('/getProjectProgress/', response_model=BaseRes, dependencies=[Depends(auth_token)])
async def get_project_progress(
        project_id: int = Query(...)
) -> BaseRes:
    _, error = verify_project_deleted(project_id)
    if error:
        return error
    try:
        finish_count = Db.select_count_by_condition(AtpOverviewTask.id, [
            AtpOverviewTask.is_delete == 2,
            AtpOverviewTask.project_id == project_id,
            AtpOverviewTask.status == 1
        ])
        total_count = Db.select_count_by_condition(AtpOverviewTask.id, [
            AtpOverviewTask.is_delete == 2,
            AtpOverviewTask.project_id == project_id,
        ])
        return BaseRes(data={
            'total': total_count,
            'finish': finish_count
        })
    except Exception as e:
        logger.error(traceback.format_exc())
        return BaseRes(status=0, error=str(e))


@router.post('/deleteTaskList/', response_model=BaseRes)
async def delete_task_list(
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
        delete_item: AtpOverviewList = session.query(AtpOverviewList).get(id)
        if delete_item:
            delete_item.is_delete = 1
            delete_item.updator = token_user.user_id,
            delete_item.update_time = datetime.datetime.now()
            session.query(AtpOverviewList).filter(*[
                AtpOverviewList.project_id == delete_item.project_id,
                AtpOverviewList.sort > delete_item.sort,
                AtpOverviewList.is_delete == 2
            ]).update(
                {
                    AtpOverviewList.sort: AtpOverviewList.sort - 1,
                    AtpOverviewList.updator: token_user.user_id,
                    AtpOverviewList.update_time: datetime.datetime.now()
                })
            session.query(AtpOverviewTask).filter(*[
                AtpOverviewTask.list_id == id,
                AtpOverviewTask.is_delete == 2
            ]).update(
                {
                    AtpOverviewTask.is_delete: 1,
                    AtpOverviewTask.updator: token_user.user_id,
                    AtpOverviewTask.update_time: datetime.datetime.now()
                })
            session.commit()
        return BaseRes()
    except Exception as e:
        session.rollback()
        logger.error(traceback.format_exc())
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
            delete_item.is_delete = 1
            delete_item.updator = token_user.user_id,
            delete_item.update_time = datetime.datetime.now()
            session.query(AtpOverviewTask).filter(*[
                AtpOverviewTask.project_id == delete_item.project_id,
                AtpOverviewTask.list_id == delete_item.list_id,
                AtpOverviewTask.sort > delete_item.sort,
                AtpOverviewTask.is_delete == 2
            ]).update(
                {
                    AtpOverviewTask.sort: AtpOverviewTask.sort - 1,
                    AtpOverviewTask.updator: token_user.user_id,
                    AtpOverviewTask.update_time: datetime.datetime.now()
                })
            session.commit()
        return BaseRes()
    except Exception as e:
        session.rollback()
        logger.error(traceback.format_exc())
        return BaseRes(status=0, error=str(e))
    finally:
        session.close()


@router.post('/updateList/', response_model=BaseRes)
async def update_task(
        project_id: int = Body(..., embed=True),
        list_id: int = Body(..., embed=True),
        title: str = Body(..., embed=True),
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_filed(project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, project_id)
    if error:
        return error
    try:
        exists_condition = [
            AtpOverviewList.is_delete == 2,
            AtpOverviewList.project_id == project_id,
            AtpOverviewList.title == title,
            AtpOverviewList.id != list_id
        ]
        count = Db.select_count_by_condition(AtpOverviewList.id, exists_condition)
        if count != 0:
            return BaseRes(status=0, error='任务栏标题已存在')
        condition = [
            AtpOverviewList.id == list_id,
            AtpOverviewList.is_delete == 2,
        ]
        Db.update_by_condition(AtpOverviewList, condition, {
            AtpOverviewList.title: title,
            AtpOverviewList.updator: token_user.user_id,
            AtpOverviewList.update_time: datetime.datetime.now()
        })
        return BaseRes()
    except Exception as e:
        logger.error(traceback.format_exc())
        return BaseRes(status=0, error=str(e))


@router.post('/updateTask/', response_model=BaseRes)
async def update_task(
        project_id: int = Body(..., embed=True),
        task_id: int = Body(..., embed=True),
        value: Any = Body(..., embed=True),
        key: str = Body(..., embed=True),
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
        session.query(AtpOverviewTask).filter(*[
            AtpOverviewTask.id == task_id,
            AtpOverviewTask.is_delete == 2
        ]).update({
            getattr(AtpOverviewTask, key): value,
            AtpOverviewTask.updator: token_user.user_id,
            AtpOverviewTask.update_time: datetime.datetime.now()
        })
        session.commit()
        return BaseRes()
    except Exception as e:
        session.rollback()
        logger.error(traceback.format_exc())
        return BaseRes(status=0, error=str(e))
    finally:
        session.close()


@router.post('/updateListSort/', response_model=BaseRes)
async def update_list_sort(
        project_id: int = Body(..., embed=True),
        start_index: int = Body(..., embed=True),
        end_index: int = Body(..., embed=True),
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
        target_list_columns: List[AtpOverviewList] = session.query(AtpOverviewList).filter(*[
            AtpOverviewList.is_delete == 2,
            AtpOverviewList.project_id == project_id,
        ]).order_by(AtpOverviewList.sort).all()
        new_sort = target_list_columns[end_index].sort
        if start_index < end_index:
            for i in target_list_columns[start_index + 1:end_index + 1]:
                i.sort -= 1
        else:
            for i in target_list_columns[end_index:start_index]:
                i.sort += 1
        target_list_columns[start_index].sort = new_sort
        session.commit()
        return BaseRes()
    except Exception as e:
        session.rollback()
        logger.error(traceback.format_exc())
        return BaseRes(status=0, error=str(e))
    finally:
        session.close()


@router.post('/updateTaskSort/', response_model=BaseRes)
async def update_task_sort(
        project_id: int = Body(..., embed=True),
        start_list_id: int = Body(..., embed=True),
        end_list_id: int = Body(..., embed=True),
        id: int = Body(..., embed=True),
        before_id: int = Body(None, embed=True),
        after_id: int = Body(None, embed=True),
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
        source_task: AtpOverviewTask = session.query(AtpOverviewTask).get(id)
        before_task: AtpOverviewTask or None = None
        after_task: AtpOverviewTask or None = None
        if before_id:
            before_task = session.query(AtpOverviewTask).get(before_id)
        if after_id:
            after_task = session.query(AtpOverviewTask).get(after_id)
        start_list: AtpOverviewList = session.query(AtpOverviewList).get(start_list_id)
        end_list: AtpOverviewList = session.query(AtpOverviewList).get(end_list_id)
        if not (start_list and end_list):
            return BaseRes()
        if start_list_id == end_list_id:
            target_task_columns: List[AtpOverviewTask] = session.query(AtpOverviewTask).filter(*[
                AtpOverviewTask.is_delete == 2,
                AtpOverviewList.project_id == project_id,
                AtpOverviewTask.list_id == end_list_id
            ]).order_by(AtpOverviewTask.sort).all()
            if after_task:
                if source_task.sort < after_task.sort:
                    new_sort = after_task.sort - 1
                    temp_list = [x for x in target_task_columns if source_task.sort < x.sort < after_task.sort]
                    for i in temp_list:
                        i.sort -= 1
                else:
                    new_sort = after_task.sort
                    for i in [x for x in target_task_columns if after_task.sort <= x.sort < source_task.sort]:
                        i.sort += 1
            else:
                # start<end并且end为最后一个
                new_sort = target_task_columns[-1].sort
                temp_list = [x for x in target_task_columns if
                             source_task.sort < x.sort < target_task_columns[-1].sort + 1]
                for i in temp_list:
                    i.sort -= 1
            source_task.sort = new_sort
        else:
            start_task_columns: List[AtpOverviewTask] = session.query(AtpOverviewTask).filter(*[
                AtpOverviewTask.is_delete == 2,
                AtpOverviewList.project_id == project_id,
                AtpOverviewTask.list_id == start_list_id
            ]).order_by(AtpOverviewTask.sort).all()
            end_task_columns: List[AtpOverviewTask] = session.query(AtpOverviewTask).filter(*[
                AtpOverviewTask.is_delete == 2,
                AtpOverviewList.project_id == project_id,
                AtpOverviewTask.list_id == end_list_id
            ]).order_by(AtpOverviewTask.sort).all()
            for i in [x for x in start_task_columns if x.sort > source_task.sort]:
                i.sort -= 1
            if after_task and before_task:
                new_sort = after_task.sort
                for i in [x for x in end_task_columns if x.sort >= after_task.sort]:
                    i.sort += 1
            elif after_task and not before_task:
                new_sort = after_task.sort
                for i in [x for x in end_task_columns if x.sort >= after_task.sort]:
                    i.sort += 1
            elif before_task and not after_task:
                new_sort = before_task.sort + 1
                for i in [x for x in end_task_columns if x.sort > before_task.sort]:
                    i.sort += 1
            else:
                new_sort = 1
                init_sort = 2
                for i in end_task_columns:
                    i.sort = init_sort
                    init_sort += 1
            source_task.sort = new_sort
            source_task.list_id = end_list_id
        session.commit()
        return BaseRes()
    except Exception as e:
        session.rollback()
        logger.error(traceback.format_exc())
        return BaseRes(status=0, error=str(e))
    finally:
        session.close()


@router.post('/createList/', response_model=BaseRes)
async def create_list(
        project_id: int = Body(..., embed=True),
        title: str = Body(..., embed=True),
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
        exists_condition = [
            AtpOverviewList.is_delete == 2,
            AtpOverviewList.project_id == project_id,
            AtpOverviewList.title == title
        ]
        count = session.query(func.count(AtpOverviewList.id)).filter(*exists_condition).all()[0][0]
        if count != 0:
            return BaseRes(status=0, error='任务栏标题已存在')
        max_sort_item = session.query(func.max(AtpOverviewList.sort)).filter(*[
            AtpOverviewList.is_delete == 2,
            AtpOverviewList.project_id == project_id
        ]).first()
        if max_sort_item[0]:
            max_sort = max_sort_item[0] + 1
        else:
            max_sort = 1
        session.add(AtpOverviewList(
            title=title,
            project_id=project_id,
            sort=max_sort,
            creator=token_user.user_id,
            create_time=datetime.datetime.now(),
            is_delete=2
        ))
        session.commit()
        return BaseRes()
    except Exception as e:
        session.rollback()
        logger.error(traceback.format_exc())
        return BaseRes(status=0, error=str(e))
    finally:
        session.close()


@router.post('/createTask/', response_model=BaseRes)
async def create_list(
        project_id: int = Body(..., embed=True),
        list_id: int = Body(..., embed=True),
        title: str = Body(..., embed=True),
        priority: int = Body(..., embed=True),
        follower: List[int] = Body(..., embed=True),
        description: str = Body(None, embed=True),
        attachment: List[int] = Body(..., embed=True),
        relevance_case: List[int] = Body(..., embed=True),
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
        max_sort_item = session.query(func.max(AtpOverviewTask.sort)).filter(*[
            AtpOverviewTask.is_delete == 2,
            AtpOverviewTask.project_id == project_id,
            AtpOverviewTask.list_id == list_id
        ]).first()
        if max_sort_item[0]:
            max_sort = max_sort_item[0] + 1
        else:
            max_sort = 1
        session.add(AtpOverviewTask(
            title=title,
            project_id=project_id,
            sort=max_sort,
            description=description,
            priority=priority,
            follower=json.dumps(follower),
            img=json.dumps(attachment),
            relevance_case=json.dumps(relevance_case),
            list_id=list_id,
            status=2,
            creator=token_user.user_id,
            create_time=datetime.datetime.now(),
            is_delete=2
        ))
        session.commit()
        return BaseRes()
    except Exception as e:
        session.rollback()
        logger.error(traceback.format_exc())
        return BaseRes(status=0, error=str(e))
    finally:
        session.close()


@router.post('/uploadTaskImg/', response_model=BaseRes)
async def upload_task_img(
        projectImg: UploadFile = File(...),
        project_id=Body(..., embed=True),
        task_id=Body(None, embed=True),
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_filed(project_id)
    if error:
        return error
    _, error = verify_project_owner(token_user.user_id, project_id)
    if error:
        return error
    encrypt_filename: str = hashlib.md5((projectImg.filename + str(time.time())).encode()).hexdigest()
    suffix = projectImg.content_type.split('/')[1]
    filename = encrypt_filename + '.' + suffix
    try:
        with open(get_settings().static_path + filename, 'wb+') as f:
            f.write(await projectImg.read())
        session = Db.get_session()
        file = AtpFileSystemFile(
            name=filename,
            creator=token_user.user_id,
            create_time=datetime.datetime.now()
        )
        session.add(file)
        session.commit()
        if task_id:
            task: AtpOverviewTask = session.query(AtpOverviewTask).get(task_id)
            file_ids = json.loads(task.img) if task.img else []
            file_ids.append(file.id)
            task.img = json.dumps(file_ids)
        session.commit()
        return BaseRes(data={'fileName': filename, 'id': file.id, 'url': get_settings().archive_host + filename})
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.get('/getTaskDetail/', response_model=BaseRes)
async def get_task_detail(
        project_id: int = Query(...),
        task_id: int = Query(...),
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_deleted(project_id)
    if error:
        return error
    session = Db.get_session()
    try:
        task: AtpOverviewTask = session.query(AtpOverviewTask).get(task_id)
        followers: List[SysUser] = session.query(SysUser).filter(*[
            SysUser.is_delete == 2,
            SysUser.id.in_(json.loads(task.follower))
        ]).all()
        imgs: List[AtpFileSystemFile] = session.query(AtpFileSystemFile).filter(*[
            AtpFileSystemFile.is_delete == 2,
            AtpFileSystemFile.id.in_(json.loads(task.img))
        ]).all()
        cases: List[AtpProjectCase] = session.query(AtpProjectCase).filter(*[
            AtpProjectCase.is_delete == 2,
            AtpProjectCase.id.in_(json.loads(task.relevance_case))
        ]).all()
        img_list = []
        for i in imgs:
            img_list.append({
                'id': i.id,
                'name': i.name,
                'url': get_settings().archive_host + i.name
            })
        task.follower = followers
        task.img = img_list
        task.relevance_case = cases
        return BaseRes(data=task)
    except Exception as e:
        logger.error(traceback.format_exc())
        return BaseRes(status=0, error=str(e))
