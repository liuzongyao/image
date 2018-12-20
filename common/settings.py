import os


def get_list_from_str(string, separator=','):
    if string is not None and string != '':
        return string.split(separator)


# necessary
API_URL = os.getenv("API_URL", "https://cloud-staging-api.alauda.cn")
ACCOUNT = os.getenv("ACCOUNT", "alauda")
SUB_ACCOUNT = os.getenv("SUB_ACCOUNT", "")
PASSWORD = os.getenv("PASSWORD", "Alauda2018!@#")
REGION_NAME = os.getenv("REGION_NAME", "high-region-available")
REGISTRY_NAME = os.getenv("REGISTRY_NAME", "high")
IMAGE = os.getenv("IMAGE", "index.alauda.cn/alaudaorg/qaimages:helloworld")
COMMAND_IP = os.getenv("COMMAND_IP", "62.234.102.38")
K8S_IP = os.getenv("K8S_IP", "62.234.114.88")
# not necessary
REGISTRY_CREDENTIAL = os.getenv("REGISTRY_CREDENTIAL", "alauda-registry-credential")

JENKINS_ENDPOINT = os.getenv("JENKINS_ENDPOINT",
                             "http://192.144.148.212:8899")
JENKINS_USER = os.getenv("JENKINS_USER", "admin")
JENKINS_TOKEN = os.getenv("JENKINS_TOKEN", "b1f626706775f04f5aef764a8fda5966")

SONAR_ENDPOINT = os.getenv("SONAR_ENDPOINT",
                           "http://192.144.148.212:10007")
SONAR_TOKEN = os.getenv("SONAR_TOKEN", "94df71bcca7d1e03cecee2222e4afa6047618533")

CLAIR_ENDPOINT = os.getenv("CLAIR_ENDPOINT", "zhang-clair.default.haproxy-52-80-107-116-testorg001.myalauda.cn")
CLAIR_SERVICE_PORT = os.getenv("CLAIR_SERVICE_PORT", "6060")
CLAIR_HEALTH_PORT = os.getenv("CLAIR_HEALTH_PORT", "6061")
CLAIR_DATABASE_ADDR = os.getenv("CLAIR_DATABASE_ADDR", "52.80.107.116:5432")
CLAIR_DATABASE_NAME = os.getenv("CLAIR_DATABASE_NAME", "alauda")
CLAIR_DATABASE_USER_NAME = os.getenv("CLAIR_DATABASE_USER_NAME", "alauda")
CLAIR_DATABASE_PASSWORD = os.getenv("CLAIR_DATABASE_PASSWORD", "alauda")

SVN_REPO = os.getenv("SVN_REPO", "http://192.144.148.212:10009/alauda_test/")
SVN_CREDENTIAL = os.getenv("SVN_CREDENTIAL", "alauda-svn-credential")
SVN_USERNAME = os.getenv("SVN_USERNAME", "User_Name-01")
SVN_PASSWORD = os.getenv("SVN_PASSWORD", "alauda_Test-!@#")

GIT_REPO = os.getenv("GIT_REPO",
                     "http://192.144.148.212:10008/root/test123")
GIT_CREDENTIAL = os.getenv("GIT_CREDENTIAL", "root")
GIT_USERNAME = os.getenv("GIT_USERNAME", "root")
GIT_PASSWORD = os.getenv("GIT_PASSWORD", "07Apples")
GIT_PATH = os.getenv("GIT_PATH", "/")
GIT_BRANCH = os.getenv("GIT_BRANCH", "master")

TESTCASES = os.getenv("TESTCASES", "")
CASE_TYPE = os.getenv("CASE_TYPE", "BAT")
PROJECT_NAME = os.getenv("PROJECT_NAME", "e2etest")
ENV = os.getenv("ENV", "Staging")
RECIPIENTS = get_list_from_str(os.getenv("RECIPIENTS", "testing@alauda.io"))
K8S_NAMESPACE = os.getenv("K8S_NAMESPACE", "{}-alauda-default2-{}".format(PROJECT_NAME, REGION_NAME).replace("_", "-"))
SPACE_NAME = os.getenv("SPACE_NAME", "alauda-default-{}".format(REGION_NAME).replace("_", "-"))

SECRET_ID = os.getenv("SECRET_ID", "AKID84kBMHwKUP4VggjwBAKFvxlJcgU3frtg")
SECRET_KEY = os.getenv("SECRET_EKY", "aDlNSjBSZGRPdkxXUjZWZ2JHZnFPaGpXMklJa3d0WjA=")

# 中间件的镜像仓库地址
MIDDLEWARE_REGISTRY = os.getenv("MIDDLEWARE_REGISTRY", "10.0.128.201:60080")

SMTP = {
    'host': os.getenv('SMTP_HOST', 'smtpdm.aliyun.com'),
    'port': os.getenv('SMTP_PORT', 465),
    'username': os.getenv('SMTP_USERNAME', 'staging@alauda.cn'),
    'password': os.getenv('SMTP_PASSWORD', 'Ahvooy5ie22H0tel'),
    'sender': os.getenv('EMAIL_FROM', 'staging@alauda.cn'),
    'debug_level': 0,
    'smtp_ssl': True
}

LOG_LEVEL = "INFO"
LOG_PATH = "./report"
REPO_NAME = "liuzongyao"
TARGET_REPO_NAME = "sys-repo"
GLOBAL_INFO_FILE = "./temp_data/global_info.json"
