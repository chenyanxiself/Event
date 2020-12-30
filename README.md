# 从数据库生成models.py文件
    sqlacodegen --outfile models.py mysql+pymysql://root:root@localhost:3306/auto_test_frame
   
# 生成数据库表
    修改config/local.py 中数据库文件
    手动创建数据库database
    cd models/db_model
    python model.py

# 部署
    pip install -r requirements.ext
    python run.py