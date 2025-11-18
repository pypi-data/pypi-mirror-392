import projectal
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestTag(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Tag)

    def test_crud(self):
        uuId = self.common.test_create(
            {
                "name": "Test Tag (python API wrapper)",
                "color": "#FF8800",
                "description": "A tag for testing",
                "identifier": "tag-3231",
            }
        )
        entity = self.common.test_get(uuId)
        changed = {
            "uuId": uuId,
            "name": "Updated Tag",
        }
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_history(self):
        tag = projectal.Tag.create({"name": "Tag"})
        tag["name"] = "History1"
        projectal.Tag.update(tag)
        assert len(tag.history()) == 2

    def test_clone(self):
        projectal.Tag.delete(projectal.Tag.list())

        tag = projectal.Tag.create({"name": "cloneme", "description": "3333"})
        uuId = tag.clone({"name": "Cloned"})
        clone = projectal.Tag.get(uuId)
        assert clone["uuId"] != tag["uuId"]
        assert clone["name"] == "Cloned"
        assert clone["description"] == "3333"

    def test_list(self):
        self.common.test_list()
