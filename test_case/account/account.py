from common.base_request import Common
from common.log import logger


def log_info(func: object) -> object:
    def wrapper(*args, **kwargs):
        logger.info(func.__name__.center(50, '*'))
        return func(*args, **kwargs)
    return wrapper


class Account(Common):
    """
    account
    api:
    1、register
    """
    def register_account_url(self):
        return "v1/auth/register"

    """
    account
    api:
    1、get account profile
    2、update account password
    """
    def account_profile_url(self):
        return "v1/auth/profile"

    """
    api:
    1、get account info
    2、update company name
    """
    def account_detail_url(self, account):
        return "v1/orgs/{0}".format(account)

    """
    api: 
    1、set ldap config
    2、get ldap config info 
    3、update ldap config 
    4、delete ldap config (abolish ?)
    """
    def ldap_url(self):
        return "v1/orgs/{0}/config/ldap".format(self.account)

    """
    api:
    1、trigger ldap sync
    2、sync sub account status
    3、delete invalid sub account
    """
    def ldap_sync_url(self):
        return "v1/orgs/{0}/config/ldap/sync".format(self.account)

    """
    api:
    1、get invalid sub account num
    """
    def ldap_info_url(self):
        return "v1/orgs/{0}/config/ldap/info".format(self.account)

    """
    api:
    1、get sub account list
    2、create sub account
    """
    def sub_account_url(self):
        return "v1/orgs/{0}/accounts".format(self.account)

    """
    api:
    1、get sub account details
    2、update sub account password
    3、delete sub account
    """
    def sub_account_operate_url(self, username):
        return "v1/orgs/{0}/accounts/{1}".format(self.account, username)

    """
    api:
    1、update sub account detail except password
    """
    def sub_account_detail_operate_url(self, username):
        return "/v1/orgs/{0}/accounts/{1}/details".format(self.account, username)

    """
    api:
    1、get sub account role
    2、assign role to a sub account
    3、revoke role of a sub account
    """
    def sub_account_role_url(self, username):
        return "v1/orgs/{0}/accounts/{1}/roles".format(self.account, username)

    """
    api:
    1、get user token
    2、update user token 
    """
    def get_token(self):
        return "v1/generate-api-token"

    @log_info
    def get_org_detail(self, account=None):
        url = self.account_detail_url(account)
        return self.send(method='GET', path=url, params='')

    @log_info
    def update_company_name(self, file, data, auth=None, account=None):
        url = self.account_detail_url(account)
        data = self.generate_data(file, data)
        return self.send(method='PUT', path=url, data=data, params='', auth=auth)

    @log_info
    def set_ldap(self, file, data):
        url = self.ldap_url()
        data = self.generate_data(file, data)
        return self.send(method='POST', path=url, data=data, params='')

    @log_info
    def get_ldap(self):
        url = self.ldap_url()
        return self.send(method='GET', path=url, params='')

    @log_info
    def update_ldap(self, file, data):
        url = self.ldap_url()
        data = self.generate_data(file, data)
        return self.send(method='PUT', path=url, data=data, params='')

    @log_info
    def delete_ldap(self):
        url = self.ldap_url()
        return self.send(method='DELETE', path=url, params='')
        pass

    @log_info
    def trigger_ldap(self):
        url = self.ldap_sync_url()
        return self.send(method='PUT', path=url, params='')

    @log_info
    def get_ldap_status(self):
        url = self.ldap_sync_url()
        return self.send(method='GET', path=url, params='')

    @log_info
    def delete_deleted_user(self):
        url = self.ldap_sync_url()
        return self.send(method='DELETE', path=url, params='')

    @log_info
    def get_ldap_invalid_accounts_num(self):
        url = self.ldap_info_url()
        return self.send(method='GET', path=url, params='')

    @log_info
    def get_sub_accounts_list(self):
        url = self.sub_account_url()
        return self.send(method='GET', path=url, params='')

    @log_info
    def create_sub_account(self, file, data):
        url = self.sub_account_url()
        data = self.generate_data(file, data)
        return self.send(method='POST', path=url, data=data, params='')
        pass

    @log_info
    def get_sub_account_detail(self, username):
        url = self.sub_account_operate_url(username)
        return self.send(method='GET', path=url, params='')

    @log_info
    def update_sub_account_password(self, file, data, username):
        url = self.sub_account_operate_url(username)
        data = self.generate_data(file, data)
        return self.send(method='PUT', path=url, data=data, params='')

    @log_info
    def delete_sub_account(self, username):
        url = self.sub_account_operate_url(username)
        return self.send(method='DELETE', path=url, params='')

    @log_info
    def update_sub_account_detail(self, file: object, data: object, username: object) -> object:
        url = self.sub_account_detail_operate_url(username)
        data = self.generate_data(file, data)
        return self.send(method='PUT', path=url, data=data, params='')

    @log_info
    def get_sub_account_role(self, username):
        url = self.sub_account_role_url(username)
        return self.send(method='GET', path=url, params='')

    @log_info
    def assign_role_to_sub_account(self, file, data, username):
        url = self.sub_account_role_url(username)
        data = self.generate_data(file, data)
        return self.send(method='POST', path=url, data=data, params='')

    @log_info
    def revoke_role_of_sub_account(self, file, data, username):
        url = self.sub_account_role_url(username)
        data = self.generate_data(file, data)
        return self.send(method='DELETE', path=url, data=data, params='')

    @log_info
    def generate_token(self, file, data, method='POST'):
        url = self.get_token()
        data = self.generate_data(file, data)
        return self.send(method=method, path=url, data=data, params='')

    @log_info
    def register_account(self, file, data):
        url = self.register_account_url()
        data = self.generate_data(file, data)
        return self.send(method='POST', path=url, data=data, params='')

    @log_info
    def get_account_profile(self, auth=None):
        url = self.account_profile_url()
        return self.send(method='GET', path=url, params='', auth=auth)

    @log_info
    def update_account_password(self, file, data, auth=None):
        url = self.account_profile_url()
        data = self.generate_data(file, data)
        return self.send(method='PUT', path=url, data=data, params='', auth=auth)
