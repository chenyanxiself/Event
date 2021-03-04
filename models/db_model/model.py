# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text, text
from sqlalchemy.dialects.mysql import LONGTEXT, TINYINT, VARCHAR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class AtpFileSystemFile(Base):
    __tablename__ = 'atp_file_system_file'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False, comment='文件名')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class AtpOverviewList(Base):
    __tablename__ = 'atp_overview_list'

    id = Column(BigInteger, primary_key=True)
    title = Column(String(100), nullable=False, comment='任务列标题')
    project_id = Column(BigInteger, nullable=False, comment='项目id')
    sort = Column(Integer, nullable=False, comment='排序字段')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class AtpOverviewTask(Base):
    __tablename__ = 'atp_overview_task'

    id = Column(BigInteger, primary_key=True)
    title = Column(String(100), nullable=False, comment='任务标题')
    list_id = Column(BigInteger, nullable=False, comment='任务列id')
    project_id = Column(BigInteger, nullable=False, comment='项目id')
    status = Column(TINYINT, nullable=False, comment='0 未完成 1已完成')
    sort = Column(Integer, nullable=False, comment='排序字段')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    img = Column(Text)
    priority = Column(TINYINT, server_default=text("'3'"))
    follower = Column(Text)
    is_delete = Column(TINYINT, server_default=text("'2'"))
    description = Column(LONGTEXT)


class AtpProject(Base):
    __tablename__ = 'atp_project'

    id = Column(BigInteger, primary_key=True)
    name = Column(VARCHAR(50), nullable=False, comment='项目名称')
    remark = Column(VARCHAR(200), comment='项目简介')
    type = Column(TINYINT, server_default=text("'1'"), comment='项目类型 1 进行中 0 已归档')
    img = Column(VARCHAR(500), comment='项目封面')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class AtpProjectApiCase(Base):
    __tablename__ = 'atp_project_api_case'

    id = Column(BigInteger, primary_key=True)
    name = Column(VARCHAR(50), nullable=False, comment='用例名称')
    method = Column(TINYINT, nullable=False, comment='请求方式 1 get 2 post')
    project_id = Column(BigInteger, nullable=False, comment='项目id')
    request_path = Column(VARCHAR(200), comment='请求路径')
    is_use_env = Column(TINYINT, server_default=text("'0'"), comment='是否使用环境 1:使用,0:不使用')
    env_host = Column(BigInteger, comment='环境id')
    request_host = Column(VARCHAR(200), comment='请求域名')
    request_headers = Column(VARCHAR(300), comment='请求头部')
    request_query = Column(VARCHAR(300), comment='请求参数')
    request_body = Column(VARCHAR(300), comment='请求主体')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class AtpProjectApiSuite(Base):
    __tablename__ = 'atp_project_api_suite'

    id = Column(BigInteger, primary_key=True)
    name = Column(VARCHAR(50), nullable=False, comment='测试集名称')
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
    name = Column(VARCHAR(50), nullable=False, comment='用例名')
    module_id = Column(BigInteger, nullable=False, comment='模块id')
    project_id = Column(BigInteger, nullable=False, comment='项目id')
    priority = Column(TINYINT, nullable=False, comment='1 低 2 中 3 高 4 最高')
    precondition = Column(VARCHAR(500), comment='前置条件')
    remark = Column(VARCHAR(500), comment='备注')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class AtpProjectCaseStep(Base):
    __tablename__ = 'atp_project_case_step'

    id = Column(BigInteger, primary_key=True)
    case_id = Column(BigInteger, nullable=False, comment='用例id')
    step = Column(VARCHAR(255), comment='步骤描述')
    exception = Column(VARCHAR(255), comment='预期结果')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class AtpProjectEnv(Base):
    __tablename__ = 'atp_project_env'

    id = Column(BigInteger, primary_key=True)
    host = Column(VARCHAR(200), nullable=False, comment='域名')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))
    name = Column(VARCHAR(50), nullable=False, comment='环境名')
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
    name = Column(VARCHAR(50), nullable=False, comment='模块名')
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
    report_name = Column(VARCHAR(50), nullable=False, comment='报告名')
    global_headers = Column(VARCHAR(300), comment='全局请求头部')
    global_host = Column(VARCHAR(300), comment='全局域名')
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
    response = Column(VARCHAR(10000), comment='接口返回值')
    is_success = Column(TINYINT, server_default=text("'1'"), comment='是否请求成功 0 否 1 是')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class SysMenu(Base):
    __tablename__ = 'sys_menus'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(20), nullable=False, comment='菜单名')
    menu_path = Column(VARCHAR(50), nullable=False, comment='菜单路径')
    menu_reg = Column(String(50), nullable=False, comment='菜单正则')
    icon = Column(String(10), comment='icon映射名')
    parent_id = Column(Integer, comment='父级菜单')
    creator = Column(BigInteger, comment='创建人id')
    create_time = Column(DateTime, comment='创建时间')
    updator = Column(BigInteger, comment='更新人id')
    update_time = Column(DateTime, comment='创建时间')
    is_delete = Column(TINYINT, server_default=text("'2'"))


class SysRole(Base):
    __tablename__ = 'sys_role'

    id = Column(BigInteger, primary_key=True)
    role_name = Column(VARCHAR(50), nullable=False, comment='角色名称')
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
    name = Column(VARCHAR(50), nullable=False, comment='用户名')
    password = Column(VARCHAR(200), nullable=False, comment='密码')
    cname = Column(VARCHAR(50), nullable=False, comment='用户昵称')
    email = Column(VARCHAR(50), comment='邮箱')
    phone = Column(VARCHAR(50), comment='手机号码')
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
