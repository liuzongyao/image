from test_case.image.image import Image
import pytest
import os
from common.log import logger


@pytest.mark.BAT
class TestImageSuite(object):
    def setup_class(self):
        self.image_tool = Image()
        self.index = 10
        self.tencent = 'test_case/image/tencent.pem'
        secret_name = 'pull-image-secret6'
        self.add_daemon = 'test_case/image/add_daemon.py'
        self.tag = 'helloworld'
        if self.image_tool.env != 'private':
            ret_registry = self.image_tool.install_registry(self.image_tool.region_name, self.image_tool.registry_name,
                                                            "test_data/image/install_registry.json")
            assert ret_registry.status_code == 200, "安装registry失败：{}".format(ret_registry.text)

            self.image_tool.get_registry_running()

        self.registry_address = self.image_tool.get_registry_endpoint()
        cmd = 'scp -i ' + self.tencent + ' -P 52022 ' + self.add_daemon + ' liuzongyao@118.24.213.153:/home/liuzongyao'
        logger.info('copy file to tencent jump host ' + cmd)
        os.system(cmd)

        copy_add_daemon = 'scp add_daemon.py root@' + self.image_tool.command_ip + ':/root'

        logger.info('copy file to the worker daemon host ' + copy_add_daemon)
        self.image_tool.remote_exec_command(copy_add_daemon, hostname='118.24.213.153', port=52022,
                                            username='liuzongyao', key_filename=self.tencent)

        copy_file = 'ssh -tt root@' + self.image_tool.command_ip + ' python add_daemon.py ' + self.registry_address
        logger.info('copy file command ' + copy_file)
        self.image_tool.remote_exec_command(copy_file, hostname='118.24.213.153', port=52022,
                                            username='liuzongyao', key_filename=self.tencent)

        restart_docker = 'ssh -tt root@' + self.image_tool.command_ip + ' systemctl restart docker.service'
        logger.info('restart docker command ' + restart_docker)
        self.image_tool.remote_exec_command(restart_docker, hostname='118.24.213.153', port=52022,
                                            username='liuzongyao', key_filename=self.tencent)

        docker_login = 'ssh -tt root@' + self.image_tool.command_ip + ' docker login -u ' + self.image_tool.account + \
                       ' -p ' + self.image_tool.password + ' ' + self.registry_address
        logger.info('docker login command ' + docker_login)
        self.image_tool.remote_exec_command(docker_login, hostname='118.24.213.153', port=52022,
                                            username='liuzongyao', key_filename=self.tencent)

        docker_pull = 'ssh -tt root@' + self.image_tool.command_ip + ' docker pull ' + self.image_tool.image
        logger.info('docker login command ' + docker_pull)
        self.image_tool.remote_exec_command(docker_pull, hostname='118.24.213.153', port=52022,
                                            username='liuzongyao', key_filename=self.tencent)

        create_secrets = 'ssh -tt root@' + self.image_tool.k8s_ip + ' kubectl create secret docker-registry  ' \
                         + secret_name + ' --docker-server=\'' + self.registry_address + '\' --docker-username=\'' \
                         + self.image_tool.account + '\' --docker-password=\'' + self.image_tool.password \
                         + '\' ' '--docker-email=highcareer@126.com -n ' + self.image_tool.k8s_namespace
        logger.info('create secrets command ' + create_secrets)

        self.image_tool.remote_exec_command(create_secrets, hostname='118.24.213.153', port=52022,
                                            username='liuzongyao', key_filename=self.tencent)

        # sa.json from k8s to tencent to local

        get_sa = 'ssh -tt root@' + self.image_tool.k8s_ip + ' kubectl get sa default -o json -n ' \
                 + self.image_tool.k8s_namespace + ' > sa.json'
        logger.info('create secrets command ' + get_sa)

        self.image_tool.remote_exec_command(get_sa, hostname='118.24.213.153', port=52022,
                                            username='liuzongyao', key_filename=self.tencent)

        self.image_tool.copy_from_jumper_to_local('/home/liuzongyao/sa.json', '118.24.213.153', 52022, 'liuzongyao',
                                                  'test_case/image', key_filename=self.tencent)

        self.image_tool.change_secrets(secret_name)

        self.image_tool.copy_from_local_to_jumper('test_case/image/sa.json', '118.24.213.153', 52022, 'liuzongyao',
                                                  '/home/liuzongyao', key_filename=self.tencent)

        cmd = self.image_tool.copy_from_jumper_to_node('sa.json', '62.234.114.88', 'root', '/root')

        self.image_tool.remote_exec_command(cmd, hostname='118.24.213.153', port=52022, username='liuzongyao',
                                            key_filename=self.tencent)

        replace_sa = 'ssh -tt root@' + self.image_tool.k8s_ip + ' kubectl replace sa default -f sa.json ' \
                     + self.image_tool.k8s_namespace
        logger.info('replace sa pull image secrets command ' + replace_sa)

        self.image_tool.remote_exec_command(replace_sa, hostname='118.24.213.153', port=52022,
                                            username='liuzongyao', key_filename=self.tencent)

        self.update_repo = "update daemon"
        self.reg_project_name = self.image_tool.region_name
        self.repo_name = self.image_tool.region_name

    def teardown_class(self):
        pass
        # self.image_tool.uninstall_registry(self.image_tool.region_name)
        # jenkins还需要镜像仓库 不应该在此次删除 应该在系统teardown里删除


    def test_multiple_project(self):
        # create registry project
        for i in range(1, self.index):
            create_reg_project = self.image_tool.create_reg_project('./test_data/image/create_reg_project.yaml',
                                                                    {"$REG_PROJECT_NAME": self.reg_project_name + str(i)})
            assert create_reg_project.status_code == 201, "创建镜像项目操作失败"
            # get registry project
            get_reg_project = self.image_tool.get_reg_project(self.reg_project_name + str(i))
            assert get_reg_project, "创建镜像项目失败"
            # delete registry project
            delete_reg_project = self.image_tool.delete_reg_project(self.reg_project_name + str(i))
            assert delete_reg_project.status_code == 204, "删除镜像项目操作失败"

    def test_one_project_multiple_repo(self):
        # create registry project
        create_reg_ret = self.image_tool.create_reg_project('./test_data/image/create_reg_project.yaml',
                                                            {"$REG_PROJECT_NAME": self.reg_project_name})
        assert create_reg_ret.status_code == 201, "创建镜像项目操作失败"
        for i in range(1, self.index):
            create_repo_ret = self.image_tool.create_repo('./test_data/image/create_repo.yaml',
                                                          {"$REPO_IMAGE": self.repo_name + str(i)},
                                                          reg_project_name=self.reg_project_name)
            assert create_repo_ret.status_code == 201, "创建镜像仓库操作失败"
            # delete repo
            delete_repo_ret = self.image_tool.delete_repo(self.repo_name + str(i),
                                                          reg_project_name=self.reg_project_name)
            assert delete_repo_ret.status_code == 204, "删除镜像仓库操作失败"
        # delete registry project
        delete_reg_ret = self.image_tool.delete_reg_project(self.reg_project_name)
        assert delete_reg_ret.status_code == 204, "删除镜像项目操作失败"

    def test_shared_multiple_repo(self):
        # create registry project
        for i in range(1, self.index):
            create_repo_ret = self.image_tool.create_repo('./test_data/image/create_repo.yaml',
                                                          {"$REPO_IMAGE": self.repo_name + str(i)})
            assert create_repo_ret.status_code == 201, "创建镜像仓库操作失败"
            # delete repo
            delete_repo_ret = self.image_tool.delete_repo(self.repo_name + str(i))
            assert delete_repo_ret.status_code == 204, "删除镜像仓库操作失败"

    def test_project_repo(self):
        # create registry project
        create_reg_ret = self.image_tool.create_reg_project('./test_data/image/create_reg_project.yaml',
                                                            {"$REG_PROJECT_NAME": self.reg_project_name})
        assert create_reg_ret.status_code == 201, "创建镜像项目操作失败"

        # get registry project
        get_reg_ret = self.image_tool.get_reg_project(self.reg_project_name)
        assert get_reg_ret, "获得镜像项目失败"

        # create repo
        create_repo_ret = self.image_tool.create_repo('./test_data/image/create_repo.yaml',
                                                      {"$REPO_IMAGE": self.repo_name},
                                                      reg_project_name=self.reg_project_name)
        assert create_repo_ret.status_code == 201, "创建镜像仓库操作失败"

        # get repo
        get_repo_ret = self.image_tool.get_repo_detail(self.repo_name, reg_project_name=self.reg_project_name)
        assert get_repo_ret.status_code == 200, "创建镜像仓库失败"

        # update repo
        update_repo_ret = self.image_tool.update_repo(self.repo_name, './test_data/image/update_repo.yaml',
                                                      {"$UPDATE_REPO": self.update_repo},
                                                      reg_project_name=self.reg_project_name)
        assert update_repo_ret.status_code == 200, "更新镜像仓库操作失败"
        # get repo detail after update
        get_repo_detail = self.image_tool.get_repo_detail(self.repo_name, reg_project_name=self.reg_project_name)
        assert get_repo_detail.status_code == 200, "获取镜像仓库详情失败"
        # verify the update value
        content = get_repo_detail.json()
        ret = self.image_tool.get_value(content, 'full_description')
        assert ret == self.update_repo, "更新镜像仓库失败"

        # delete repo
        delete_repo_ret = self.image_tool.delete_repo(self.repo_name, reg_project_name=self.reg_project_name)
        assert delete_repo_ret.status_code == 204, "删除镜像仓库操作失败"

        # verify delete result
        get_repo_ret = self.image_tool.get_repo_detail(self.repo_name, reg_project_name=self.reg_project_name)
        assert get_repo_ret.status_code == 404, "镜像仓库没有被成功删除掉"

        # delete registry project
        delete_reg_ret = self.image_tool.delete_reg_project(self.reg_project_name)
        assert delete_reg_ret.status_code == 204, "删除镜像项目操作失败"

        # verify delete result
        get_reg_project_ret = self.image_tool.get_reg_project(self.reg_project_name)
        assert get_reg_project_ret is False, "删除镜像项目失败"

    def test_shared_repo(self):
        # create repo
        create_repo_ret = self.image_tool.create_repo('./test_data/image/create_repo.yaml',
                                                      {"$REPO_IMAGE": self.repo_name})
        assert create_repo_ret.status_code == 201, "创建镜像仓库操作失败"

        # get repo
        get_repo_ret = self.image_tool.get_repo_detail(self.repo_name)
        assert get_repo_ret.status_code == 200, "创建镜像仓库失败"

        # update repo
        update_repo_ret = self.image_tool.update_repo(self.repo_name, './test_data/image/update_repo.yaml',
                                                      {"$UPDATE_REPO": self.update_repo})
        assert update_repo_ret.status_code == 200, "更新镜像仓库操作失败"
        # get repo detail after update
        get_repo_detail = self.image_tool.get_repo_detail(self.repo_name,)
        assert get_repo_detail.status_code == 200, "获取镜像仓库详情失败"
        # verify the update value
        content = get_repo_detail.json()
        ret = self.image_tool.get_value(content, 'full_description')
        assert ret == self.update_repo, "更新镜像仓库失败"

        # delete repo
        delete_repo_ret = self.image_tool.delete_repo(self.repo_name)
        assert delete_repo_ret.status_code == 204, "删除镜像仓库操作失败"

    def test_project_push_image(self):
        create_reg_ret = self.image_tool.create_reg_project('./test_data/image/create_reg_project.yaml',
                                                            {"$REG_PROJECT_NAME": self.reg_project_name})
        assert create_reg_ret.status_code == 201, "创建镜像项目操作失败"

        # create repo
        create_repo_ret = self.image_tool.create_repo('./test_data/image/create_repo.yaml',
                                                      {"$REPO_IMAGE": self.repo_name},
                                                      reg_project_name=self.reg_project_name)
        assert create_repo_ret.status_code == 201, "创建镜像仓库操作失败"

        docker_tag = 'ssh -tt root@' + self.image_tool.command_ip + ' docker tag ' + self.image_tool.image + ' ' \
                     + self.registry_address + '/'+self.repo_name+'/'+self.reg_project_name+':'+self.tag
        logger.info('docker login command ' + docker_tag)
        self.image_tool.remote_exec_command(docker_tag, hostname='118.24.213.153', port=52022,
                                            username='liuzongyao', key_filename=self.tencent)

        docker_push = 'ssh -tt root@' + self.image_tool.command_ip + ' docker push ' + self.registry_address +\
                      '/'+self.repo_name+'/'+self.reg_project_name+':'+self.tag
        logger.info('docker login command ' + docker_push)
        self.image_tool.remote_exec_command(docker_push, hostname='118.24.213.153', port=52022,
                                            username='liuzongyao', key_filename=self.tencent)

        get_repo_tag = self.image_tool.get_repo_tag(self.repo_name, self.reg_project_name)
        assert get_repo_tag.status_code == 200, "创建镜像仓库操作失败"

        get_image_detail = self.image_tool.get_image_detail(self.repo_name, self.tag, self.reg_project_name)
        assert get_image_detail.status_code == 200, "创建镜像仓详情失败"

        get_repo_detail = self.image_tool.get_repo_detail(self.repo_name, self.reg_project_name)

        assert get_repo_detail.json()['upload'] == 1

        delete_repo_ret = self.image_tool.delete_repo(self.repo_name, self.reg_project_name)
        assert delete_repo_ret.status_code == 204, "删除镜像仓库操作失败"

        delete_reg_ret = self.image_tool.delete_reg_project(self.reg_project_name)
        assert delete_reg_ret.status_code == 204, "删除镜像项目操作失败"

    def test_shared_push_image(self):
        create_repo_ret = self.image_tool.create_repo('./test_data/image/create_repo.yaml',
                                                      {"$REPO_IMAGE": self.repo_name})
        assert create_repo_ret.status_code == 201, "创建镜像仓库操作失败"

        docker_tag = 'ssh -tt root@' + self.image_tool.command_ip + ' docker tag ' + self.image_tool.image + ' ' +\
                     self.registry_address + '/' + self.repo_name + ':' + self.tag
        logger.info('docker login command ' + docker_tag)
        self.image_tool.remote_exec_command(docker_tag, hostname='118.24.213.153', port=52022,
                                            username='liuzongyao', key_filename=self.tencent)

        docker_push = 'ssh -tt root@' + self.image_tool.command_ip + ' docker push ' + self.registry_address + '/' + \
                      self.repo_name + ':' + self.tag
        logger.info('docker login command ' + docker_push)
        self.image_tool.remote_exec_command(docker_push, hostname='118.24.213.153', port=52022,
                                            username='liuzongyao', key_filename=self.tencent)

        get_repo_tag = self.image_tool.get_repo_tag(self.repo_name)
        assert get_repo_tag.status_code == 200, "创建镜像仓库操作失败"

        get_image_detail = self.image_tool.get_image_detail(self.repo_name, self.tag)
        assert get_image_detail.status_code == 200, "创建镜像仓详情失败"

        get_repo_detail = self.image_tool.get_repo_detail(self.repo_name)

        assert get_repo_detail.json()['upload'] == 1

        delete_repo_ret = self.image_tool.delete_repo(self.repo_name)

        assert delete_repo_ret.status_code == 204, "删除镜像仓库操作失败"
