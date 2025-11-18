import projectal
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestStage(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Stage)

    def test_crud(self):
        new = {
            "name": "Test stage (python API wrapper)",
            "description": "A description",
        }
        uuId = self.common.test_create(new)
        entity = self.common.test_get(uuId)
        changed = {
            "uuId": uuId,
            "name": "Updated stage",
            "description": "New description!",
        }
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_history(self):
        stage = projectal.Stage.create({"name": "Stage"})
        stage["name"] = "History1"
        projectal.Stage.update(stage)
        assert len(stage.history()) == 2

    def test_clone(self):
        stage = projectal.Stage.create({"name": "Stage"})
        uuId = stage.clone({"name": "Cloned"})
        clone = projectal.Stage.get(uuId)
        assert clone["uuId"] != stage["uuId"]
        assert clone["name"] == "Cloned"

    def test_list(self):
        self.common.test_list()

    def test_link_tag(self):
        tag = self.make_tag()
        stage = self.make_stage()
        stage.link_tag(tag)
        stage.unlink_tag(tag)

    # Reverse links
    def test_link_project(self):
        stage = self.make_stage()
        project = self.make_project()
        stage.link_project(project)
        stage.unlink_project(project)

    def test_link_task(self):
        stage = self.make_stage()
        project = self.make_project()
        project.link_stage_list([stage])
        task = self.make_task(project)
        stage.link_task(task)
        stage.unlink_task(task)
