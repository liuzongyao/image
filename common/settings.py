import os

API_URL = os.getenv("API_URL", "https://api-staging.alauda.cn")
ACCOUNT = os.getenv("ACCOUNT", "testorg001")
SUB_ACCOUNT = os.getenv("SUB_ACCOUNT", "")
PASSWORD = os.getenv("PASSWORD", "alauda_staging")
REGION_NAME = os.getenv("REGION_NAME", "aws_newk8s")
REGISTRY_NAME = os.getenv("REGISTRY_NAME", "awsnewk8s")
SVN_REPO = os.getenv("SVN_REPO", "http://svn-password.k8s-st.haproxy-54-223-242-27-alaudacn.myalauda.cn/alauda_test/")
SVN_REPO_USERNAME = os.getenv("SVN_REPO_USERNAME", "User_Name-01")
SVN_REPO_PASSWORD = os.getenv("SVN_REPO_PASSWORD", "alauda_Test-!@#")
TESTCASES = os.getenv("TESTCASES")
CASE_TYPE = os.getenv("CASE_TYPE")
PROJECT_NAME = os.getenv("PROJECT_NAME", "rubicktest")

SMTP = {
    'host': os.getenv('SMTP_HOST', 'smtpdm.aliyun.com'),
    'port': os.getenv('SMTP_PORT', 465),
    'username': os.getenv('SMTP_USERNAME', 'info@alauda.cn'),
    'password': os.getenv('SMTP_PASSWORD', 'MATHilde123'),
    'sender': os.getenv('EMAIL_FROM', 'info@alauda.cn'),
    'debug_level': 0,
    'smtp_ssl': os.getenv('SMTP_SSL', True)
}

LOG_LEVEL = "INFO"
LOG_PATH = "/var/log/mathilde/"
REPO_NAME = "hello-world"
SPACE_NAME = "staging"
