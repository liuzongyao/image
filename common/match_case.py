# -*- coding: UTF-8 -*-
def casename():
    casename_dict = {
        "test_newk8s_app": "应用测试",
        "test_dashboard": "监控面板相关测试",
        "test_svn_build": "svn快速构建",
        "test_sync_public_registry": "镜像同步",
        "test_project_repo": "创建镜像项目-获取镜像项目-创建镜像仓库-获取镜像仓库-更新镜像仓库-获取镜像仓库详情-验证更新结果-"
                             "删除镜像仓库-删除镜像项目",
        "test_gfs_app": "应用使用gfs测试",
        "test_ebs_app": "应用使用ebs测试",
        "test_pvc_app": "应用使用pvc测试",
        "test_gfs_volume": "存储卷gfs测试",
        "test_ebs_volume": "存储卷ebs测试",
        "test_pv": "持久卷测试",
        "test_ci_cd": "创建集成中心实例-获取实例状态-停用实例-获取实例状态-更新实例-获取实例状态-删除实例",
        "test_noti": "通知增删改查测试",
        "test_pvc": "持久卷声明测试",
        "test_jenkins_buildimage_updateservice": "获取模板-创建集成中心实例-创建svn凭证-创建镜像仓库凭证-获取镜像地址-创建应用-"
                                                 "获取应用状态-创建Jenkins流水线项目-执行流水线-获取流水线执行状态-检查应用的"
                                                 "镜像版本是否更新成功-删除应用-删除Jenkins流水线-删除集成中心实例-删除镜像版本",
        "test_job_config": "任务测试",
        "test_pvc_use_scs": "持久卷声明使用存储类测试",
        "test_pvc_use_defaultscs": "持久卷声明使用默认存储类测试",
        "test_scs": "存储类测试",
    }
    return casename_dict
