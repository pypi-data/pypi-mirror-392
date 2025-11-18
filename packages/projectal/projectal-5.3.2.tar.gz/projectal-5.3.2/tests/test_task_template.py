import projectal
from projectal.enums import (
    PayFrequency,
    SkillLevel,
    GanttLinkType,
    Currency,
    TaskType,
    ConstraintType,
)
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestTaskTemplate(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.TaskTemplate)
        # Need project template to serve as holder
        self.project_template = projectal.ProjectTemplate.create(
            {
                "name": "Holder",
            }
        )
        self.task_template = self.make_task_template(self.project_template)

    def test_crud(self):
        new = projectal.TaskTemplate.create(
            self.project_template,
            {
                "name": "Test task template (python API wrapper)",
                "identifier": "123456",
                "taskType": TaskType.Project,
                "constraintType": ConstraintType.ASAP,
            },
        )
        assert new["uuId"]
        uuId = new["uuId"]

        entity = self.common.test_get(uuId)
        changed = {
            "uuId": uuId,
            "name": "Updated task template",
            "identifier": "654321",
        }
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_link_resource(self):
        resource = projectal.Resource.create(
            {
                "name": "Resource",
                "payFrequency": PayFrequency.Hourly,
                "payAmount": 345,
                "payCurrency": Currency.BRL,
            }
        )
        resource["resourceLink"] = {"quantity": 2, "utilization": 0.3}
        self.task_template.link_resource(resource)
        resource["resourceLink"] = {"quantity": 4, "utilization": 0.5}
        self.task_template.relink_resource(resource)
        self.task_template.unlink_resource(resource)

    def test_link_skill(self):
        skill = self.make_skill()
        skill["skillLink"] = {"level": SkillLevel.Mid}
        self.task_template.link_skill(skill)
        skill["skillLink"] = {"level": SkillLevel.Senior}
        self.task_template.relink_skill(skill)
        self.task_template.unlink_skill(skill)

    def test_link_file(self):
        file = projectal.File.create(b"testdata", {"name": "File"})
        self.task_template.link_file(file)
        self.task_template.unlink_file(file)

    def test_link_staff(self):
        staff = self.make_staff()
        staff["resourceLink"] = {"utilization": 0.6}
        self.task_template.link_staff(staff)
        staff["resourceLink"] = {"utilization": 0.8}
        self.task_template.relink_staff(staff)
        self.task_template.unlink_staff(staff)

    def test_link_rebate(self):
        rebate = projectal.Rebate.create({"name": "Rebate", "rebate": "0.2"})
        self.task_template.link_rebate(rebate)
        self.task_template.unlink_rebate(rebate)

    def test_history(self):
        self.task_template["name"] = "History1"
        projectal.TaskTemplate.update(self.task_template)
        assert len(self.task_template.history()) == 2

    def test_link_predecessor_task(self):
        other = self.make_task_template(self.project_template)
        other["planLink"] = {"lag": 5, "type": GanttLinkType.StartToFinish}
        projectal.TaskTemplate.link_predecessor_task(self.task_template, other)
        other["planLink"] = {"lag": 3, "type": GanttLinkType.StartToStart}
        projectal.TaskTemplate.relink_predecessor_task(self.task_template, other)
        projectal.TaskTemplate.unlink_predecessor_task(self.task_template, other)

    def test_link_tag(self):
        tag = self.make_tag()
        task = self.make_task_template()
        task.link_tag(tag)
        task.unlink_tag(tag)

    # Empty linkers
    def test_link_note(self):
        task = self.make_task_template()
        note = projectal.Note.create(task, {"text": "Note"})
        assert len(task["noteList"]) == 1
        assert task["noteList"][0]["uuId"] == note["uuId"]
        assert task["noteList"][0]["text"] == note["text"]

        task = projectal.TaskTemplate.get(task["uuId"], links=["note"])
        projectal.Note.create(task, {"text": "Note 2"})
        assert len(task["noteList"]) == 2

    def test_clone(self):
        uuId = self.task_template.clone(self.project_template, {"name": "Cloned"})
        clone = projectal.TaskTemplate.get(uuId)
        assert clone["uuId"] != self.task_template["uuId"]
        assert clone["name"] == "Cloned"

    def test_list(self):
        self.common.test_list()
