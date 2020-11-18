# 从数据库生成models.py文件
    sqlacodegen --outfile models.py mysql+pymsql://root:root@localhost:3306/auto-test-frame
   
# 生成数据库表
    在model.py文件下调用
    from models.db_model.db import engine
        Base.metadata.create_all(engine)