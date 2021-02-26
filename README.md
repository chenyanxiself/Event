# 从数据库生成models.py文件
    sqlacodegen --outfile models.py mysql+pymysql://root:root@localhost:3306/auto_test_frame
   
# 部署
    pip install -r requirements.ext
    python run.py