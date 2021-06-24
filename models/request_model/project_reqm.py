#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/18 2:48 下午
# @Author  : yxChen


from pydantic import BaseModel
from fastapi import Body
from typing import List
from models.request_model.request_reqm import ApiCase
from .request_reqm import Args


class DelProject(BaseModel):
    user_id: int
    user_cname: str


class Project(BaseModel):
    project_name: str = Body(...)
    project_desc: str = Body(None)
    project_img: int = Body(None)
    project_member: List[int] = Body(...)


class UpdateProject(Project):
    id: int = Body(...)


class ProjectApiCase(ApiCase):
    name: str = Body(...)
    project_id: int = Body(...)
    suite_id:int=Body(...)


class UpdateProjectApiCase(ProjectApiCase):
    id: int = Body(...)


class ProjectEnv(BaseModel):
    project_id: int = Body(...)
    env_name: str = Body(...)
    env_host: str = Body(...)


class UpdateProjectEnv(ProjectEnv):
    id: int = Body(...)


class ExecuteSuite(BaseModel):
    project_id: int = Body(...)
    suite_id: int = Body(...)
    is_use_env: bool = Body(...)
    request_host: str = Body(None)
    env_host: int = Body(None)
    is_save_cookie: bool = Body(...)
    global_headers: dict = Body(None)


class Module(BaseModel):
    name: str = Body(...)
    parent_id: int = Body(...)
    project_id: int = Body(...)


class UpdateModule(Module):
    id: int = Body(...)


class CaseStep(BaseModel):
    id: int = Body(None)
    case_id: int = Body(None)
    step: str = Body(None)
    exception: str = Body(None)


class ProjectCase(BaseModel):
    name: str = Body(...)
    module_id: int = Body(...)
    project_id: int = Body(...)
    priority: int = Body(...)
    precondition: str = Body(None)
    remark: str = Body(None)
    steps: List[CaseStep] = Body(None)

class UpdateProjectCase(ProjectCase):
    id:int=Body(...)
