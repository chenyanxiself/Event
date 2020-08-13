#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/7/17 10:05 上午
# @Author  : yxChen

from models.response_model.base_resm import BaseRes
from models.db_model.model import AtpProject, SysUser, AtpProjectMember
from models.db_model.db import Db
import typing


def verify_project_deleted(id: int):
    project_id = id
    project: AtpProject = Db.select_by_primary_key(AtpProject, project_id)
    if not project:
        return None, BaseRes(status=0, error='项目不存在')
    else:
        if project.is_delete == 1:
            return None, BaseRes(status=0, error='项目不存在')
        else:
            return project, None


def verify_project_filed(id: int):
    project, error = verify_project_deleted(id)
    if error:
        return None, error
    else:
        if project.type == 0:
            return None, BaseRes(status=0, error='项目已归档,无法操作')
        else:
            return project, None


def verify_project_member(user_id: int, project_id: int):
    user: SysUser = Db.select_by_primary_key(SysUser, user_id)
    if not user:
        return None, BaseRes(status=0, error='用户不存在')
    else:
        member_list: typing.List[AtpProjectMember] = Db.select_by_condition(
            AtpProjectMember,
            [AtpProjectMember.project_id == project_id, AtpProjectMember.is_delete == 2]
        )
        is_memeber = False
        for member_item in member_list:
            if member_item.member_id == user.id:
                is_memeber = True
                break
        if is_memeber:
            return True, None
        else:
            return None, BaseRes(status=0, error='非项目成员无权操作')


def verify_project_owner(user_id: int, project_id: int):
    res, error = verify_project_member(user_id, project_id)
    if error:
        return None, error
    else:
        project: AtpProject = Db.select_by_primary_key(AtpProject, project_id)
        if project.creator == user_id:
            return True, None
        else:
            return None, BaseRes(status=0, error='非项目负责人无权操作')
