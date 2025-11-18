import projectal
from projectal.enums import CalendarType
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestLocation(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Location)

    def test_crud(self):
        uuId = self.common.test_create(
            {"name": "Test location (python API wrapper)", "postcode": "6666"}
        )
        entity = self.common.test_get(uuId)
        changed = {"uuId": uuId, "name": "Updated location", "postcode": "4242"}
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_history(self):
        location = projectal.Location.create({"name": "Location"})
        location["name"] = "History1"
        projectal.Location.update(location)
        assert len(location.history()) == 2

    def test_clone(self):
        location = projectal.Location.create({"name": "Location"})
        uuId = location.clone({"name": "Cloned"})
        clone = projectal.Location.get(uuId)
        assert clone["uuId"] != location["uuId"]
        assert clone["name"] == "Cloned"

    def test_calendar(self):
        location = projectal.Location.create({"name": "Location"})
        cals = location.calendar()
        assert len(cals) > 0

        # Try some date ranges
        cals = location.calendar(begin="2022-01-10")
        assert len(cals) > 0
        cals = location.calendar(begin="2021-08-22", until="2022-01-01")
        assert len(cals) > 0

    def test_list(self):
        self.common.test_list()

    def test_link_tag(self):
        tag = self.make_tag()
        location = self.make_location()
        location.link_tag(tag)
        location.unlink_tag(tag)

    # Reverse linkers
    def test_link_company(self):
        location = self.make_location()
        company = self.make_company()
        location.link_company(company)
        location.unlink_company(company)

    def test_link_customer(self):
        location = self.make_location()
        customer = projectal.Customer.create({"name": "Holder"})
        location.link_customer(customer)
        location.unlink_customer(customer)

    def test_link_project(self):
        location = self.make_location()
        project = self.make_project()
        location.link_project(project)
        location.unlink_project(project)

    def test_link_staff(self):
        location = self.make_location()
        staff = self.make_staff()
        location.link_staff(staff)
        location.unlink_staff(staff)

    # Empty linkers
    def test_link_note(self):
        location = self.make_location()
        note = projectal.Note.create(location, {"text": "Note"})
        assert len(location["noteList"]) == 1
        assert location["noteList"][0]["uuId"] == note["uuId"]
        assert location["noteList"][0]["text"] == note["text"]

        location = projectal.Location.get(location["uuId"], links=["note"])
        projectal.Note.create(location, {"text": "Note 2"})
        assert len(location["noteList"]) == 2

    def test_link_calendar(self):
        location = self.make_location()
        calendar = projectal.Calendar.create(
            location,
            {
                "name": "calendar 1",
                "startDate": "2020-02-02",
                "endDate": "2020-02-03",
                "isWorking": False,
                "type": CalendarType.Leave,
            },
        )
        assert len(location["calendarList"]) == 1
        assert location["calendarList"][0]["uuId"] == calendar["uuId"]
        assert location["calendarList"][0]["name"] == calendar["name"]

        location = projectal.Location.get(location, links=["calendar"])
        projectal.Calendar.create(
            location,
            {
                "name": "calendar 2",
                "startDate": "2020-02-04",
                "endDate": "2020-02-05",
                "isWorking": False,
                "type": CalendarType.Leave,
            },
        )
        assert len(location["calendarList"]) == 2
