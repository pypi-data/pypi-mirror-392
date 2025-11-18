
from processcube_client.core.api.client import DeployResults

from robot.api import logger

from ._retry_helper import retry_on_exception


class DeployKeyword:

    def __init__(self, client, **kwargs):
        self._client = client

    @retry_on_exception
    def deploy_processmodel(self, pathname, exit_on_fail: bool = True, overwrite_existing: bool = True, **kwargs) -> DeployResults:
        deploy_results = self._client.deploy_bpmn_from_path(pathname)

        for deploy_result in deploy_results.deployed_files:
            logger.info(
                f"Deploy '{deploy_result.filename}' successfully=='{deploy_result.deployed}'")

        return deploy_results
