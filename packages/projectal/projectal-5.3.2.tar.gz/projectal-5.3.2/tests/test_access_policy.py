import projectal
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestAccessPolicy(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.AccessPolicy)

    def test_crud(self):
        uuId = self.common.test_create(
            {"name": "Test policy (python API wrapper)", "description": "A description"}
        )
        entity = self.common.test_get(uuId)
        changed = {
            "uuId": uuId,
            "name": "Updated policy",
            "description": "New description!",
        }
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_history(self):
        ap = projectal.AccessPolicy.create({"name": "AP"})
        ap["name"] = "History1"
        projectal.AccessPolicy.update(ap)

        # All history (newest to oldest+)
        assert len(ap.history()) == 2

    def test_clone(self):
        ap = projectal.AccessPolicy.create({"name": "AP"})
        uuId = ap.clone({"name": "Cloned"})
        clone = projectal.AccessPolicy.get(uuId)
        assert clone["uuId"] != ap["uuId"]
        assert clone["name"] == "Cloned"

    def test_link_permission(self):
        ap = projectal.AccessPolicy.create({"name": "AP"})
        # Use authed user for simplicity (we have to have some perms to be here)
        auth = projectal.auth_details()
        perm = projectal.User.get_permissions(auth)[0]
        ap.link_permission(perm)
        ap.unlink_permission(perm)

    # Reverse linkers

    def test_link_user(self):
        ap = projectal.AccessPolicy.create({"name": "AP"})
        user = self.make_user()
        ap.link_user(user)
        ap.unlink_user(user)

    def test_list(self):
        self.common.test_list()
