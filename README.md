# RUN
本地执行：
1.首先运行环境需要安装python3+和pytest以及requests包

2.然后设置需要测试对象的环境变量

查看common/settings文件定义的变量
如：API_URL，ACCOUNT, PASSWORD, REGION_NAME, REGISTRY_NAME等等

如果用到第三方服务，要保证第三方服务的可用性，如：jenkins，svn，gitlab等，同时将用到的参数写入环境变量中

3.最后执行python main.py文件即可

容器执行：

1.下载镜像 index.alauda.cn/alaudaorg/api-test:latest

2.然后需要准备测试对象的环境变量写入一个环境变量文件，具体设置和本地运行一致。然后在运行容器时将这个环境变量文件挂载到容器

3.执行命令：
docker run -t --name vipercd \
	-v $(pwd)/report:/app/report/ \
	--env-file=./local-test.env \
	index.alauda.cn/alaudaorg/api-test:latest


# Code Standard

1.只要有改动，一定要保证改动影响到的case跑通过之后才可以提交PR

2.每个case之间不能存在任何依赖，都可以单独执行

3.要保证case全部通过，如果环境不支持的case，Report结果标记为通过

4.如果新增了环境变量，要case合并到master后及时更新私有部署自动化测试使用文档的说明

5.添加新功能的case时，挑选一个critical级别的case，打上BAT的标签。

6.在封装基础类方法时要考虑到通用性、可读性和易用性

7.尽可能将有用的信息使用logging打印出来，因为pytest的测试报告会收集相关日志信息，方便查看日志定位问题

8.各个模块用到的方法在各自模块定义，禁止出现来回调用的情况

9.在测试跑完之后要保证测试环境的干净，所有资源必须全部删除

10.变量和函数名统一使用小写自己和下划线，尽量简洁明了

11.写case时尽量多的考虑下出异常的情况，保证代码健壮性

12.非block case统一在测试执行结束后判断