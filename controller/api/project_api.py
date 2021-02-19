#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/17 6:43 下午
# @Author  : yxChen


from fastapi import APIRouter, Body, Depends, UploadFile, File, Query, BackgroundTasks
from consts.log_name import API_PROJECT
from models.response_model.base_resm import BaseRes
from models.db_model.model import *
from models.db_model.db import Db
from models.request_model.user_reqm import TokenUser
from models.request_model.project_reqm import *
from util.jwt_util import auth_token
import logging, hashlib, time, os, datetime, json
from config.settings import get_settings
from typing import List, Optional
from util.request_util import execute_suite_request
from sqlalchemy import or_
from copy import deepcopy
from util.project_verify import verify_project_deleted, verify_project_filed, verify_project_member, \
    verify_project_owner

router = APIRouter()
logger = logging.getLogger(API_PROJECT)


@router.post('/createProject/', response_model=BaseRes)
async def create_project(
        create_project: Project,
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    user_id = token_user.user_id
    session = Db.get_session()
    try:
        project: AtpProject = AtpProject(
            name=create_project.project_name,
            remark=create_project.project_desc,
            type=1,
            img=create_project.project_img,
            creator=user_id,
            create_time=datetime.datetime.now()
        )
        session.add(project)
        session.commit()
        project_id = project.id
        for member_id in create_project.project_member:
            member: AtpProjectMember = AtpProjectMember(
                project_id=project_id,
                member_id=member_id,
                creator=user_id,
                create_time=datetime.datetime.now()
            )
            session.add(member)
        session.commit()
        return BaseRes()
    except Exception as e:
        logger.error(e)
        session.rollback()
        return BaseRes(status=0, error=str(e))


@router.get('/getAllProject/', response_model=BaseRes, dependencies=[Depends(auth_token)])
async def get_all_project(type: int = Query(...)) -> BaseRes:
    try:
        project_list: List[AtpProject] = Db.select_by_condition(
            AtpProject,
            [AtpProject.is_delete == 2, AtpProject.type == type]
        )
        for project in project_list:
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
        return BaseRes(data=project_list)
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.get('/getProjectById/', response_model=BaseRes, dependencies=[Depends(auth_token)])
async def get_project_id(id: int = Query(...)) -> BaseRes:
    _, error = verify_project_deleted(id)
    if error:
        return error
    try:
        project: AtpProject = Db.select_by_primary_key(AtpProject, id)
        member_relation_list: List[AtpProjectMember] = Db.select_by_condition(
            AtpProjectMember,
            [
                AtpProjectMember.project_id == id,
                AtpProjectMember.is_delete == 2
            ]
        )
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
        project.member = []
        for member_relation in member_relation_list:
            user: SysUser = Db.select_by_primary_key(SysUser, member_relation.member_id)
            project.member.append({
                'id': user.id,
                'cname': user.cname,
            })
        return BaseRes(data=project)
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/updateProjectById/', response_model=BaseRes)
async def update_project_id(
        project: UpdateProject,
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_filed(project.id)
    if error:
        return error
    _, error = verify_project_owner(token_user.user_id, project.id)
    if error:
        return error
    session = Db.get_session()
    try:
        session.query(AtpProject).filter(AtpProject.id == project.id, AtpProject.is_delete == 2).update(
            {
                AtpProject.name: project.project_name,
                AtpProject.remark: project.project_desc,
                AtpProject.updator: token_user.user_id,
                AtpProject.update_time: datetime.datetime.now()
            }
        )
        new_member_id_list = project.project_member
        old_memeber_id_list = []
        items: List[AtpProjectMember] = session.query(AtpProjectMember).filter(
            AtpProjectMember.is_delete == 2,
            AtpProjectMember.project_id == project.id
        ).all()
        for item in items:
            old_memeber_id_list.append(item.member_id)
        added_member = set(new_member_id_list) - set(old_memeber_id_list)
        lost_member = set(old_memeber_id_list) - set(new_member_id_list)
        for add_member_id in added_member:
            instance = session.query(AtpProjectMember).filter(
                AtpProjectMember.project_id == project.id,
                AtpProjectMember.member_id == add_member_id,
                AtpProjectMember.is_delete == 1
            )
            if instance.first():
                instance.update({
                    AtpProjectMember.is_delete: 2,
                    AtpProjectMember.updator: token_user.user_id,
                    AtpProjectMember.update_time: datetime.datetime.now()
                })
            else:
                session.add(AtpProjectMember(
                    project_id=project.id,
                    member_id=add_member_id,
                    creator=token_user.user_id,
                    create_time=datetime.datetime.now()
                ))
        if len(lost_member) != 0:
            session.query(AtpProjectMember).filter(
                AtpProjectMember.is_delete == 2,
                AtpProjectMember.project_id == project.id,
                AtpProjectMember.member_id.in_(list(lost_member))) \
                .update({
                AtpProjectMember.is_delete: 1,
                AtpProjectMember.updator: token_user.user_id,
                AtpProjectMember.update_time: datetime.datetime.now()
            }, synchronize_session=False)
        session.commit()
        return BaseRes(data=project)
    except Exception as e:
        session.rollback()
        logger.error(e)
        return BaseRes(status=0, error=str(e))
    finally:
        session.close()


@router.post('/updateProjectType', response_model=BaseRes)
async def update_project_type(
        id: int = Body(..., embed=True),
        project_type: int = Body(..., embed=True),
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_deleted(id)
    if error:
        return error
    _, error = verify_project_owner(token_user.user_id, id)
    if error:
        return error
    try:
        count = Db.update_by_condition(
            AtpProject,
            [AtpProject.id == id, AtpProject.is_delete == 2],
            {
                AtpProject.type: project_type,
                AtpProject.updator: token_user.user_id,
                AtpProject.update_time: datetime.datetime.now()
            }
        )
        return BaseRes(data=count)
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/updateProjectEnv', response_model=BaseRes)
async def update_project_env(
        env_info: UpdateProjectEnv,
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_filed(env_info.project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, env_info.project_id)
    if error:
        return error
    try:
        Db.update_by_condition(
            AtpProjectEnv,
            [AtpProjectEnv.is_delete == 2, AtpProjectEnv.id == env_info.id],
            {
                AtpProjectEnv.host: env_info.env_host,
                AtpProjectEnv.name: env_info.env_name,
                AtpProjectEnv.updator: token_user.user_id,
                AtpProjectEnv.update_time: datetime.datetime.now()
            }
        )
        return BaseRes()
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/createProjectEnv', response_model=BaseRes)
async def create_project_env(
        env_info: ProjectEnv,
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_filed(env_info.project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, env_info.project_id)
    if error:
        return error
    try:
        Db.insert(
            AtpProjectEnv(
                name=env_info.env_name,
                host=env_info.env_host,
                project_id=env_info.project_id,
                creator=token_user.user_id,
                create_time=datetime.datetime.now()
            )
        )
        return BaseRes()
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/deleteProjectEnv', response_model=BaseRes)
async def delete_project_env(
        id: int = Body(..., embed=True),
        project_id: int = Body(..., embed=True),
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
        session.query(AtpProjectEnv).filter(AtpProjectEnv.is_delete == 2, AtpProjectEnv.id == id).update(
            {
                AtpProjectEnv.is_delete: 1,
                AtpProjectEnv.updator: token_user.user_id,
                AtpProjectEnv.update_time: datetime.datetime.now()
            }
        )
        session.query(AtpProjectApiCase).filter(
            AtpProjectApiCase.is_delete == 2,
            AtpProjectApiCase.project_id == project_id,
            AtpProjectApiCase.env_host == id
        ).update({
            AtpProjectApiCase.env_host: None
        })
        session.commit()
        return BaseRes()
    except Exception as e:
        session.rollback()
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/deleteProject', response_model=BaseRes)
async def delete_project(
        id: int = Body(..., embed=True),
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_deleted(id)
    if error:
        return error
    _, error = verify_project_owner(token_user.user_id, id)
    if error:
        return error
    try:
        count = Db.update_by_condition(
            AtpProject,
            [AtpProject.id == id, AtpProject.is_delete == 2],
            {
                AtpProject.is_delete: 1,
                AtpProject.updator: token_user.user_id,
                AtpProject.update_time: datetime.datetime.now()
            }
        )
        return BaseRes(data=count)
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/deleteApiCaseById/', response_model=BaseRes)
async def delete_api_case_by_id(
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
            AtpProjectApiCase,
            [
                AtpProjectApiCase.id == id,
                AtpProjectApiCase.is_delete == 2,
            ],
            {
                AtpProjectApiCase.is_delete: 1,
                AtpProjectApiCase.updator: token_user.user_id,
                AtpProjectApiCase.update_time: datetime.datetime.now()
            }
        )
        return BaseRes(data=update_count)
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.get('/getApiCaseByCondition/', response_model=BaseRes, dependencies=[Depends(auth_token)])
async def get_api_case_by_condition(
        project_id: int = Query(...),
        page_num: int = Query(...),
        page_size: int = Query(...),
        type: int = Query(...),
        keyword: Optional[str] = Query(None)
) -> BaseRes:
    _, error = verify_project_deleted(project_id)
    if error:
        return error
    try:
        if page_num == 0 and page_size == 0:
            offset = None
            limit = None
        else:
            offset = page_size * (page_num - 1)
            limit = page_size
        condition_list: list = [
            AtpProjectApiCase.is_delete == 2,
            AtpProjectApiCase.project_id == project_id
        ]
        if keyword and keyword != '':
            condition_list.append(AtpProjectApiCase.name.like(f'%{keyword}%'))
        if type in [1, 2]:
            condition_list.append(AtpProjectApiCase.method == type)
        api_case_list: List[AtpProjectApiCase] = Db.select_by_condition(
            AtpProjectApiCase,
            condition_list,
            AtpProjectApiCase.id,
            offset,
            limit
        )
        total: int = Db.select_count_by_condition(AtpProjectApiCase.id, condition_list)
        res_list: list = []
        order_id = page_size * (page_num - 1)
        for item in api_case_list:
            item_dict: dict = {}
            order_id += 1
            item_dict.setdefault('id', item.id)
            item_dict.setdefault('order_id', order_id)
            item_dict.setdefault('name', item.name)
            item_dict.setdefault('method', item.method)
            item_dict.setdefault('is_use_env', item.is_use_env)
            item_dict.setdefault('request_host', item.request_host)
            item_dict.setdefault('env_host', item.env_host)
            item_dict.setdefault('request_path', item.request_path)
            item_dict.setdefault('request_headers', json.loads(item.request_headers))
            item_dict.setdefault('request_query', json.loads(item.request_query))
            item_dict.setdefault('request_body', json.loads(item.request_body))
            if item.is_use_env:
                if item.env_host:
                    env: AtpProjectEnv = Db.select_by_primary_key(AtpProjectEnv, item.env_host)
                    item_dict.setdefault('real_host', env.host)
                else:
                    item_dict.setdefault('real_host', None)
            else:
                item_dict.setdefault('real_host', item.request_host)
            res_list.append(item_dict)
        return BaseRes(data={'data': res_list, 'total': total})
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.get('/getEnvByProjectId/', response_model=BaseRes, dependencies=[Depends(auth_token)])
async def get_env_by_project_id(project_id: int = Query(...)) -> BaseRes:
    _, error = verify_project_deleted(project_id)
    if error:
        return error
    try:
        env_list: List[AtpProjectEnv] = Db.select_by_condition(AtpProjectEnv,
                                                               [AtpProjectEnv.is_delete == 2,
                                                                AtpProjectEnv.project_id == project_id])
        return BaseRes(data=env_list)
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/uploadProjectImg/', response_model=BaseRes)
async def upload_project_img(
        projectImg: UploadFile = File(...),
        project_id=Body(None, embed=True),
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
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
        if project_id:
            _, error = verify_project_filed(project_id)
            if error:
                return error
            _, error = verify_project_owner(token_user.user_id, project_id)
            if error:
                return error

            session.query(AtpProject) \
                .filter(*[AtpProject.id == project_id, AtpProject.is_delete == 2]) \
                .update({
                # AtpProject.img: 'http://localhost:8900/static/' + filename,
                AtpProject.img: file.id,
                AtpProject.updator: token_user.user_id,
                AtpProject.update_time: datetime.datetime.now()
            })
            session.commit()
        return BaseRes(data={'id': file.id, 'fileName': filename, 'url': get_settings().archive_host




                                                                         + filename})
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/delProjectImg/', response_model=BaseRes)
async def del_project_img(
        file_id: int = Body(..., embed=True),
        task_id: int = Body(None, embed=True),
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    session = Db.get_session()
    file: AtpFileSystemFile = session.query(AtpFileSystemFile).get(file_id)
    if not file:
        return BaseRes(status=0, error='file not found')
    file_path = get_settings().static_path + file.name
    if not os.path.exists(file_path):
        return BaseRes(status=0, error='file not found')
    os.remove(file_path)
    if task_id:
        task: AtpOverviewTask = session.query(AtpOverviewTask).get(task_id)
        _, error = verify_project_filed(task.projectId)
        if error:
            return error
        _, error = verify_project_member(token_user.user_id, task.projectId)
        if error:
            return error
        img_list = json.loads(task.img)
        img_list.remove(file_id)
        task.img = json.dumps(img_list)
        session.commit()
    return BaseRes()


@router.post('/createProjectApiCase/', response_model=BaseRes)
async def create_project_api_case(
        project_api_case: ProjectApiCase,
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_filed(project_api_case.project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, project_api_case.project_id)
    if error:
        return error
    try:
        request_headers: str = json.dumps(project_api_case.request_headers)
        request_query: str = json.dumps(project_api_case.request_query)
        request_body: str = json.dumps(project_api_case.request_body)
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error='json转换异常 : ' + str(e))
    atp_project_api_case: AtpProjectApiCase = AtpProjectApiCase(
        name=project_api_case.name,
        method=project_api_case.request_method,
        project_id=project_api_case.project_id,
        request_path=project_api_case.request_path,
        is_use_env=project_api_case.request_host.is_user_env,
        env_host=project_api_case.request_host.env_host,
        request_host=project_api_case.request_host.request_host,
        request_headers=request_headers,
        request_query=request_query,
        request_body=request_body,
        creator=token_user.user_id,
        create_time=datetime.datetime.now()
    )
    try:
        Db.insert(atp_project_api_case)
        return BaseRes()
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/updateProjectApiCase/', response_model=BaseRes)
async def update_project_api_case(
        update_project_api_case: UpdateProjectApiCase,
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_filed(update_project_api_case.project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, update_project_api_case.project_id)
    if error:
        return error
    try:
        request_headers: str = json.dumps(update_project_api_case.request_headers)
        request_query: str = json.dumps(update_project_api_case.request_query)
        request_body: str = json.dumps(update_project_api_case.request_body)
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))
    try:
        db_res: int = Db.update_by_condition(
            AtpProjectApiCase,
            [
                AtpProjectApiCase.id == update_project_api_case.id,
                AtpProjectApiCase.is_delete == 2
            ],
            {
                AtpProjectApiCase.name: update_project_api_case.name,
                AtpProjectApiCase.method: update_project_api_case.request_method,
                AtpProjectApiCase.project_id: update_project_api_case.project_id,
                AtpProjectApiCase.request_path: update_project_api_case.request_path,
                AtpProjectApiCase.is_use_env: update_project_api_case.request_host.is_user_env,
                AtpProjectApiCase.env_host: update_project_api_case.request_host.env_host,
                AtpProjectApiCase.request_host: update_project_api_case.request_host.request_host,
                AtpProjectApiCase.request_headers: request_headers,
                AtpProjectApiCase.request_query: request_query,
                AtpProjectApiCase.request_body: request_body,
                AtpProjectApiCase.updator: token_user.user_id,
                AtpProjectApiCase.update_time: datetime.datetime.now()
            }
        )
        return BaseRes(data=db_res)
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.get('/getSuiteByProjectId/', response_model=BaseRes, dependencies=[Depends(auth_token)])
async def get_suite_by_project_id(project_id: int = Query(...)) -> BaseRes:
    _, error = verify_project_deleted(project_id)
    if error:
        return error
    suite_list: List[AtpProjectApiSuite] = Db.select_by_condition(
        AtpProjectApiSuite,
        [AtpProjectApiSuite.is_delete == 2, AtpProjectApiSuite.project_id == project_id]
    )
    res_list: list = []
    for suite in suite_list:
        item = {
            'id': suite.id,
            'name': suite.name,
            'project_id': suite.project_id,
        }
        res_list.append(item)
    return BaseRes(data=res_list)


@router.get('/getSuiteInfoById/', response_model=BaseRes, dependencies=[Depends(auth_token)])
async def get_suite_info_by_id(id: int = Query(...), project_id: int = Query(...)) -> BaseRes:
    _, error = verify_project_deleted(project_id)
    if error:
        return error
    try:
        case_list: List[AtpProjectApiSuiteCaseRelation] = Db.select_by_condition(
            AtpProjectApiSuiteCaseRelation,
            [AtpProjectApiSuiteCaseRelation.project_id == project_id, AtpProjectApiSuiteCaseRelation.is_delete == 2,
             AtpProjectApiSuiteCaseRelation.suite_id == id],
            AtpProjectApiSuiteCaseRelation.sort
        )
        # suite_info: AtpProjectApiSuite = Db.select_by_primary_key(AtpProjectApiSuite, id)
        return BaseRes(data=case_list)
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))
    # condition_list: list = [
    #     AtpProjectApiCase.is_delete == 2,
    #     AtpProjectApiCase.project_id == project_id
    # ]
    # try:
    #     api_case_list: List[AtpProjectApiCase] = Db.select_by_condition(
    #         AtpProjectApiCase,
    #         condition_list,
    #         AtpProjectApiCase.id,
    #     )
    # except Exception as e:
    #     logger.error(e)
    #     return BaseRes(status=0, error=str(e))
    # total_case_list: list = []
    # order_id = 0
    # for item in api_case_list:
    #     item_dict: dict = {}
    #     order_id += 1
    #     item_dict.setdefault('id', item.id)
    #     item_dict.setdefault('order_id', order_id)
    #     item_dict.setdefault('name', item.name)
    #     item_dict.setdefault('method', item.method)
    #     item_dict.setdefault('is_use_env', item.is_use_env)
    #     item_dict.setdefault('request_host', item.request_host)
    #     item_dict.setdefault('env_host', item.env_host)
    #     item_dict.setdefault('request_path', item.request_path)
    #     item_dict.setdefault('request_headers', json.loads(item.request_headers))
    #     item_dict.setdefault('request_query', json.loads(item.request_query))
    #     item_dict.setdefault('request_body', json.loads(item.request_body))
    #     if item.is_use_env:
    #         env: AtpProjectEnv = Db.select_by_primary_key(AtpProjectEnv, item.env_host)
    #         item_dict.setdefault('real_host', env.host)
    #     else:
    #         item_dict.setdefault('real_host', item.request_host)
    #     total_case_list.append(item_dict)
    # return BaseRes(data={
    #     'id': suite_info.id,
    #     'suite_name': suite_info.name,
    #     'total_case_list': total_case_list,
    #     'relation': case_list,
    # })


@router.post('/createSuite/', response_model=BaseRes)
async def create_suite(
        project_id: int = Body(..., embed=True), suite_name: str = Body(..., embed=True),
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_filed(project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, project_id)
    if error:
        return error
    suite = AtpProjectApiSuite(name=suite_name, project_id=project_id, creator=token_user.user_id,
                               create_time=datetime.datetime.now())
    try:
        Db.insert(suite)
        return BaseRes()
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/deleteSuite/', response_model=BaseRes)
async def delete_suite(
        suite_id: int = Body(..., embed=True),
        project_id: int = Body(..., embed=True),
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_filed(project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, project_id)
    if error:
        return error
    try:
        count = Db.update_by_condition(AtpProjectApiSuite, [AtpProjectApiSuite.id == suite_id],
                                       {
                                           AtpProjectApiSuite.is_delete: 1,
                                           AtpProjectApiSuite.updator: token_user.user_id,
                                           AtpProjectApiSuite.update_time: datetime.datetime.now()
                                       })
        return BaseRes(data=count)
    except Exception as e:
        logger.error(e)
        return BaseRes(status=0, error=str(e))


@router.post('/updateSuiteCaseRelation/', response_model=BaseRes)
async def update_suite_case_relation(
        suite_id: int = Body(..., embed=True),
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
    try:
        all_relation: List[AtpProjectApiSuiteCaseRelation] = session.query(AtpProjectApiSuiteCaseRelation).filter(
            # AtpProjectApiSuiteCaseRelation.is_delete == 2,
            AtpProjectApiSuiteCaseRelation.suite_id == suite_id,
        ).order_by(AtpProjectApiSuiteCaseRelation.case_id).all()
        current_case_id_list = []
        for relation in all_relation:
            if relation.is_delete == 2:
                current_case_id_list.append(relation.case_id)
        remove_case_id_list = list(set(current_case_id_list) - set(case_id_list))
        new_add_case_id_list = list(set(case_id_list) - set(current_case_id_list))
        new_add_case_id_list.sort()

        def filter_relation(arg: AtpProjectApiSuiteCaseRelation):
            start_sort = 90000
            if arg.case_id in remove_case_id_list:
                arg.is_delete = 1
                return False
            if arg.case_id in new_add_case_id_list:
                new_add_case_id_list.remove(arg.case_id)
                arg.is_delete = 2
                arg.sort = start_sort
                start_sort += 1
                return True
            return True

        filtered_all_relation: List[AtpProjectApiSuiteCaseRelation] = list(filter(filter_relation, all_relation))

        for new_add_case_id in new_add_case_id_list:
            new_obj = AtpProjectApiSuiteCaseRelation(
                case_id=new_add_case_id,
                suite_id=suite_id,
                project_id=project_id,
                creator=token_user.user_id,
                create_time=datetime.datetime.now(),
                sort=99999
            )
            filtered_all_relation.append(new_obj)
            session.add(new_obj)

        filtered_all_relation.sort(key=lambda x: x.sort)
        for i, v in enumerate(filtered_all_relation):
            v.sort = i + 1
        session.commit()
        return BaseRes()
    except Exception as e:
        session.rollback()
        logger.error(e)
        return BaseRes(status=0, error=str(e))
    finally:
        session.close()


@router.post('/updateSuiteCaseSort/', response_model=BaseRes)
async def update_suite_case_sort(
        before_id: int = Body(..., embed=True),
        after_id: int = Body(..., embed=True),
        project_id: int = Body(..., embed=True),
        suite_id: int = Body(..., embed=True),
        type: int = Body(..., embed=True),
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
        all_relation: List[AtpProjectApiSuiteCaseRelation] = session.query(AtpProjectApiSuiteCaseRelation).filter(
            AtpProjectApiSuiteCaseRelation.is_delete == 2,
            AtpProjectApiSuiteCaseRelation.suite_id == suite_id
        ).order_by(AtpProjectApiSuiteCaseRelation.sort).all()
        before_index = None
        after_index = None
        for index, relation in enumerate(all_relation):
            if relation.case_id == before_id:
                before_index = index
            if relation.case_id == after_id:
                after_index = index
        if type == 1:
            temp = all_relation[before_index]
            del all_relation[before_index]
            temp.sort = all_relation[after_index].sort
            all_relation.insert(after_index, temp)
            for i, v in enumerate(all_relation[after_index + 1:]):
                v.sort = i + after_index + 2
        elif type == 2:
            temp = all_relation[before_index]
            del all_relation[before_index]
            all_relation.insert(after_index, temp)
            for i, v in enumerate(all_relation[before_index:]):
                v.sort = i + before_index + 1
        session.commit()
        return BaseRes()
    except Exception as e:
        session.rollback()
        logger.error(e)
        return BaseRes(status=0, error=str(e))
    finally:
        session.close()


@router.post('/executeSuite/', response_model=BaseRes)
async def execute_suite(
        request: ExecuteSuite,
        background_tasks: BackgroundTasks,
        token_user: TokenUser = Depends(auth_token)
) -> BaseRes:
    _, error = verify_project_deleted(request.project_id)
    if error:
        return error
    _, error = verify_project_member(token_user.user_id, request.project_id)
    if error:
        return error
    if request.is_use_env and request.env_host:
        env_db_res: AtpProjectEnv = Db.select_by_primary_key(AtpProjectEnv, request.env_host)
        global_host = env_db_res.host
    else:
        if request.request_host:
            global_host = request.request_host
        else:
            global_host = ''
    case_relation: List[AtpProjectApiSuiteCaseRelation] = Db.select_by_condition(
        AtpProjectApiSuiteCaseRelation,
        [
            AtpProjectApiSuiteCaseRelation.project_id == request.project_id,
            AtpProjectApiSuiteCaseRelation.suite_id == request.suite_id,
            AtpProjectApiSuiteCaseRelation.is_delete == 2,
        ],
        AtpProjectApiSuiteCaseRelation.sort
    )
    request_list = []
    for item in case_relation:
        case: AtpProjectApiCase = Db.select_by_primary_key(AtpProjectApiCase, item.case_id)
        case_item = {
            'case_id': case.id,
            'suite_id': request.suite_id,
            'path': case.request_path,
            'params': json.loads(case.request_query),
            'body': json.loads(case.request_body),
            'method': 'Get' if case.method == 1 else 'Post'
        }
        if global_host:
            case_item.setdefault('host', global_host)
        else:
            if case.is_use_env:
                request_host_item: AtpProjectEnv = Db.select_by_primary_key(
                    AtpProjectEnv,
                    case.env_host)
                case_item.setdefault('host', request_host_item.host)
            else:
                case_item.setdefault('host', case.request_host)
        request_headers = json.loads(deepcopy(case.request_headers))
        if request_headers is None:
            request_headers = {}
        if request.global_headers:
            request_headers.update(request.global_headers)
            case_item.setdefault('headers', request_headers)
        else:
            case_item.setdefault('headers', request_headers)
        request_list.append(case_item)
    session = Db.get_session()
    try:
        report = AtpProjectTestReport(
            report_name=str(int(time.time())),
            global_headers=json.dumps(request.global_headers) if request.global_headers else None,
            global_host=global_host if global_host else None,
            is_save_cookie=request.is_save_cookie,
            total_case_num=len(request_list),
            status=0,
            project_id=request.project_id,
            suite_id=request.suite_id,
            start_time=datetime.datetime.now(),
            creator=token_user.user_id,
            create_time=datetime.datetime.now(),
        )
        session.add(report)
        session.commit()
        report_id = report.id
    except Exception as e:
        session.rollback()
        logger.error(e)
        return BaseRes(status=0, error=str(e))
    finally:
        session.close()
    fun_arg = {
        'request_list': request_list,
        'report_id': report_id
    }
    background_tasks.add_task(execute_suite_request, **fun_arg)
    return BaseRes()


@router.post('/test')
async def test(
        id: bool = Body(..., embed=True)
):
    print(id)
