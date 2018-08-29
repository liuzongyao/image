# -*- coding: UTF-8 -*-
def casename():
    casename_dict = {
        "test_newk8s_app": "创建应用-验证应用状态-服务名称校验-获取应用详情-获取应用列表-获取应用yaml-操作事件-应用监控-日志-exec-"
                           "服务监控-访问组件地址-获取容器组列表-获取资源事件-获取组件实例数-重构实例-创建configmap-更新组件-验证组件更新-服务yaml-"
                           "获取文件日志源-停止组件-启动组件-获取版本-回滚到指定版本-回滚版本-停止应用-启动应用-删除服务-"
                           "更新应用-验证多容器-验证亲和反亲和-验证指定主机-删除应用",
        "test_dashboard": "监控面板相关测试",
        "test_svn_build": "svn快速构建",
        "test_sync_public_registry": "创建同步配置-获取配置详情-更新配置-触发镜像同步-获取镜像同步状态-获取镜像同步日志-删除同步配置",
        "test_project_repo": "创建镜像项目-获取镜像项目-创建镜像仓库-获取镜像仓库-更新镜像仓库-获取镜像仓库详情-验证更新结果-"
                             "删除镜像仓库-删除镜像项目",
        "test_gfs_app": "应用使用gfs测试:创建gfs-创建应用-验证应用状态",
        "test_ebs_app": "应用使用ebs测试:创建ebs-创建应用-验证应用状态",
        "test_pvc_app": "应用使用pvc测试:创建存储卷-创建pv-创建pvc-创建应用-验证应用状态",
        "test_gfs_volume": "存储卷gfs测试:获取驱动类型-创建gfs-获取存储卷列表-获取gfs详情-删除gfs",
        "test_ebs_volume": "存储卷ebs测试:获取驱动类型-创建ebs-获取存储卷列表-获取ebs详情-删除ebs",
        "test_pv": "持久卷测试:创建存储卷-创建pv-获取pv列表-更新pv-获取pv详情-删除pv",
        "test_ci_cd": "创建集成中心实例-获取实例状态-停用实例-获取实例状态-更新实例-获取实例状态-删除实例",
        "test_noti": "通知增删改查测试",
        "test_pvc": "持久卷声明测试:创建存储卷-创建pv-创建pvc-获取pvc列表-获取pvc详情-删除pvc",
        "test_jenkins_buildimage_updateservice": "获取模板-创建集成中心实例-创建svn凭证-创建镜像仓库凭证-获取镜像地址-创建应用-"
                                                 "获取应用状态-创建Jenkins流水线项目-执行流水线-获取流水线执行状态-检查应用的"
                                                 "镜像版本是否更新成功-删除应用-删除Jenkins流水线-删除集成中心实例-删除镜像版本",
        "test_job": "任务测试:创建任务-获取创建任务事件-获取任务列表-获取任务配置详情-触发任务配置-查看任务历史-查看任务历史日志-定时任务"
                    "更新任务配置-更新任务事件-获取任务配置详情-触发任务-任务历史列表和日志-删除任务历史-删除任务配置-查看删除任务配置事件",
        "test_pvc_use_scs": "持久卷声明使用存储类测试:创建存储类-创建pvc-获取pvc详情",
        "test_pvc_use_defaultscs": "持久卷声明使用默认存储类测试:制造默认存储类-创建pvc-获取pvc详情",
        "test_scs": "存储类测试:创建sc-获取sc列表-设为默认-获取sc详情-删除sc",
        "test_configmap": "配置管理测试:创建cm-获取cm列表-更新cm-获取cm详情-删除cm",
        "test_project": "创建项目-获取项目列表-更新项目-获取项目详情-删除项目"
    }
    return casename_dict
