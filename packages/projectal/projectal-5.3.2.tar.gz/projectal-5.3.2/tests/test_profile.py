import projectal
from tests.base_test import BaseTest


class TestProfile(BaseTest):
    def test_profiles(self):
        project = projectal.Project.create({"name": "Project"})
        category = "profiletest"
        folder = "project"

        # Should return a profile with uuId on first access
        profile = projectal.profile.get(category, folder, project["uuId"])
        assert isinstance(profile, dict)
        assert len(profile.keys()) == 1
        assert "uuId" in profile

        # Should auto-create and populate profile on first write
        project2 = projectal.Project.create({"name": "Project"})
        data = {"keyhere": "valuehere"}
        profile = projectal.profile.set(category, folder, project2["uuId"], data)
        assert "keyhere" in profile
        # Setting again should overwrite first one
        data = {"second": "second"}
        projectal.profile.set(category, folder, project2["uuId"], data)

        # Get should give us the latest write
        profile = projectal.profile.get(category, folder, project2["uuId"])
        assert profile["second"] == "second"
