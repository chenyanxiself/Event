# 从数据库生成models.py文件
    sqlacodegen --outfile models.py mysql+pymysql://root:root@localhost:3306/auto_test_frame
   
# 部署
    pip install -r requirements.ext
    本地启动修改config/local.py中数据库配置
    python run.py