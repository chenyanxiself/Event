#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/11 5:18 下午
# @Author  : yxChen

import os
import uvicorn
from env_config.settings import get_settings
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from controller.api.user_api import router as user_route
from controller.api.project_api import router as project_route
from controller.api.request_api import router as request_route
from controller.api.project_report_api import router as report_route
from controller.api.project_case_api import router as case_route
from controller.api.workstation_api import router as workstation_route
from controller.api.project_overview_websocket_api import router as overview_route
from controller.api.project_editor_api import router as editor_route
import logging
import traceback


def create_app() -> FastAPI:
    app = FastAPI()
    app.mount('/static', StaticFiles(directory='./static'), name='static')
    app.debug = True

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(
        user_route,
        prefix='/api/v1/user',
        tags=['login'],
    )
    app.include_router(
        project_route,
        prefix='/api/v1/project',
        tags=['project'],
    )
    app.include_router(
        request_route,
        prefix='/api/v1/request',
        tags=['request'],
    )
    app.include_router(
        report_route,
        prefix='/api/v1/project/report',
        tags=['report'],
    )
    app.include_router(
        case_route,
        prefix='/api/v1/project/case',
        tags=['case'],
    )
    app.include_router(
        workstation_route,
        prefix='/api/v1/workstation',
        tags=['workstation'],
    )
    app.include_router(
        overview_route,
        prefix='/api/v1/project/overview',
        tags=['overview'],
    )
    app.include_router(
        editor_route,
        prefix='/api/v1/project/editor',
        tags=['editor'],
    )
    return app


def db_init():
    from models.db_model.db import engine, Db
    from models.db_model.model import Base, SysUser, SysMenu, SysRole, SysRoleMenu,SysUserRole
    from sqlalchemy_utils import database_exists, create_database
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(engine)
    if not database_exists(engine.url):
        session = Db.get_session()
        try:
            admin_user = SysUser(
                name='admin',
                password='$2b$12$CzZv68jyas1POYLBRx14fecZhj4mBNA2da9JqdVRPIvT7r4JBiUJm',
                cname='管理员',
            )
            session.add(admin_user)
            workspace_menu = SysMenu(
                name='我的工作台',
                menu_path='/workspace',
                menu_reg='^\/workspace\/?$',
                icon='workspace'
            )
            session.add(workspace_menu)
            project_menu = SysMenu(
                name='项目',
                menu_path='/project',
                menu_reg='^\/project\/?',
                icon='project'
            )
            session.add(project_menu)
            tool_menu = SysMenu(
                name='工具',
                menu_path='/tool',
                menu_reg='^\/tool\/?',
                icon='tool'
            )
            session.add(tool_menu)
            manage_menu = SysMenu(
                name='管理',
                menu_path='/manage',
                menu_reg='^\/manage\/?$',
                icon='manage'
            )
            session.add(manage_menu)
            session.commit()
            user_manage_menu = SysMenu(
                name='用户管理',
                menu_path='/manage/user',
                menu_reg='^\/manage\/user\/?$',
                parent_id=manage_menu.id
            )
            session.add(user_manage_menu)
            role_manage_menu = SysMenu(
                name='角色管理',
                menu_path='/manage/role',
                menu_reg='^\/manage\/role\/?$',
                parent_id=manage_menu.id
            )
            session.add(role_manage_menu)
            admin_role = SysRole(
                role_name='管理员',
            )
            session.add(admin_role)
            session.commit()
            session.add(SysUserRole(
                user_id=admin_user.id,
                role_id=admin_role.id
            ))
            session.add(SysRoleMenu(
                role_id=admin_role.id,
                menu_id=workspace_menu.id
            ))
            session.add(SysRoleMenu(
                role_id=admin_role.id,
                menu_id=project_menu.id
            ))
            session.add(SysRoleMenu(
                role_id=admin_role.id,
                menu_id=tool_menu.id
            ))
            session.add(SysRoleMenu(
                role_id=admin_role.id,
                menu_id=manage_menu.id
            ))
            session.add(SysRoleMenu(
                role_id=admin_role.id,
                menu_id=user_manage_menu.id
            ))
            session.add(SysRoleMenu(
                role_id=admin_role.id,
                menu_id=role_manage_menu.id
            ))
            session.commit()
        except Exception as e:
            session.rollback()
            logging.error(traceback.format_exc())


def start():
    db_init()
    if not os.path.exists(get_settings().static_path):
        os.mkdir(get_settings().static_path)
    app = create_app()
    uvicorn.run(app, **get_settings().config)
