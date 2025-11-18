import projectal
from projectal.enums import PayFrequency, Currency
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestActivity(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Activity)
        self.activity = projectal.Activity.create({"name": "Activity"})

    def test_crud(self):
        new = {
            "identifier": "TestIdentifier",
            "name": "Test activity (python API wrapper)",
        }
        uuId = self.common.test_create(new)
        entity = self.common.test_get(uuId)

        # Change only some details
        changed = {
            "uuId": uuId,
            "identifier": "Updated identifier",
            "name": "Updated name",
        }
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_link_contact(self):
        customer = projectal.Customer.create({"name": "Holder"})
        contact = projectal.Contact.create(
            customer["uuId"],
            {
                "firstName": "First",
                "lastName": "Last",
            },
        )
        self.activity.link_contact(contact)
        self.activity.unlink_contact(contact)

    def test_link_location(self):
        location = projectal.Location.create({"name": "Location"})
        self.activity.link_location(location)
        self.activity.unlink_location(location)

    def test_link_rebate(self):
        rebate = projectal.Rebate.create({"name": "Rebate", "rebate": "0.2"})
        self.activity.link_rebate(rebate)
        self.activity.unlink_rebate(rebate)

    def test_link_resource(self):
        resource = projectal.Resource.create(
            {
                "name": "Resource",
                "payFrequency": PayFrequency.Hourly,
                "payAmount": 345,
                "payCurrency": Currency.BRL,
            }
        )
        resource["resourceLink"] = {"quantity": 2, "utilization": 0.5}
        self.activity.link_resource(resource)
        resource["resourceLink"] = {"quantity": 4, "utilization": 0.8}
        self.activity.relink_resource(resource)
        self.activity.unlink_resource(resource)

    def test_link_staff(self):
        staff = self.make_staff()
        staff["resourceLink"] = {"utilization": 0.6}
        self.activity.link_staff(staff)
        staff["resourceLink"] = {"utilization": 0.8, "duration": 2400}
        self.activity.relink_staff(staff)
        # Test the duration is saved
        activity = projectal.Activity.get(self.activity, links=["STAFF"])
        assert "duration" in activity["staffList"][0]["resourceLink"]
        assert activity["staffList"][0]["resourceLink"]["duration"] == 2400
        self.activity.unlink_staff(staff)

    def test_link_stage(self):
        stage = projectal.Stage.create({"name": "Stage"})
        self.activity.link_stage(stage)
        self.activity.unlink_stage(stage)

    def test_link_tag(self):
        tag = self.make_tag()
        self.activity.link_tag(tag)
        self.activity.unlink_tag(tag)

    def test_clone(self):
        uuId = self.activity.clone({"name": "Cloned"})
        clone = projectal.Activity.get(uuId)
        assert clone["uuId"] != self.activity["uuId"]
        assert clone["name"] == "Cloned"

    def test_list(self):
        self.common.test_list()

    def test_history(self):
        self.activity["name"] = "History1"
        projectal.Activity.update(self.activity)
        assert len(self.activity.history()) == 2
