import projectal
from projectal.enums import PayFrequency, Currency
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestResource(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Resource)

    def test_crud(self):
        new = {
            "name": "Test resource (python API wrapper)",
            "payFrequency": PayFrequency.Hourly,
            "payAmount": 345,
            "payCurrency": Currency.INR,
        }
        uuId = self.common.test_create(new)
        entity = self.common.test_get(uuId)
        changed = {
            "uuId": uuId,
            "name": "Updated resource",
            "payFrequency": PayFrequency.Monthly,
            "payAmount": 99345,
        }
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_history(self):
        resource = projectal.Resource.create(
            {
                "name": "Rebate",
                "payFrequency": PayFrequency.Hourly,
                "payAmount": 345,
                "payCurrency": Currency.RUB,
            }
        )
        resource["name"] = "History1"
        projectal.Resource.update(resource)
        assert len(resource.history()) == 2

    def test_clone(self):
        resource = projectal.Resource.create(
            {
                "name": "ResourceToClone",
                "payFrequency": PayFrequency.Hourly,
                "payAmount": 345,
                "payCurrency": Currency.RUB,
            }
        )
        uuId = resource.clone({"name": "ClonedResource"})
        clone = projectal.Resource.get(uuId)
        assert clone["uuId"] != resource["uuId"]
        assert clone["name"] == "ClonedResource"

    def test_list(self):
        self.common.test_list()

    def test_link_tag(self):
        tag = self.make_tag()
        resource = self.make_resource()
        resource.link_tag(tag)
        resource.unlink_tag(tag)

    # Reverse linkers
    def test_link_staff(self):
        resource = self.make_resource()
        resource["resourceLink"] = {"quantity": 2, "utilization": 0.3}
        staff = self.make_staff()
        resource.link_staff(staff)
        resource.unlink_staff(staff)

    def test_link_task(self):
        resource = self.make_resource()
        resource["resourceLink"] = {"quantity": 2, "utilization": 0.3}
        task = self.make_task()
        resource.link_task(task)
        resource.unlink_task(task)

    def test_link_task_template(self):
        resource = self.make_resource()
        resource["resourceLink"] = {"quantity": 2, "utilization": 0.3}
        task_template = self.make_task_template()
        resource.link_task_template(task_template)
        resource.unlink_task_template(task_template)

    # Empty linkers
    def test_link_note(self):
        resource = self.make_resource()
        note = projectal.Note.create(resource, {"text": "Note"})
        assert len(resource["noteList"]) == 1
        assert resource["noteList"][0]["uuId"] == note["uuId"]
        assert resource["noteList"][0]["text"] == note["text"]

        resource = projectal.Resource.get(resource["uuId"], links=["note"])
        projectal.Note.create(resource, {"text": "Note 2"})
        assert len(resource["noteList"]) == 2
