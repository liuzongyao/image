# What is this repository for?

1. 该仓库是用来测试大平台的Jakiro API测试，使用的python pytest测试框架
2. pytest会自动收集指定目录下所有以test开头的方法作为测试的case，并且最终会在Report下生成测试报告

# RUN
本地执行：
1.首先运行环境需要安装python3+和pytest以及requests包，参考requirement.txt
解决本地python环境问题文档：https://www.jianshu.com/p/00af447f0005

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

#Writing test cases

# 注意管理视图的api发送请求时需要添加参数params={}

1.新增测试模块时需要添加对应的目录，在目录下添加对应模块的方法类

2.方法类需要继承基础的base_requests，方法类封装完成后在test_case下添加对应的case

3.需要新建资源post的数据统一放在test_data目录下，新建属于自己模块的目录，将测试数据统一管理

# Code Standard   提交代码要保证flake8通过

1.只要有改动，一定要保证改动影响到的case跑通过之后才可以提交PR

2.每个case之间不能存在任何依赖，都可以单独执行

3.要保证case全部通过，如果环境不支持的case，Report结果标记为通过

4.如果新增了环境变量，要case合并到master后及时更新私有部署自动化测试使用文档的说明

5.添加新功能的case时，挑选一个critical级别的case，打上BAT的标签。

6.在封装基础类方法时要考虑到通用性、可读性和易用性

7.尽可能将有用的信息使用logging打印出来，因为pytest的测试报告会收集相关日志信息，方便查看日志定位问题

8.各个模块用到的方法在各自模块定义，禁止出现来回调用的情况

9.在测试跑完之后要保证测试环境的干净，所有资源必须全部删除

10.变量和函数名统一使用小写字母和下划线，尽量简洁明了

11.写case时尽量多的考虑下出异常的情况，保证代码健壮性

12.非block case统一在测试执行结束后判断

13.所有的create资源的方法，在创建前都要执行一下删除操作

# 平台参数

平台的一些参数和集群的信息在用例执行前会写入到./temp_data/global_info.json的文件内，
需要注意的是这些key不要存在包含与被包含的关系 比如不要有$REPO $REPO_NAME 这样的情况，否则替换字符串会出现问题
样例如下：
{
  "$NAMESPACE": "testorg001",   #账号
  "$SVN_PASSWORD": "alauda_Test-!@#",  # svn密码
  "$SVN_USERNAME": "User_Name-01",   # svn账号
  "$SVN_REPO": "http://svn-password.k8s-st.haproxy-54-223-242-27-alaudacn.myalauda.cn/alauda_test/", #svn地址
  "$REGISTRY": "awsnewk8s",  #集群对应registry名称
  "$REPO_NAME": "hello-world",  #测试使用的镜像仓库
  "$SPACE_NAME": "alauda-default-aws-newk8s",  #测试使用的资源空间
  "$REGION_NAME": "aws_newk8s",   #集群名称
  "$K8S_NAMESPACE": "alauda-default2-aws-newk8s",  #测试使用的k8s namespace
  "$IMAGE": "index.alauda.cn/alaudaorg/qaimages:helloworld", #测试服务使用的镜像
  "$REGION_ID": "dc07a499-ecf2-4f73-8f85-188990a8415c",  # 集群的uuid
  "$REGION_VOLUME": "glusterfs,ebs",  #当前集群支持的存储卷类型
  "$BUILD_ENDPOINT_ID": "2aed16f6-0bc6-402e-8091-31ea83109c13",  #构建集群的uuid
  "$HAPROXY_NAME": "haproxy-54-222-236-194",   #集群对应负载均衡的名称
  "$HAPROXY_IP": "54.222.236.194",   #集群对应负载均衡的ip
  "$SLAVEIPS": "172.31.23.198,172.31.16.59,172.31.19.89,172.31.22.166", #集群内可调用节点的ip
  "PUBLIC_REGISTRY": [
    {
      "name": "alauda_public_registry",  #公有镜像源的名称
      "uuid": "aa0fd126-49c5-4abe-9355-3f924357868d",  #公有镜像源的uuid
      "endpoint": "index-staging.alauda.cn"  #公有镜像源的地址
    }
  ],
  "PRIVATE_REGISTRY": [
    {
      "name": "awsnewk8s",  #集群对应registry名称
      "uuid": "b2eb2693-7245-4318-b11d-96dcd56b2fcc",  #集群对应registry的uuid
      "endpoint": "aws-newk8s-testorg001.stagingindex.alauda.cn:5000" #集群对应registry地址
    }
  ],
  "$PROJECT_UUID": "a1e03f0e-92b6-4b7f-a8ec-59a45698cb82",  # 测试使用项目的uuid
  "$K8S_NS_UUID": "7d7d3201-a41d-11e8-a068-0212cdf75a6a",   # 测试使用的k8s namespace对应的uuid
  "$SPACE_UUID": "d2561952-cccb-4aaa-861e-97bd4fa1ae3a"     # 测试使用资源空间对应的uuid
}