import projectal
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestProjectTemplate(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.ProjectTemplate)

    def test_crud(self):
        uuId = self.common.test_create(
            {
                "name": "Test project template (python API wrapper)",
                "identifier": "123456",
            }
        )
        entity = self.common.test_get(uuId)
        changed = {
            "uuId": uuId,
            "name": "Updated project template",
            "identifier": "654321",
        }
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_history(self):
        pt = projectal.ProjectTemplate.create({"name": "PT"})
        pt["name"] = "History1"
        projectal.ProjectTemplate.update(pt)
        assert len(pt.history()) == 2

    def test_clone(self):
        pt = projectal.ProjectTemplate.create({"name": "PT"})
        uuId = pt.clone({"name": "Cloned"})
        clone = projectal.ProjectTemplate.get(uuId)
        assert clone["uuId"] != pt["uuId"]
        assert clone["name"] == "Cloned"

    @classmethod
    def test_autoschedule(cls):
        # TODO: better test
        pt = projectal.ProjectTemplate.create(
            {
                "name": "PT",
            }
        )
        assert projectal.ProjectTemplate.autoschedule(pt, mode="ALAP")

    def test_list(self):
        self.common.test_list()

    def test_link_tag(self):
        tag = self.make_tag()
        project = self.make_project_template()
        project.link_tag(tag)
        project.unlink_tag(tag)

    # Empty linkers
    def test_link_note(self):
        project = self.make_project_template()
        note = projectal.Note.create(project, {"text": "Note"})
        assert len(project["noteList"]) == 1
        assert project["noteList"][0]["uuId"] == note["uuId"]
        assert project["noteList"][0]["text"] == note["text"]

        project = projectal.ProjectTemplate.get(project["uuId"], links=["note"])
        projectal.Note.create(project, {"text": "Note 2"})
        assert len(project["noteList"]) == 2
