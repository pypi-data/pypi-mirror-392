import projectal
from tests.base_test import BaseTest


class TestPermission(BaseTest):
    # Reverse linkers
    def test_link_user(self):
        perm = projectal.auth_details()["permissionList"][0]
        perm = projectal.Permission(perm)
        user = self.make_user()
        perm.link_user(user)
        perm.unlink_user(user)

    def test_link_access_policy(self):
        perm = projectal.auth_details()["permissionList"][0]
        perm = projectal.Permission(perm)
        ap = projectal.AccessPolicy.create({"name": "AP"})
        perm.link_access_policy(ap)
        perm.unlink_access_policy(ap)
