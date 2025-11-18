import projectal
from tests.base_test import BaseTest


class TestProfile(BaseTest):
    def test_crud(self):
        project = projectal.Project.create({"name": "Project"})
        key = "unittest"
        # No profile yet. Create on first access (profile always has uuid set)
        data = project.profile_get(key)
        assert isinstance(data, dict)
        assert len(data) == 1

        # Set a value on profile and check if saved.
        data["key1"] = "value1"
        project.profile_set(key, data)
        data = project.profile_get(key)
        assert isinstance(data, dict)
        assert len(data) == 2

        # Set another value on profile
        data["key2"] = "value2"
        project.profile_set(key, data)
        data = project.profile_get(key)
        assert len(data) == 3

        # Change only one value. Should still have 2 and other is unchanged.
        data["key1"] = "changed"
        project.profile_set(key, data)
        data = project.profile_get(key)
        assert len(data) == 3
        assert data["key1"] == "changed"
        assert data["key2"] == "value2"
