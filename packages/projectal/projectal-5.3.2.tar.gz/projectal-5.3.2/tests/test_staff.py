import projectal
from projectal.enums import (
    StaffType,
    PayFrequency,
    DateLimit,
    SkillLevel,
    ConstraintType,
    TaskType,
    Currency,
    CalendarType,
)
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestStaff(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Staff)
        self.staff = self.make_staff()

    def test_crud(self):
        uuId = self.common.test_create(
            {
                "email": "test.staff.{}@example.com".format(self.random()),
                "firstName": "Firstname",
                "lastName": "Lastname",
                "staffType": StaffType.Consultant,
                "payFrequency": PayFrequency.Weekly,
                "payAmount": 200,
                "startDate": DateLimit.Min,
                "endDate": DateLimit.Max,
            }
        )
        entity = self.common.test_get(uuId)

        # Change only some details
        changed = {"uuId": uuId, "payAmount": 205, "lastName": "Updated lastname"}

        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_link_location(self):
        location = projectal.Location.create({"name": "Location"})
        self.staff.link_location(location)
        self.staff.unlink_location(location)

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
        self.staff.link_resource(resource)
        resource["resourceLink"] = {"quantity": 4, "utilization": 0.5}
        self.staff.relink_resource(resource)
        self.staff.unlink_resource(resource)

    def test_link_skill(self):
        skill = self.make_skill()
        skill["skillLink"] = {"level": SkillLevel.Mid}
        self.staff.link_skill(skill)
        skill["skillLink"] = {"level": SkillLevel.Senior}
        self.staff.relink_skill(skill)
        self.staff.unlink_skill(skill)

    def test_link_file(self):
        file = projectal.File.create(b"testdata", {"name": "File"})
        self.staff.link_file(file)
        self.staff.unlink_file(file)

    def test_link_tag(self):
        tag = self.make_tag()
        staff = self.make_staff()
        staff.link_tag(tag)
        staff.unlink_tag(tag)

    # Reverse linkers
    def test_link_company(self):
        company = self.make_company()
        self.staff.link_company(company)
        self.staff.unlink_company(company)

    def test_link_department(self):
        department = self.make_department()
        self.staff.link_department(department)
        self.staff.unlink_department(department)

    def test_link_task(self):
        task = self.make_task()
        self.staff["resourceLink"] = {"utilization": 0.1}
        self.staff.link_task(task)
        self.staff.unlink_task(task)

    def test_link_task_template(self):
        task_template = self.make_task_template()
        self.staff["resourceLink"] = {"utilization": 0.1}
        self.staff.link_task_template(task_template)
        self.staff.unlink_task_template(task_template)

    # Empty linkers
    def test_link_note(self):
        staff = self.make_staff()
        note = projectal.Note.create(staff, {"text": "Note"})
        assert len(staff["noteList"]) == 1
        assert staff["noteList"][0]["uuId"] == note["uuId"]
        assert staff["noteList"][0]["text"] == note["text"]

        staff = projectal.Staff.get(staff["uuId"], links=["note"])
        projectal.Note.create(staff, {"text": "Note 2"})
        assert len(staff["noteList"]) == 2

    def test_link_calendar(self):
        staff = self.make_staff()
        calendar = projectal.Calendar.create(
            staff,
            {
                "name": "calendar 1",
                "startDate": "2020-02-02",
                "endDate": "2020-02-03",
                "isWorking": False,
                "type": CalendarType.Leave,
            },
        )
        assert len(staff["calendarList"]) == 1
        assert staff["calendarList"][0]["uuId"] == calendar["uuId"]
        assert staff["calendarList"][0]["name"] == calendar["name"]

        # TODO: this needs to work
        # staff['calendarList'][0]['name'] = 'newname'
        # staff.save()
        # staff = projectal.Staff.get(staff, links=['calendar'])
        # assert staff['calendarList'][0]['name'] == 'newname'

        staff = projectal.Staff.get(staff, links=["calendar"])
        projectal.Calendar.create(
            staff,
            {
                "name": "calendar 2",
                "startDate": "2020-02-04",
                "endDate": "2020-02-05",
                "isWorking": False,
                "type": CalendarType.Leave,
            },
        )
        assert len(staff["calendarList"]) == 2

    def test_history(self):
        self.staff["lastName"] = "History1"
        projectal.Staff.update(self.staff)
        assert len(self.staff.history()) == 2

    def test_clone(self):
        uuId = self.staff.clone(
            {
                "firstName": "Cloned",
                "lastName": "Cloned",
                "email": "cloned-{}@example.com".format(self.random()),
            }
        )
        clone = projectal.Staff.get(uuId)
        assert clone["uuId"] != self.staff["uuId"]
        assert clone["firstName"] == "Cloned"

    def test_calendar(self):
        cals = projectal.Staff.calendar(self.staff["uuId"])
        assert len(cals) > 0

        # Try some date ranges
        cals = projectal.Staff.calendar(self.staff["uuId"], begin="2022-01-10")
        assert len(cals) > 0
        cals = projectal.Staff.calendar(
            self.staff["uuId"], begin="2021-08-22", until="2022-01-01"
        )
        assert len(cals) > 0

    def test_calendar_availability(self):
        cals = projectal.Staff.calendar(self.staff["uuId"])
        assert len(cals) > 0

        # Try some date ranges
        cals = projectal.Staff.calendar_availability(
            self.staff["uuId"], begin="2022-01-10"
        )
        assert len(cals) > 0
        cals = projectal.Staff.calendar_availability(
            self.staff["uuId"], begin="2021-08-22", until="2022-01-01"
        )
        assert len(cals) > 0

    def test_usage(self):
        # Delete all - this test requires fresh start of staff list
        staff = projectal.Staff.list()
        projectal.Staff.delete(staff)

        # We get project usage. Project needs a task
        project = projectal.Project.create({"name": "Project - add tasks to me"})
        task = projectal.Task.create(
            project["uuId"],
            {
                "name": "Task",
                "constraintType": ConstraintType.ASAP,
                "taskType": TaskType.Task,
            },
        )

        # And some staff assigned to it
        def make_staff():
            staff = projectal.Staff.create(
                {
                    "email": "test.staff.usage.{}@example.com".format(self.random()),
                    "firstName": "Firstname",
                    "lastName": "Lastname",
                    "staffType": StaffType.Consultant,
                    "payFrequency": PayFrequency.Weekly,
                    "payAmount": 200,
                    "startDate": DateLimit.Min,
                    "endDate": DateLimit.Max,
                }
            )
            staff["resourceLink"] = {"utilization": 0.8}
            projectal.Task.link_staff(task, staff)
            return staff

        make_staff()
        s2 = make_staff()
        make_staff()
        make_staff()
        make_staff()
        make_staff()
        make_staff()
        s8 = make_staff()

        # Minimum params is the start/end. No holder = all staff
        staffs = projectal.Staff.usage(begin="2021-01-01", until="2023-01-01")
        assert len(staffs) == 8

        staffs = projectal.Staff.usage(
            holder=project["uuId"], begin="2021-01-01", until="2023-01-01"
        )
        assert len(staffs) == 8

        # Test out all the params
        staffs = projectal.Staff.usage(
            holder=project["uuId"],
            begin="2021-01-01",
            until="2023-01-01",
            start=1,
            limit=2,
            span="Daily",
            ksort="position",
            order="desc",
        )
        assert len(staffs) == 2  # limit is 2

        # We have the option to NOT use a holder but pass in a list of staff instead
        staffs = projectal.Staff.usage(
            begin="2021-01-01", until="2023-01-01", staff=[s2, s8], span="Monthly"
        )
        assert len(staffs) == 2
        assert s2["uuId"] == staffs[0]["uuId"]
        assert s8["uuId"] == staffs[1]["uuId"]

    def test_allocation(self):
        projectal.Staff.auto_assign()

    def test_list(self):
        def make():
            projectal.Staff.create(
                {
                    "email": "staff.{}@example.com".format(self.random()),
                    "firstName": "Firstname",
                    "lastName": "LastName",
                    "staffType": StaffType.Consultant,
                    "payFrequency": PayFrequency.Weekly,
                    "payAmount": 200,
                    "startDate": DateLimit.Min,
                    "endDate": DateLimit.Max,
                }
            )

        for n in range(0, 100):
            make()
        # List as UUIDs
        staff = projectal.Staff.list()
        assert len(staff) >= 100
        # Again, with expansion
        staff = projectal.Staff.list(expand=True)
        assert isinstance(staff[0], projectal.Staff)

        # Delete them all and test listing empty
        projectal.Staff.delete(staff)
        staff = projectal.Staff.list()
        assert len(staff) == 0

    def test_generic_staff(self):
        # Nothing complex, just make sure it works
        projectal.Staff.create(
            {
                "firstName": "Generic Staff",
                "staffType": StaffType.Consultant,
                "payFrequency": PayFrequency.Weekly,
                "payAmount": 200,
                "startDate": DateLimit.Min,
                "endDate": DateLimit.Max,
                "genericStaff": True,
            }
        )

    def test_uuid_identifier(self):
        # Backend back not matching identifier when text is in uuid format
        uuid = "ea27576d-d730-48a2-9b76-0710de8f10b9"
        projectal.Staff.create(
            {
                "identifier": uuid,
                "email": "test.staff{}@example.com".format(self.random()),
                "firstName": "Firstname",
                "lastName": "Lastname",
                "staffType": StaffType.Consultant,
                "payFrequency": PayFrequency.Weekly,
                "payAmount": 200,
                "startDate": DateLimit.Min,
                "endDate": DateLimit.Max,
            }
        )
        staff = projectal.Staff.match(
            "identifier", "ea27576d-d730-48a2-9b76-0710de8f10b9"
        )
        assert staff
