#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/11 6:30 下午
# @Author  : yxChen


import sqlalchemy
from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy.ext.declarative import declarative_base
from typing import List
from sqlalchemy import func
from config.settings import get_settings

# DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/auto_test_frame"
mysql_config = get_settings().mysql_config
DATABASE_URL = f"mysql+pymysql://{mysql_config['username']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}"
engine = sqlalchemy.create_engine(DATABASE_URL,pool_recycle=60)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()


class Db:
    @classmethod
    def select_by_condition(
            cls, model: Base, condition: list, order_by=None, offset: int = None, limit: int = None
    ) -> List[Base]:
        session = SessionLocal()
        res = session.query(model).filter(*condition).order_by(order_by).offset(offset).limit(limit).all()
        session.close()
        return res

    @classmethod
    def select_count_by_condition(
            cls, attribute, condition: list, order_by=None, offset: int = None, limit: int = None
    ) -> int:
        session = SessionLocal()
        res = session.query(func.count(attribute)).filter(*condition).order_by(order_by).offset(offset).limit(
            limit).all()
        session.close()
        return res[0][0]

    @classmethod
    def select_by_primary_key(cls, model: Base, id: int) -> Base:
        session = SessionLocal()
        res = session.query(model).get(id)
        session.close()
        return res

    @classmethod
    def update_by_condition(cls, model: Base, condition: list, value: dict) -> int:
        session = SessionLocal()
        update_count = session.query(model).filter(*condition).update(value)
        session.commit()
        session.close()
        return update_count

    @classmethod
    def insert(cls, model: Base):
        session = SessionLocal()
        session.add(model)
        session.commit()
        session.close()

    @classmethod
    def insert_by_transaction(cls, models: List[Base]):
        session = SessionLocal()
        for model in models:
            session.add(model)
        session.commit()
        session.close()


    @classmethod
    def get_session(cls) -> Session:
        return SessionLocal()


if __name__ == '__main__':
    from models.db_model.model import *
    session = Db.get_session()
    all_relation: List[AtpProjectApiSuiteCaseRelation] = session.query(AtpProjectApiSuiteCaseRelation).filter(
        # AtpProjectApiSuiteCaseRelation.is_delete == 2,
        AtpProjectApiSuiteCaseRelation.suite_id == 8,
    ).order_by(AtpProjectApiSuiteCaseRelation.sort.desc()).all()
    print(all_relation[0])
    all_relation[0].is_delete = 2
    session.commit()

    # all_relation: List[AtpProjectApiSuiteCaseRelation] = session.query(AtpProjectApiSuiteCaseRelation).filter(
    #     # AtpProjectApiSuiteCaseRelation.is_delete == 2,
    #     AtpProjectApiSuiteCaseRelation.suite_id == 8,
    # ).order_by(AtpProjectApiSuiteCaseRelation.sort.desc())
    # print(all_relation[0])
    # session=Db.get_session()
    # test=session.query(SysUser).filter(SysUser.name=='test').first()
    # test.update({SysUser.name:'111'})
    # session.commit()
    # print(test.name)
    # try:
    #     user=SysUser(name='8989',password='1212',cname='1212')
    #     session.add(user)
    #     session.commit()
    #     raise Exception('aa')
    # except:
    #     session.rollback()
    # condition_list: list = [
    #     AtpProjectApiCase.is_delete == 2,
    #     AtpProjectApiCase.project_id == 1
    # ]
    # total: int = Db.select_count_by_condition(AtpProjectApiCase.id, condition_list)
    # print(total)
    # total_projects_num = Db.select_count_by_condition(AtpProject,[])
    # print(total_projects_num)
    # session.commit()
    # print(user.id)
    # print(len(Db.select_by_condition(SysUser, [SysUser.is_delete == 2], SysUser.id, 1,2)))
    # print(Db.select_count_by_condition(SysUser.id, [SysUser.is_delete == 2]))
    # aaa=Db.select_by_primary_key(SysUser, 1)
    # aaa.
    # print(Db.update_by_condition(SysUser, [SysUser.id == 1], {SysUser.cname: '你好'}))
    # print(Db.insert(SysUser(name='admin', password='1234', cname='test')))
