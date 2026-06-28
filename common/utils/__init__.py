from common.utils.errors import ErrorService
from common.utils.GitHubRequestMixin import GitHubRequestMixin
from common.utils.log import logger


class BaseUtils(ErrorService, GitHubRequestMixin):
    logger = logger
