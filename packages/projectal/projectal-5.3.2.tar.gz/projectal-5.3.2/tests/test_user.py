import projectal
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestUser(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.User)
        self.user = projectal.User.create(
            {
                "email": "test.user.{}@example.com".format(self.random()),
                "firstName": "First",
                "lastName": "Last",
            }
        )

    def test_crud(self):
        uuId = self.common.test_create(
            {
                "email": "test.user.{}@example.com".format(self.random()),
                "identifier": "123456",
                "firstName": "First",
                "lastName": "Last",
            }
        )
        entity = self.common.test_get(uuId)

        # Change only some details
        changed = {
            "uuId": uuId,
            "identifier": "654321",
            "firstName": "Updated first",
            "lastName": "Updated last",
        }

        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_history(self):
        # Push some changes to entity
        # Create event is History0, so 4 events
        self.user["firstName"] = "History1"
        self.user["lastName"] = "History1"
        projectal.User.update(self.user)
        self.user["firstName"] = "History2"
        self.user["lastName"] = "History2"
        projectal.User.update(self.user)
        self.user["firstName"] = "History3"
        self.user["lastName"] = "History3"
        projectal.User.update(self.user)

        # All history (newest to oldest+)
        history = self.user.history(order="asc")
        assert len(history) == 4
        assert history[1]["properties"][0]["newValue"] == "History1"
        assert history[3]["properties"][0]["newValue"] == "History3"

        # Limit history
        history = self.user.history(limit=2)
        assert len(history) == 2

        # Start at end, only 2 left
        history = self.user.history(start=2)
        assert len(history) == 2

        # All, desc order
        history = self.user.history(order="desc")
        assert len(history) == 4
        assert history[0]["properties"][0]["newValue"] == "History3"
        assert history[2]["properties"][0]["newValue"] == "History1"

    def test_clone(self):
        uuId = self.user.clone(
            {
                "firstName": "Cloned",
                "lastName": "Cloned",
                "email": "cloned-{}@example.com".format(self.random()),
            }
        )
        clone = projectal.User.get(uuId)
        assert clone["uuId"] != self.user["uuId"]
        assert clone["firstName"] == "Cloned"

    def test_register(self):
        assert projectal.User.register(self.user)

    def test_permissions_current_user(self):
        perms = projectal.User.current_user_permissions()
        # There's at least 127, so this is a reasonably safe number
        assert len(perms) > 20

    def test_link_access_policy(self):
        ap = projectal.AccessPolicy.create({"name": "Access Policy"})
        self.user.link_access_policy(ap)
        self.user.unlink_access_policy(ap)

    def test_link_permission(self):
        # Grab one of the perms from authed user
        perm = projectal.auth_details()["permissionList"][0]
        self.user.link_permission(perm)
        # Check if they have it
        u = projectal.User.get(self.user["uuId"], links=["PERMISSION"])
        assert u["permissionList"][0]["uuId"] == perm["uuId"]
        # Remove it
        self.user.unlink_permission(perm)

    def test_link_tag(self):
        tag = self.make_tag()
        user = self.make_user()
        user.link_tag(tag)
        user.unlink_tag(tag)

    # Empty linkers
    def test_link_note(self):
        user = self.make_user()
        note = projectal.Note.create(user, {"text": "Note"})
        assert len(user["noteList"]) == 1
        assert user["noteList"][0]["uuId"] == note["uuId"]
        assert user["noteList"][0]["text"] == note["text"]

        user = projectal.User.get(user["uuId"], links=["note"])
        projectal.Note.create(user, {"text": "Note 2"})
        assert len(user["noteList"]) == 2

    def test_details(self):
        d = projectal.User.current_user_details()
        assert d["uuId"]

    def test_permissions(self):
        # Use authed user for simplicity (we have to have some perms to be here)
        auth = projectal.auth_details()
        perms = projectal.User.get_permissions(auth)
        assert len(perms) > 0

    def test_bulk_permissions(self):
        auth = projectal.auth_details()
        perm = projectal.User.get_permissions(auth)[5]
        self.user.link_permission(perm)
        self.user.unlink_permission(perm)

    def test_list(self):
        self.common.test_list()
