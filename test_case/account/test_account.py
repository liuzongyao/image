from typing import Dict, Any, Union

import pytest
import time

from common.base_request import Common
from test_case.account.account import Account


def get_file_path(key, value):
    return './test_data/{}/{}.json'.format(key, value)


@pytest.mark.account
class TestAccountSuite(object):

    def setup_class(self):
        self.timestamp = int(time.time())
        self.sub_account_username = "e2euser"
        self.sub_account_password = "12345678"
        self.sub_account_new_password = "11111111"
        self.sub_account_type = "organizations.Account"
        self.office_address = "office_address"
        self.sub_account_role = "system-project_admin"
        self.test_account_name = 'e2e{}'.format(self.timestamp)
        self.test_account_email = '{}@test.com'.format(self.timestamp)
        self.test_account_mobile = '1{}'.format(self.timestamp)
        self.test_account_password = '123456'
        self.new_account_password = '111111'
        self.company_name = 'alauda'
        self.sub_account_info: Dict[str, str] = {
            "department": "department",
            "email": "test@test.com",
            "extra_info": "extra_info",
            "landline_phone": "01012345678",
            "mobile": "12345678901",
            "office_address": "office_address",
            "position": "position",
            "realname": "realname"
        }
        self.register_account_data: Dict[str, str] = {
            "company": "company",
            "city": "beijing",
            "position": "position",
            "realname": "realname",
            "username": "{}".format(self.test_account_name),
            "email": "{}".format(self.test_account_email),
            "mobile": "{}".format(self.test_account_mobile),
            "password": self.test_account_password
        }
        self.account = Account()
        self.common = Common()

    def teardown_class(self):
        self.account.delete_sub_account(self.sub_account_username)

    @pytest.mark.skip(reason="I haven't thought about it yet.")
    def test_ldap_create(self):
        pass

    @pytest.mark.skip(reason="I haven't thought about it yet.")
    def test_ldap(self):
        pass

    @pytest.mark.BAT
    def test_account(self):
        """
        流程： 创建子账号-获取子账号列表-获取子账号token(模拟登录)-更新token-更新子账号基本信息-获取子账号基本信息-
              更新子账号密码-获取子账号token(模拟登录)-子账号加角色-获取子账号角色列表-删除子账号角色-验证已删除角色
              不在子账号列表-删除子账号-获取子账号token(模拟登录)-注册根账号-获取账号基本信息-更新账号密码-获取账号
              token(模拟登录)-更新公司名称
        """
        result = {'flag': True}

        # prepare test data
        register_account_data: Dict[str, str] = {
            "$company": self.register_account_data['company'],
            "$city": self.register_account_data['city'],
            "$position": self.register_account_data['position'],
            "$realname": self.register_account_data['realname'],
            "$username": self.register_account_data['username'],
            "$email": self.register_account_data['email'],
            "$mobile": self.register_account_data['mobile'],
            "$password": self.register_account_data['password']
        }

        update_account_password_data: Dict[str, str] = {
            "$new_account_password": self.new_account_password,
            "$old_account_password": self.test_account_password
        }

        update_company_name_data: Dict[str, str] = {
            "$new_company_name": self.company_name
        }

        generate_account_token_data: Dict[str, str] = {
            "$test_account_name": self.test_account_name,
            "$test_account_password": self.new_account_password
        }

        create_sub_account_data: Dict[str, str] = {
            "$sub_account_password": self.sub_account_password,
            "$sub_account_user_name": self.sub_account_username
        }

        generate_sub_account_token_data: Dict[str, str] = {
            "$account": self.common.account,
            "$sub_account_user_name": self.sub_account_username,
            "$sub_account_password": self.sub_account_password
        }

        update_sub_account_detail_data: Dict[str, str] = {
            "$department": self.sub_account_info['department'],
            "$email": self.sub_account_info['email'],
            "$extra_info": self.sub_account_info['extra_info'],
            "$landline_phone": self.sub_account_info['landline_phone'],
            "$mobile": self.sub_account_info['mobile'],
            "$office_address": self.sub_account_info['office_address'],
            "$position": self.sub_account_info['position'],
            "$realname": self.sub_account_info['realname'],
            "$sub_account_user_name": self.sub_account_username
        }

        update_sub_account_password_data: Dict[str, str] = {
            "$sub_account_user_name": self.sub_account_username,
            "$sub_account_user_password": self.sub_account_new_password
        }

        generate_new_token_data: Dict[str, str] = {
            "$account": self.common.account,
            "$sub_account_user_name": self.sub_account_username,
            "$sub_account_password": self.sub_account_new_password
        }

        operate_role_to_sub_account_data: Dict[str, str] = {
            "$sub_account_role": self.sub_account_role
        }

        # verify create sub account
        create_sub_account_result = self.account.create_sub_account(get_file_path('account', 'create_sub_account'),
                                                                    create_sub_account_data)
        assert create_sub_account_result.status_code == 201, \
            "创建子账号失败,返回状态码： {}, 返回结果： {}".format(
                create_sub_account_result.status_code,
                create_sub_account_result.content
            )
        assert create_sub_account_result.json()[0]['username'] == \
            self.sub_account_username, "创建账号失败，创建的账号与请求不符，返回的账号： {}".format(
            create_sub_account_result.json()['username'])
        assert self.sub_account_password == create_sub_account_result.json()[0]['password'], \
            "创建子账号失败 ," \
            "创建的密码与请求不符，返回的密码是 {}".format(create_sub_account_result.json()[0]['password'])

        # verify sub account list
        get_sub_account_list_result = self.account.get_sub_accounts_list()

        assert get_sub_account_list_result.status_code == 200
        verify_flag = True if (self.sub_account_username in
                               self.common.get_value_list(get_sub_account_list_result.json()['results'],
                                                          'username')) else False
        assert verify_flag is True, "创建的子账号不在子账号列表, 返回结果： {}".format(
            get_sub_account_list_result.url
        )
        sub_account_type: Union[str, Any] = self.common.get_uuid_accord_name(
            get_sub_account_list_result.json()['results'],
            {"username": self.sub_account_username},
            "type"
        )
        verify_flag = True if (self.sub_account_type == sub_account_type) else False
        assert verify_flag is True, "创建的账号类型不正确, 返回的账号类型是 {}".format(sub_account_type)

        # verify generate token (login)
        generate_token_data_result = self.account.generate_token(
            get_file_path('account', 'generate_sub_account_token'),
            generate_sub_account_token_data
        )
        verify_flag = True if (generate_token_data_result.status_code == 200) else False
        assert verify_flag is True, "获取token失败，响应状态码： {}".format(
            generate_token_data_result.status_code
        )
        for i in generate_token_data_result.json():
            if i == 'token':
                assert generate_token_data_result.json()[i] != '', "获取token失败，token： {} ".format(
                    generate_token_data_result.json()[i]
                )
            if i == 'username':
                assert generate_token_data_result.json()[i] == self.sub_account_username, "获取token失败，" \
                                                                                          "返回子账号无效"
            if i == 'namespace':
                assert generate_token_data_result.json()[i] == self.common.account, "获取token信息失败，" \
                                                                                    "返回账号无效"
        the_old_token = generate_token_data_result.json()['token']
        update_token_result = self.account.generate_token(get_file_path('account', 'generate_sub_account_token'),
                                                          generate_sub_account_token_data, method='PUT')
        verify_flag = True if (update_token_result.status_code == 200) else False
        assert verify_flag is True, "更新token失败, 响应状态码： {}".format(update_token_result.status_code)
        the_new_token: object = update_token_result.json()['token']
        assert the_new_token != the_old_token, '更新token失败 ,旧token： {0} ,' \
                                               '新token： {1}'.format(the_old_token, the_new_token)

        # verify update sub account detail except password
        update_sub_account_detail_result = self.account.update_sub_account_detail(
            get_file_path('account', 'update_sub_account_detail'),
            update_sub_account_detail_data,
            self.sub_account_username
        )
        verify_flag = True if (200 == update_sub_account_detail_result.status_code) else False
        assert verify_flag is True, '更新用户信息失败, 响应状态码： {}， 响应结果： {}'.format(
            update_sub_account_detail_result.status_code,
            update_sub_account_detail_result.content,
        )

        # verify sub account detail
        get_sub_account_detail_result = self.account.get_sub_account_detail(self.sub_account_username)
        verify_flag = True if (get_sub_account_detail_result.status_code == 200) else False
        assert verify_flag is True, "获取子账号信息失败. 响应状态码： {}, 返回结果： {}". \
            format(get_sub_account_detail_result.status_code,
                   get_sub_account_detail_result.content
                   )
        for key in get_sub_account_detail_result:
            if key in self.sub_account_info:
                assert get_sub_account_detail_result.json()[key] == self.sub_account_info[key]

        # verify sub account password
        update_sub_account_password = self.account.update_sub_account_password(get_file_path('account',
                                                                                             'update_password'),
                                                                               update_sub_account_password_data,
                                                                               self.sub_account_username)
        verify_flag = True if (update_sub_account_password.status_code == 204) else False
        assert verify_flag is True, "更新子账号密码失败. 响应状态码是 {}，返回结果：{}". \
            format(update_sub_account_password.status_code,
                   update_sub_account_password.content
                   )

        # verify generate token (login)
        generate_new_token_data_result = self.account.generate_token(
            get_file_path('account', 'generate_sub_account_token'),
            generate_new_token_data
        )
        verify_flag = True if (generate_new_token_data_result.status_code == 200) else False
        assert verify_flag is True, "获取token失败, 响应状态码： {}, 返回结果： {}".format(
            generate_new_token_data_result.status_code,
            generate_new_token_data_result.content
        )

        # verify assign role to sub account
        assign_role_to_sub_account = self.account.assign_role_to_sub_account(
            get_file_path('account', 'operate_role_to_sub_account'),
            operate_role_to_sub_account_data,
            self.sub_account_username
        )

        verify_flag = True if (assign_role_to_sub_account.status_code == 200) else False
        assert verify_flag is True, "添加角色失败, 响应状态码： {}， 返回结果：{}".format(
            assign_role_to_sub_account.status_code,
            assign_role_to_sub_account.content
        )

        assert assign_role_to_sub_account.json()[0]['user'] == self.sub_account_username
        assert assign_role_to_sub_account.json()[0]['role_name'] == self.sub_account_role

        # verify account role list
        get_sub_account_role = self.account.get_sub_account_role(self.sub_account_username)

        verify_flag = True if (get_sub_account_role.status_code == 200) else False

        assert verify_flag is True, "获取子账号角色列表失败, 响应状态码： {}， 返回结果：{}".format(
            get_sub_account_role.status_code,
            get_sub_account_role.content
        )
        assert self.sub_account_role in self.common.get_value_list(
            get_sub_account_role.json(), 'role_name'
        ), "获取子账号角色失败, 添加的角色不在子账号角色列表中"

        revoke_rolt_from_sub_account = self.account.revoke_role_of_sub_account(
            get_file_path('account', 'operate_role_to_sub_account'),
            operate_role_to_sub_account_data,
            self.sub_account_username
        )

        verify_flag = True if (revoke_rolt_from_sub_account.status_code == 204) else False

        assert verify_flag is True, "删除子账号角色失败, 响应状态码： {}， 返回结果：{}".format(
            revoke_rolt_from_sub_account.status_code,
            revoke_rolt_from_sub_account.content
        )

        # verify role not in sub role list
        get_sub_account_role = self.account.get_sub_account_role(self.sub_account_username)

        verify_flag = True if (get_sub_account_role.status_code == 200) else False

        assert verify_flag is True, "获取子账号角色列表失败, 响应状态码： {}， 返回结果：{}".format(
            get_sub_account_role.status_code,
            get_sub_account_role.content
        )
        assert self.sub_account_role not in self.common.get_value_list(
            get_sub_account_role.json(), 'role_name'
        ), "删除子账号角色失败, 删除的子账号角色依然存在于子账号角色列表"

        # delete sub account
        delete_sub_account = self.account.delete_sub_account(self.sub_account_username)
        verify_flag = True if (delete_sub_account.status_code == 204) else False
        assert verify_flag is True, "删除子账号失败, 响应状态码：{}，返回结果：{}".format(
            delete_sub_account.status_code,
            delete_sub_account.content
        )

        # verify generate token (login)
        generate_new_token_data_result = self.account.generate_token(
            get_file_path('account', 'generate_sub_account_token'),
            generate_new_token_data
        )
        verify_flag = True if (generate_new_token_data_result.status_code == 400) else False
        assert verify_flag is True, "获取token成功, 子账号删除失败"

        # verify register account
        register_account = self.account.register_account(get_file_path('account', 'register'), register_account_data)
        verify_flag = True if (register_account.status_code == 201) else False
        assert verify_flag is True, "注册根账号失败,响应状态码：{0},返回结果：{1}".format(
            register_account.status_code,
            register_account.content
        )
        for key in register_account.json():
            if key in self.register_account_data:
                assert register_account.json()[key] == self.register_account_data[key], \
                    "根账号信息错误 ,实际值： {0} 期望值： {1}".format(
                        self.register_account_data[key],
                        register_account.json()[key]
                )

        # verify account profile
        get_account_profile = self.account.get_account_profile(auth=(self.test_account_name,
                                                                     self.test_account_password))
        verify_flag = True if (get_account_profile.status_code == 200) else False
        assert verify_flag is True
        for key in get_account_profile.json():
            if key in self.register_account_data:
                assert get_account_profile.json()[key] == self.register_account_data[key], \
                    "根账号信息错误 ,实际值： {0} 期望值： {1}".format(
                        self.register_account_data[key],
                        get_account_profile.json()[key],
                    )

        # verify update account password
        update_account_password = self.account.update_account_password(
            get_file_path('account', 'update_account_password'),
            update_account_password_data,
            auth=(self.test_account_name, self.test_account_password)
        )
        verify_flag = True if (update_account_password.status_code == 200) else False
        assert verify_flag is True, "更想根账号密码错误,响应状态码：{}, 返回结果： {}".format(
            update_account_password.status_code,
            update_account_password.content
        )

        # verify account login
        generate_account_token = self.account.generate_token(get_file_path('account', 'generate_account_token'),
                                                             generate_account_token_data)
        verify_flag = True if (generate_account_token.status_code == 200) else False
        assert verify_flag is True, "获取根账号token失败,响应状态码 {0}, 返回结果：{1}".format(
            generate_account_token.status_code,
            generate_account_token.content
        )

        # verify update company name
        update_company_name = self.account.update_company_name(get_file_path('account', 'update_company'),
                                                               update_company_name_data,
                                                               auth=(self.test_account_name, self.new_account_password),
                                                               account=self.test_account_name
                                                               )

        verify_flag = True if (update_company_name.status_code == 200) else False
        assert verify_flag is True
        for key in update_company_name.json():
            if key == 'company':
                assert update_company_name.json()['company'] == self.company_name, \
                    "更新公司名称失败, 响应状态码：{}，返回结果：{}".format(
                        update_company_name.status_code,
                        update_company_name.content
                    )

        assert result['flag'] is True
