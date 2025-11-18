import projectal
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestBooking(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Booking)
        self.staff_one = self.make_staff()
        self.staff_two = self.make_staff()
        self.project_one = self.make_project()
        self.project_two = self.make_project()
        self.booking = projectal.Booking.create(
            {
                "staff": {"uuId": self.staff_one["uuId"]},
                "name": "Booking",
                "project": {"uuId": self.project_one["uuId"]},
            }
        )

    def test_crud(self):
        new = {
            "staff": {"uuId": self.staff_one["uuId"]},
            "identifier": "TestIdentifier",
            "name": "Test booking (python API wrapper)",
            "project": {"uuId": self.project_one["uuId"]},
        }
        uuId = self.common.test_create(new)
        entity = self.common.test_get(uuId)

        # Change only some details
        changed = {
            "uuId": uuId,
            "identifier": "Updated identifier",
            "name": "Updated name",
            "project": {"uuId": self.project_two["uuId"]},
            "staff": {"uuId": self.staff_two["uuId"]},
        }
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_link_stage(self):
        stage = projectal.Stage.create({"name": "Stage"})
        self.booking.link_stage(stage)
        self.booking.unlink_stage(stage)

    def test_link_tag(self):
        tag = self.make_tag()
        self.booking.link_tag(tag)
        self.booking.unlink_tag(tag)

    def test_clone(self):
        uuId = self.booking.clone({"name": "Cloned"})
        clone = projectal.Booking.get(uuId)
        assert clone["uuId"] != self.booking["uuId"]
        assert clone["name"] == "Cloned"

    def test_list(self):
        self.common.test_list()

    def test_history(self):
        self.booking["name"] = "History1"
        projectal.Booking.update(self.booking)
        assert len(self.booking.history()) == 3
