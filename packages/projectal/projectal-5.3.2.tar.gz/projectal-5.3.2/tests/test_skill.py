import projectal
from projectal.enums import SkillLevel
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestSkill(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Skill)

    def test_crud(self):
        new = {
            "name": "Test skill (python API wrapper)",
            "skillLevels": [
                {"kind": SkillLevel.Senior, "data": 5.0},
                {"kind": SkillLevel.Mid, "data": 6.0},
                {"kind": SkillLevel.Junior, "data": 7.0},
            ],
        }
        uuId = self.common.test_create(new)
        entity = self.common.test_get(uuId)
        changed = {
            "uuId": uuId,
            "name": "Updated skill",
        }
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_history(self):
        skill = self.make_skill()
        skill["name"] = "History1"
        projectal.Skill.update(skill)
        assert len(skill.history()) == 2

    def test_clone(self):
        skill = self.make_skill()
        uuId = skill.clone({"name": "Cloned"})
        clone = projectal.Skill.get(uuId)
        assert clone["uuId"] != skill["uuId"]
        assert clone["name"] == "Cloned"

    def test_list(self):
        self.common.test_list()

    def test_link_tag(self):
        tag = self.make_tag()
        skill = self.make_skill()
        skill.link_tag(tag)
        skill.unlink_tag(tag)

    # Reverse linkers
    def test_link_staff(self):
        skill = self.make_skill()
        staff = self.make_staff()
        skill.link_staff(staff)
        skill.unlink_staff(staff)

    def test_link_task(self):
        skill = self.make_skill()
        task = self.make_task()
        skill.link_task(task)
        skill.unlink_task(task)

    def test_link_task_template(self):
        skill = self.make_skill()
        task_template = self.make_task_template()
        skill.link_task_template(task_template)
        skill.unlink_task_template(task_template)
