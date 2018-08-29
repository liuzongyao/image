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

JENKINS_ENDPOINT = os.getenv("JENKINS_ENDPOINT", "http://52.80.105.130:8899/")
JENKINS_USER = os.getenv("JENKINS_USER", "admin")
JENKINS_TOKEN = os.getenv("JENKINS_TOKEN", "87d5faf547e7e6216fdc2fa2b0b91405")

SVN_REPO = os.getenv("SVN_REPO", "http://svn-password.k8s-st.haproxy-54-223-242-27-alaudacn.myalauda.cn/alauda_test/")
SVN_CREDENTIAL = os.getenv("SVN_CREDENTIAL", "alauda-svn-credential")
SVN_USERNAME = os.getenv("SVN_USERNAME", "User_Name-01")
SVN_PASSWORD = os.getenv("SVN_PASSWORD", "alauda_Test-!@#")
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
