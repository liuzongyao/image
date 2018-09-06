import os


def get_list_from_str(string, separator=','):
    if string is not None and string != '':
        return string.split(separator)


# necessary
API_URL = os.getenv("API_URL", "https://api-staging.alauda.cn")
ACCOUNT = os.getenv("ACCOUNT", "testorg001")
SUB_ACCOUNT = os.getenv("SUB_ACCOUNT", "")
PASSWORD = os.getenv("PASSWORD", "alauda_staging")
REGION_NAME = os.getenv("REGION_NAME", "aws_newk8s")
REGISTRY_NAME = os.getenv("REGISTRY_NAME", "aws_newk8s")
IMAGE = os.getenv("IMAGE", "index.alauda.cn/alaudaorg/qaimages:helloworld")
# not necessary
REGISTRY_CREDENTIAL = os.getenv("REGISTRY_CREDENTIAL", "alauda-registry-credential")

JENKINS_ENDPOINT = os.getenv("JENKINS_ENDPOINT",
                             "http://alauda-jenkins.jenkins.nginx-52-81-25-67-testorg001.myalauda.cn/")
JENKINS_USER = os.getenv("JENKINS_USER", "admin")
JENKINS_TOKEN = os.getenv("JENKINS_TOKEN", "1323a281573d215c39c573bcd2654e7e")

SONAR_ENDPOINT = os.getenv("SONAR_ENDPOINT",
                           "http://sonarqube-donotdelete.nolimited.haproxy-54-223-242-27-alaudacn.myalauda.cn/")
SONAR_TOKEN = os.getenv("SONAR_TOKEN", "318983ce89e6f48c6d1bc3235119841dbff12a2b")

CLAIR_ENDPOINT = os.getenv("CLAIR_ENDPOINT", "zhang-clair.default.haproxy-52-80-107-116-testorg001.myalauda.cn")
CLAIR_SERVICE_PORT = os.getenv("CLAIR_SERVICE_PORT", "6060")
CLAIR_HEALTH_PORT = os.getenv("CLAIR_HEALTH_PORT", "6061")
DATABASE_ADDR = os.getenv("DATABASE_ADDR", "52.80.107.116:5432")
DATABASE_NAME = os.getenv("DATABASE_NAME", "alauda")
DATABASE_USER_NAME = os.getenv("DATABASE_USER_NAME", "alauda")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "alauda")

SVN_REPO = os.getenv("SVN_REPO", "http://svn-password.k8s-st.haproxy-54-223-242-27-alaudacn.myalauda.cn/alauda_test/")
SVN_CREDENTIAL = os.getenv("SVN_CREDENTIAL", "alauda-svn-credential")
SVN_USERNAME = os.getenv("SVN_USERNAME", "User_Name-01")
SVN_PASSWORD = os.getenv("SVN_PASSWORD", "alauda_Test-!@#")

GIT_REPO = os.getenv("GIT_REPO",
                     "http://gitlab.nolimited.haproxy-54-223-242-27-alaudacn.myalauda.cn/alauda/helloci.git")
GIT_CREDENTIAL = os.getenv("GIT_CREDENTIAL", "alauda-git-credential")
GIT_USERNAME = os.getenv("GIT_USERNAME", "alauda")
GIT_PASSWORD = os.getenv("GIT_PASSWORD", "alauda_Test-!@#")

TESTCASES = os.getenv("TESTCASES", "")
CASE_TYPE = os.getenv("CASE_TYPE")
PROJECT_NAME = os.getenv("PROJECT_NAME", "default")
ENV = os.getenv("ENV", "Staging")
RECIPIENTS = get_list_from_str(os.getenv("RECIPIENTS", "testing@alauda.io"))
K8S_NAMESPACE = os.getenv("K8S_NAMESPACE", "alauda-default2-{}".format(REGION_NAME).replace("_", "-"))
SPACE_NAME = os.getenv("SPACE_NAME", "alauda-default-{}".format(REGION_NAME).replace("_", "-"))

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
