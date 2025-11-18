import projectal
from projectal import ProjectalException
from tests.base_test import BaseTest


class TestAlias(BaseTest):
    def test_alias(self):
        user = self.make_user()
        # Should not work yet - user doesn't have permission
        try:
            projectal.api_alias = user["uuId"]
            resource = projectal.Resource.create({"name": "new resource!"})
        except ProjectalException as e:
            assert e.response.status_code == 403
        finally:
            projectal.api_alias = None

        # Try again with permission
        perms = projectal.Permission.list()
        alias_perm = perms["AUTHORING_AS_ALIAS_USER"]
        user.link_permission(alias_perm)

        # Only active users can be aliased
        response = user.register()
        registration = response["jobClue"]
        user.set_password("DLsdkjl#@$", registration["tokenId"])

        projectal.api_alias = user["uuId"]
        resource = self.make_resource()
        resource["name"] = "updated"
        resource.save()

        staff = self.make_staff()
        resource["resourceLink"] = {"quantity": 2, "utilization": 0.3}
        resource.link_staff(staff)

        # Check history for aliased user
        for event in resource.history():
            assert event["user"]["uuId"] == user["uuId"]
            assert event["user"]["aliasRef"] == projectal.api_auth_details["uuId"]
