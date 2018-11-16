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
REGISTRY_NAME = os.getenv("REGISTRY_NAME", "hightest")
IMAGE = os.getenv("IMAGE", "index.alauda.cn/alaudaorg/qaimages:helloworld")
# not necessary
REGISTRY_CREDENTIAL = os.getenv("REGISTRY_CREDENTIAL", "alauda-registry-credential")

JENKINS_ENDPOINT = os.getenv("JENKINS_ENDPOINT",
                             "http://154.8.229.251:8899")
JENKINS_USER = os.getenv("JENKINS_USER", "admin")
JENKINS_TOKEN = os.getenv("JENKINS_TOKEN", "dccbd8d020b4e461f73f7bbb646477e8")

SONAR_ENDPOINT = os.getenv("SONAR_ENDPOINT",
                           "http://sonarqube-donotdelete.nolimited.haproxy-54-223-242-27-alaudacn.myalauda.cn/")
SONAR_TOKEN = os.getenv("SONAR_TOKEN", "318983ce89e6f48c6d1bc3235119841dbff12a2b")

CLAIR_ENDPOINT = os.getenv("CLAIR_ENDPOINT", "zhang-clair.default.haproxy-52-80-107-116-testorg001.myalauda.cn")
CLAIR_SERVICE_PORT = os.getenv("CLAIR_SERVICE_PORT", "6060")
CLAIR_HEALTH_PORT = os.getenv("CLAIR_HEALTH_PORT", "6061")
CLAIR_DATABASE_ADDR = os.getenv("CLAIR_DATABASE_ADDR", "52.80.107.116:5432")
CLAIR_DATABASE_NAME = os.getenv("CLAIR_DATABASE_NAME", "alauda")
CLAIR_DATABASE_USER_NAME = os.getenv("CLAIR_DATABASE_USER_NAME", "alauda")
CLAIR_DATABASE_PASSWORD = os.getenv("CLAIR_DATABASE_PASSWORD", "alauda")

SVN_REPO = os.getenv("SVN_REPO", "http://10.0.96.19:32660/alauda_test")
SVN_CREDENTIAL = os.getenv("SVN_CREDENTIAL", "alauda-svn-credential")
SVN_USERNAME = os.getenv("SVN_USERNAME", "User_Name-01")
SVN_PASSWORD = os.getenv("SVN_PASSWORD", "alauda_Test-!@#")

GIT_REPO = os.getenv("GIT_REPO",
                     "http://154.8.229.251:32475/test/alauda.git")
GIT_CREDENTIAL = os.getenv("GIT_CREDENTIAL", "alauda-git-credential")
GIT_USERNAME = os.getenv("GIT_USERNAME", "alauda")
GIT_PASSWORD = os.getenv("GIT_PASSWORD", "alauda_Test-!@#")

TESTCASES = os.getenv("TESTCASES", "")
CASE_TYPE = os.getenv("CASE_TYPE", "not cluster")
PROJECT_NAME = os.getenv("PROJECT_NAME", "e2etest")
ENV = os.getenv("ENV", "Staging")
RECIPIENTS = get_list_from_str(os.getenv("RECIPIENTS", "testing@alauda.io"))
K8S_NAMESPACE = os.getenv("K8S_NAMESPACE", "{}-alauda-default2-{}".format(PROJECT_NAME, REGION_NAME).replace("_", "-"))
SPACE_NAME = os.getenv("SPACE_NAME", "alauda-default-{}".format(REGION_NAME).replace("_", "-"))

SECRET_ID = os.getenv("SECRET_ID", "AKID84kBMHwKUP4VggjwBAKFvxlJcgU3frtg")
SECRET_KEY = os.getenv("SECRET_EKY", "aDlNSjBSZGRPdkxXUjZWZ2JHZnFPaGpXMklJa3d0WjA=")

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
REPO_NAME = "hello-world"
GLOBAL_INFO_FILE = "./temp_data/global_info.json"
