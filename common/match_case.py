# -*- coding: UTF-8 -*-
def casename():
    casename_dict = {
        "test_newk8s_app": "创建应用-验证应用状态-获取应用详情-获取应用列表-获取应用yaml-操作事件-应用监控-日志-exec-组件监控-"
                           "访问组件地址-获取组件实例数-重构实例-更新组件-验证组件更新-获取文件日志源-停止组件-启动组件-回滚到指定版本-回滚版本-停止应用-启动应用-删除服务-更新应用-验证亲和反亲和-删除应用",
        "test_dashboard": "监控面板相关测试",
        "test_svn_build": "svn快速构建",
        "test_sync_public_registry": "镜像同步",
        "test_project_repo": "项目下镜像的测试",
        "test_gfs_app": "应用使用gfs测试",
        "test_ebs_app": "应用使用ebs测试",
        "test_pvc_app": "应用使用pvc测试",
        "test_gfs_volume": "存储卷gfs测试",
        "test_ebs_volume": "存储卷ebs测试",
        "test_pv": "持久卷测试",
        "test_ci_cd": "持续集成",
        "test_noti": "通知增删改查测试",
        "test_pvc": "持久卷声明测试",
        "test_job_config": "任务测试",
        "test_pvc_use_scs": "持久卷声明使用存储类测试",
        "test_pvc_use_defaultscs": "持久卷声明使用默认存储类测试",
        "test_scs": "存储类测试",
    }
    return casename_dict
