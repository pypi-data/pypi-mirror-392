import projectal.api
import projectal
from projectal.errors import ProjectalVersionException
from tests.base_test import BaseTest


class TestStatus(BaseTest):
    def test_status(self):
        status = projectal.status()
        assert status["status"] == "UP"

    def test_version_support(self):
        projectal.api._check_version_or_fail()

        old = projectal.MIN_PROJECTAL_VERSION
        projectal.MIN_PROJECTAL_VERSION = "0.2.3"
        projectal.api._check_version_or_fail()
        projectal.MIN_PROJECTAL_VERSION = "20.7.1"
        try:
            projectal.api._check_version_or_fail()
        except ProjectalVersionException:
            assert True
            return
        finally:
            # Put it back or remaining tests will fail
            projectal.MIN_PROJECTAL_VERSION = old

        assert False

    def test_permissions(self):
        perms = projectal.api.permission_list()
        assert len(perms) > 0

    def test_url(self):
        # With and without trailing slash should both work
        projectal.api_base = "https://localhost:8443"
        projectal.login()
        projectal.api_base = "https://localhost:8443/"
        projectal.login()
