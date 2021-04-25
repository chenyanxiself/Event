<p align="center">
   <img alt="Logo" height="64" src="https://github.com/chenyanxiself/Event/blob/master/docs/ic-logo.png">
</p>
<h1 align="center">Event</h1>

<div align="center">

轻量级项目协作,测试集成一体化,丰富工具集成.

[![antd](https://img.shields.io/badge/antd-^4.0.0-blue.svg?style=flat-square)](https://github.com/ant-design/ant-design)
[![umi](https://img.shields.io/badge/umi-^2.2.1-orange.svg?style=flat-square)](https://github.com/umijs/umi)
[![fastapi](https://img.shields.io/badge/fastapi-^0.58.0-green.svg?style=flat-square)](https://github.com/tiangolo/fastapi)

</div>

- 在线demo - [https://antd-admin.zuiidea.com](https://antd-admin.zuiidea.com)


## 特性

- 轻量级项目协作

<p align="center">
   <img alt="overview" height="64" src="https://github.com/chenyanxiself/Event/blob/master/docs/overview.png">
</p>

- 测试用例集成项目管理
<p align="center">
   <img alt="case" height="64" src="https://github.com/chenyanxiself/Event/blob/master/docs/case.png">
</p>

- 接口测试
<p align="center">
   <img alt="apicase" height="64" src="https://github.com/chenyanxiself/Event/blob/master/docs/apicase.png">
</p>

- 接口测试报告
<p align="center">
   <img alt="testreport" height="64" src="https://github.com/chenyanxiself/Event/blob/master/docs/testreport.png">
</p>

- 在线编辑脑图、流程图
<p align="center">
   <img alt="editor" height="64" src="https://github.com/chenyanxiself/Event/blob/master/docs/editor.png">
</p>

- 常用工具集成
<p align="center">
   <img alt="tools" height="64" src="https://github.com/chenyanxiself/Event/blob/master/docs/tools.png">
</p>

## 部署

1. 克隆代码.

```bash
git clone https://github.com/zuiidea/antd-admin.git
```

2. 安装依赖.

```bash
pip install -r requirements.txt
```


3. 启动本地服务.

```bash
python start.py -e local
```

## 相关命令
```bash
sqlacodegen --outfile models.py mysql+pymysql://root:root@localhost:3306/auto_test_frame
```