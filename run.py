#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/11 5:18 下午
# @Author  : yxChen

import os
os.environ['FASTAPI_ENV'] = 'local'
from config.settings import get_settings
if not os.path.exists(get_settings().static_path):
    os.makedirs(get_settings().static_path)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from controller.api.user_api import router as user_route
from controller.api.project_api import router as project_route
from controller.api.request_api import router as request_route
from controller.api.project_report_api import router as report_route
from controller.api.project_case_api import router as case_route
from controller.api.workstation_api import router as workstation_route
from controller.api.project_overview_api import router as overview_route


def create_app() -> FastAPI:
    app = FastAPI()
    app.mount('/static',StaticFiles(directory='./static'),name='static')
    app.debug=True

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
    return app

def start():
    import uvicorn
    app = create_app()
    uvicorn.run(app,**get_settings().config)

if __name__ == '__main__':
    start()