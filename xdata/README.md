## xdata

[![Python3](https://img.shields.io/badge/python-3.x-green.svg?style=plastic)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-0.12-brightgreen.svg?style=plastic)](http://flask.pocoo.org/)
[![Paramiko](https://img.shields.io/badge/paramiko-2.2.1-green.svg?style=plastic)](http://www.paramiko.org/)
[![Node](https://img.shields.io/badge/node-6.x-green.svg?style=plastic)](https://nodejs.org/)
[![Element](https://img.shields.io/badge/Element-2.x-green.svg?style=plastic)](http://element-cn.eleme.io/#/zh-CN/)

xdata is an open source O & M management system developed with Python + Flask + Vue + Element. The system is separated from the front and the back of the system to help small and medium-sized enterprises manage the hosts, tasks, deployment, configuration files, monitoring and alarming

xdata是一款使用Python+Flask+Vue+Element组件开发的开源运维管理系统,系统前后端分离,帮助中小型企业完成主机、任务、发布部署、配置文件、监控、报警等管理。




### Feature 功能
----------------------------
  - CMDB 资产管理
  - Task 任务计划管理
  - CI/CD 部署、发布管理
  - Config File 配置文件管理
  - Monitor 监控(未完成）
  - Alarm  报警（未完成）


### Environment 环境
----------------------------
   * Python 3.x
   * Flask 0.12
   * Node 6.x
   * Element 2.x



### 详细安装步骤
----------------------------

    [文档](https://github.com/guanshanyue/xdata/wiki)


### Development 开发
----------------------------
```
   1. Clone code 克隆代码：
   $ git clone git@github.com:guanshanyue/xdata.git

   2. Start server 启动服务端：
   $ cd xdata/xdata_api
   $ pip install -r requirements.txt  //安装依赖包
   $ mv config.py.example config.py   //编辑配置文件
   $ python manage.py init_db         //初始化数据库
   $ python manage.py create_admin    //创建管理员
   $ python main.py                   //启动服务

   3. Start web  启动前端：
   $ cd xdata/xdata_web
   $ npm install
   $ npm run dev

   4. Visit 访问：
   $ http://$HOST:8010 (http://你的主机IP:8080 来访问 xdata)

```


### Docs 开发者文档
----------------------------

 * [Project structure 项目结构](https://github.com/openxdata/xdata/blob/master/docs/project_structure.md)
 * [前端UI组件](http://element-cn.eleme.io/2.1/#/zh-CN/component/installation)
 * [后端Flask文档](http://flask.pocoo.org/)


### License & Copyright
----------------------------
[MIT](https://opensource.org/licenses/MIT)
