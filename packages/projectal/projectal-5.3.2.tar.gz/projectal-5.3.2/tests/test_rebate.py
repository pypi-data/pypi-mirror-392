import projectal
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestRebate(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Rebate)

    def test_crud(self):
        uuId = self.common.test_create(
            {"name": "Test rebate (python API wrapper)", "rebate": 0.5}
        )
        entity = self.common.test_get(uuId)
        changed = {
            "uuId": uuId,
            "name": "Updated rebate",
        }
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_history(self):
        rebate = projectal.Rebate.create({"name": "Rebate", "rebate": 0.3})
        rebate["name"] = "History1"
        projectal.Rebate.update(rebate)
        assert len(rebate.history()) == 2

    def test_clone(self):
        rebate = projectal.Rebate.create({"name": "Rebate", "rebate": 0.1})
        uuId = rebate.clone({"name": "Cloned", "rebate": 0.3})
        clone = projectal.Rebate.get(uuId)
        assert clone["uuId"] != rebate["uuId"]
        assert clone["name"] == "Cloned"

    def test_list(self):
        self.common.test_list()

    def test_link_tag(self):
        tag = self.make_tag()
        rebate = self.make_rebate()
        rebate.link_tag(tag)
        rebate.unlink_tag(tag)

    # Reverse linkers
    def test_link_project(self):
        rebate = self.make_rebate()
        project = self.make_project()
        rebate.link_project(project)

    def test_link_task(self):
        rebate = self.make_rebate()
        task = self.make_task()
        rebate.link_task(task)
        rebate.unlink_task(task)

    def test_link_task_template(self):
        rebate = self.make_rebate()
        task_template = self.make_task_template()
        rebate.link_task_template(task_template)
        rebate.unlink_task_template(task_template)

    # Empty linkers
    def test_link_note(self):
        rebate = self.make_rebate()
        note = projectal.Note.create(rebate, {"text": "Note"})
        assert len(rebate["noteList"]) == 1
        assert rebate["noteList"][0]["uuId"] == note["uuId"]
        assert rebate["noteList"][0]["text"] == note["text"]

        rebate = projectal.Rebate.get(rebate["uuId"], links=["note"])
        projectal.Note.create(rebate, {"text": "Note 2"})
        assert len(rebate["noteList"]) == 2
