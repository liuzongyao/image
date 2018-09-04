# -*- coding: UTF-8 -*-
def casename():
    casename_dict = {
        "test_newk8s_app": "创建应用-验证应用状态-服务名称校验-获取应用详情-获取应用列表-获取应用yaml-操作事件-应用监控-日志-exec-"
                           "服务监控-访问组件地址-获取容器组列表-获取资源事件-获取组件实例数-重构实例-创建configmap-更新组件-验证组件更新-服务yaml-"
                           "获取文件日志源-停止组件-启动组件-获取版本-回滚到指定版本-回滚版本-停止应用-启动应用-删除服务-"
                           "更新应用-验证多容器-验证亲和反亲和-验证指定主机-删除应用",
        "test_dashboard": "创建监控面板-获取面板列表-更新面板-新建node-CPU监控图表-新建comp-ddagent图表-新建服务CPU图表-获取面板详情-删除图表-删除面板",
        "test_svn_build": "获取CI镜像-预览YAML-上传Dockerfile-预览Dockerfile-更新Dockerfile-删除Dockerfile-创建构建-"
                          "检查创建事件-获取构建配置列表-触发构建-构建日志-检查触发事件-检查版本-获取历史列表-删除构建历史-删除构建配置",
        "test_sync_public_registry": "创建同步配置-获取配置详情-更新配置-触发镜像同步-获取镜像同步状态-获取镜像同步日志-删除同步配置",
        "test_project_repo": "创建镜像项目-获取镜像项目-创建镜像仓库-获取镜像仓库-更新镜像仓库-获取镜像仓库详情-验证更新结果-"
                             "删除镜像仓库-删除镜像项目",
        "test_gfs_app": "应用使用gfs测试:创建gfs-创建应用-验证应用状态",
        "test_ebs_app": "应用使用ebs测试:创建ebs-创建应用-验证应用状态",
        "test_pvc_app": "应用使用pvc测试:创建存储卷-创建pv-创建pvc-创建应用-验证应用状态",
        "test_gfs_volume": "存储卷gfs测试:获取驱动类型-创建gfs-获取存储卷列表-获取gfs详情-删除gfs",
        "test_ebs_volume": "存储卷ebs测试:获取驱动类型-创建ebs-获取存储卷列表-获取ebs详情-删除ebs",
        "test_pv": "持久卷测试:创建存储卷-创建pv-获取pv列表-更新pv-获取pv详情-获取存储卷详情-删除pv",
        "test_ci_cd": "创建集成中心实例-获取实例状态-停用实例-获取实例状态-更新实例-获取实例状态-删除实例",
        "test_noti": "通知增删改查测试",
        "test_pvc": "持久卷声明测试:创建存储卷-创建pv-创建pvc-获取pvc列表-获取pvc详情-获取pv详情-删除pvc",
        "test_jenkins_buildimage_updateservice": "检查Jenkins是否能访问-判断集成中心实例是否创建成功-获取模板-创建svn凭证-创建镜像仓库凭证-获取镜像地址-"
                                                 "创建Jenkins流水线项目-获取流水线详情-更新流水线-执行流水线-获取流水线执行状态-检查应用的"
                                                 "镜像版本是否更新成功-删除Jenkins流水线-删除镜像版本",
        "test_jenkins_build_with_git": "检查Jenkins是否能访问-判断集成中心实例是否创建成功-获取模板-创建git凭证-创建流水线项目-"
                                       "执行流水线项目-取消执行流水线历史-再次执行流水线历史-删除流水线历史-删除流水线项目",
        "test_jenkins_build_with_svn_no_sonar": "检查Jenkins是否能访问-判断集成中心实例是否创建成功-获取模板-获取镜像版本-"
                                                "创建代码凭证-创建流水线项目-获取流水线项目列表-执行流水线项目-获取流水线运行历史列表-删除流水线项目",
        "test_jenkins_update_service": "检查Jenkins是否能访问-判断集成中心实例是否创建成功-获取模板-获取镜像仓库地址-获取镜像版本-"
                                       "创建流水线项目-执行流水线项目-获取流水线项目执行状态-获取应用详情-获取应用的镜像版本-"
                                       "获取应用的环境变量-删除流水线项目",
        "test_jenkins_build_with_svn_sonar": "检查Jenkins是否能访问-检查sonar是否能访问-判断集成中心实例是否创建成功-获取模板-"
                                             "创建svn代码仓库凭证-获取代码扫描阈值-获取开发语言-创建流水线项目-执行流水线项目-"
                                             "获取流水线项目的执行状态-删除流水线项目",
        "test_pipeline": "创建流水线项目-获取流水线列表-获取流水线详情-更新流水线-获取流水线详情-获取应用详情-获取镜像版本-"
                         "启动流水线项目-获取流水线运行状态-获取流水线日志-验证应用是否更新成功-获取流水线历史列表-获取上传产出物-"
                         "获取下载产出物-删除流水线运行历史-删除流水线项目",
        "test_job": "任务测试:创建任务-获取创建任务事件-获取任务列表-获取任务配置详情-触发任务配置-查看任务历史-查看任务历史日志-定时任务"
                    "更新任务配置-更新任务事件-获取任务配置详情-触发任务-任务历史列表和日志-删除任务历史-删除任务配置-查看删除任务配置事件",
        "test_pvc_use_scs": "持久卷声明使用存储类测试:创建存储类-创建pvc-获取pvc详情",
        "test_pvc_use_defaultscs": "持久卷声明使用默认存储类测试:制造默认存储类-创建pvc-获取pvc详情",
        "test_scs": "存储类测试:创建sc-获取sc列表-设为默认-获取sc详情-删除sc",
        "test_configmap": "配置管理测试:创建cm-获取cm列表-更新cm-获取cm详情-删除cm",
        "test_metric_alarm": "指标警报测试:创建指标警报-获取警报详情-验证扩容-发送确认-更新指标警报-验证缩容-获取警报列表-删除警报",
        "test_project": "创建项目-获取项目列表-更新项目-获取项目详情-删除项目"
    }
    return casename_dict
