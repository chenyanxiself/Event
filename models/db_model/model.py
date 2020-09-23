# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Integer, String, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class AtpProject(Base):
    __tablename__ = 'atp_project'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(50, 'utf8mb4_bin'), nullable=False, comment='项目名称')
    remark = Column(String(200, 'utf8mb4_bin'), comment='项目简介')
    type = Column(TINYINT, server_default=text("'1'"), comment='项目类型 1 进行中 0 已归档')
    url = Column(String(500, 'utf8mb4_bin'), comment='项目封面')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class AtpProjectApiCase(Base):
    __tablename__ = 'atp_project_api_case'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(50, 'utf8mb4_bin'), nullable=False, comment='用例名称')
    method = Column(TINYINT, nullable=False, comment='请求方式 1 get 2 post')
    project_id = Column(BigInteger, nullable=False, comment='项目id')
    request_path = Column(String(200, 'utf8mb4_bin'), comment='请求路径')
    is_use_env = Column(TINYINT, server_default=text("'0'"), comment='是否使用环境 1:使用,0:不使用')
    env_host = Column(BigInteger, comment='环境id')
    request_host = Column(String(200, 'utf8mb4_bin'), comment='请求域名')
    request_headers = Column(String(300, 'utf8mb4_bin'), comment='请求头部')
    request_query = Column(String(300, 'utf8mb4_bin'), comment='请求参数')
    request_body = Column(String(300, 'utf8mb4_bin'), comment='请求主体')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class AtpProjectApiSuite(Base):
    __tablename__ = 'atp_project_api_suite'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(50, 'utf8mb4_bin'), nullable=False, comment='测试集名称')
    project_id = Column(BigInteger, nullable=False, comment='项目id')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class AtpProjectApiSuiteCaseRelation(Base):
    __tablename__ = 'atp_project_api_suite_case_relation'

    id = Column(BigInteger, primary_key=True)
    case_id = Column(BigInteger, nullable=False, comment='用例id')
    suite_id = Column(BigInteger, nullable=False, comment='测试集id')
    project_id = Column(BigInteger, nullable=False, comment='项目id')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))
    sort = Column(Integer, nullable=False, comment='排序')


class AtpProjectCase(Base):
    __tablename__ = 'atp_project_case'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(50, 'utf8mb4_bin'), nullable=False, comment='用例名')
    module_id = Column(BigInteger, nullable=False, comment='模块id')
    project_id = Column(BigInteger, nullable=False, comment='项目id')
    priority = Column(TINYINT, nullable=False, comment='1 低 2 中 3 高 4 最高')
    precondition = Column(String(500, 'utf8mb4_bin'), comment='前置条件')
    remark = Column(String(500, 'utf8mb4_bin'), comment='备注')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class AtpProjectCaseStep(Base):
    __tablename__ = 'atp_project_case_step'

    id = Column(BigInteger, primary_key=True)
    case_id = Column(BigInteger, nullable=False, comment='用例id')
    step = Column(String(255, 'utf8mb4_bin'), comment='步骤描述')
    exception = Column(String(255, 'utf8mb4_bin'), comment='预期结果')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class AtpProjectEnv(Base):
    __tablename__ = 'atp_project_env'

    id = Column(BigInteger, primary_key=True)
    host = Column(String(200, 'utf8mb4_bin'), nullable=False, comment='域名')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))
    name = Column(String(50, 'utf8mb4_bin'), nullable=False, comment='环境名')
    project_id = Column(BigInteger, nullable=False, comment='项目id')


class AtpProjectMember(Base):
    __tablename__ = 'atp_project_member'

    id = Column(BigInteger, primary_key=True)
    project_id = Column(BigInteger, nullable=False, comment='项目id')
    member_id = Column(BigInteger, nullable=False, comment='成员id')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class AtpProjectModule(Base):
    __tablename__ = 'atp_project_module'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(50, 'utf8mb4_bin'), nullable=False, comment='模块名')
    parent_id = Column(BigInteger, nullable=False, comment='父级id')
    project_id = Column(BigInteger, nullable=False, comment='项目id')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class AtpProjectTestReport(Base):
    __tablename__ = 'atp_project_test_report'

    id = Column(BigInteger, primary_key=True)
    report_name = Column(String(50, 'utf8mb4_bin'), nullable=False, comment='报告名')
    global_headers = Column(String(300, 'utf8mb4_bin'), comment='全局请求头部')
    global_host = Column(String(300, 'utf8mb4_bin'), comment='全局域名')
    is_save_cookie = Column(TINYINT, server_default=text("'1'"), comment='是否保存cookie 0 否 1 是')
    total_case_num = Column(Integer, nullable=False, comment='所有测试用例数')
    success_case_num = Column(Integer, server_default=text("'0'"), comment='成功测试用例数')
    failed_case_num = Column(Integer, server_default=text("'0'"), comment='失败测试用例数')
    status = Column(TINYINT, server_default=text("'0'"), comment='0 未开始 1 进行中 2 完成')
    project_id = Column(BigInteger, nullable=False, comment='项目id')
    suite_id = Column(BigInteger, nullable=False, comment='测试集id')
    start_time = Column(DateTime, comment='开始时间')
    finish_time = Column(DateTime, comment='结束时间')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class AtpProjectTestReportDetail(Base):
    __tablename__ = 'atp_project_test_report_detail'

    id = Column(BigInteger, primary_key=True)
    report_id = Column(BigInteger, nullable=False, comment='测试报告id')
    case_id = Column(BigInteger, nullable=False, comment='用例id')
    status = Column(Integer, nullable=False, server_default=text("'200'"), comment='响应状态码')
    response = Column(String(10000, 'utf8mb4_bin'), comment='接口返回值')
    is_success = Column(TINYINT, server_default=text("'1'"), comment='是否请求成功 0 否 1 是')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class SysMenu(Base):
    __tablename__ = 'sys_menus'

    id = Column(BigInteger, primary_key=True)
    menu_path = Column(String(50, 'utf8mb4_bin'), nullable=False, comment='菜单路径')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class SysRole(Base):
    __tablename__ = 'sys_role'

    id = Column(BigInteger, primary_key=True)
    role_name = Column(String(50, 'utf8mb4_bin'), nullable=False, comment='角色名称')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class SysRoleMenu(Base):
    __tablename__ = 'sys_role_menus'

    id = Column(BigInteger, primary_key=True)
    role_id = Column(BigInteger, nullable=False, comment='角色id')
    menu_id = Column(BigInteger, nullable=False, comment='菜单id')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class SysUser(Base):
    __tablename__ = 'sys_user'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(50, 'utf8mb4_bin'), nullable=False, comment='用户名')
    password = Column(String(200, 'utf8mb4_bin'), nullable=False, comment='密码')
    cname = Column(String(50, 'utf8mb4_bin'), nullable=False, comment='用户昵称')
    email = Column(String(50, 'utf8mb4_bin'), comment='邮箱')
    phone = Column(String(50, 'utf8mb4_bin'), comment='手机号码')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class SysUserRole(Base):
    __tablename__ = 'sys_user_role'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False, comment='用户id')
    role_id = Column(BigInteger, nullable=False, comment='角色id')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))
# if __name__ == '__main__':
#     from models.db_model.db import engine
#     Base.metadata.create_all(engine)