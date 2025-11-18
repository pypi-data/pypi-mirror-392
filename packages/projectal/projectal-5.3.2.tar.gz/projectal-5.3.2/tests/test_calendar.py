import projectal
from projectal import UnsupportedException
from projectal.enums import (
    StaffType,
    PayFrequency,
    DateLimit,
    CalendarType,
    ConstraintType,
    TaskType,
)
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestCalendar(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Calendar)
        # Need staff to serve as holder
        self.staff = self.make_staff()

    def test_crud(self):
        new = projectal.Calendar.create(
            self.staff["uuId"],
            {
                "name": "Test calendar (python API wrapper)",
                "type": CalendarType.Thursday,
                "startHour": 32400000,
                "endHour": 61200000,
            },
        )
        assert new["uuId"]
        uuId = new["uuId"]

        entity = self.common.test_get(uuId)
        changed = {
            "uuId": uuId,
            "name": "Updated calendar",
            "type": CalendarType.Working,
        }
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_list(self):
        try:
            self.common.test_list()
        except UnsupportedException:
            pass

    def test_duration(self):
        # Test building a duration for a task. Durations must take into
        # account weekends and time off from the location calendar.
        project = projectal.Project.create({"name": "Project"})
        location = projectal.Location.create({"name": "Location"})
        project.link_location(location)

        task = projectal.Task.create(
            project["uuId"],
            {
                "name": "Task",
                "constraintType": ConstraintType.ASAP,
                "taskType": TaskType.Task,
                "autoScheduling": False,
            },
        )
        task["startTime"] = projectal.timestamp_from_datetime("2022-06-01 09:00")  # Wed
        task["closeTime"] = projectal.timestamp_from_datetime("2022-06-03 17:00")  # Fri
        # Test it without passing in calendars
        task.reset_duration()
        assert task["duration"] == 3 * 480
        # Again, with calendars
        task.reset_duration(calendars=location.calendar())

        # Minus 2 days for Weekend = 5 days
        task["startTime"] = projectal.timestamp_from_datetime("2022-06-01 09:00")  # Wed
        task["closeTime"] = projectal.timestamp_from_datetime("2022-06-07 17:00")  # Tue
        task.reset_duration(location.calendar())
        assert task["duration"] == 5 * 480

        # Two weeks with one workday as holiday = 9 days
        projectal.Calendar.create(
            location,
            {
                "startDate": "2022-06-08",
                "endDate": "2022-06-08",
                "name": "Custom",
                "type": CalendarType.Leave,
            },
        )
        task["startTime"] = projectal.timestamp_from_datetime("2022-06-06 09:00")
        task["closeTime"] = projectal.timestamp_from_datetime("2022-06-17 17:00")
        task.reset_duration(location.calendar())
        assert task["duration"] == 9 * 480

        # 7 days. One day is a weekend. One day is a weekend marked as isWorking
        # = 6 days
        projectal.Calendar.create(
            location,
            {
                "startDate": "2022-07-10",
                "startHour": "32400000",
                "endDate": "2022-07-10",
                "endHour": "61200000",
                "name": "Custom",
                "type": CalendarType.Working,
                "isWorking": True,
            },
        )
        task["startTime"] = projectal.timestamp_from_datetime("2022-07-06 09:00")  # Wed
        task["closeTime"] = projectal.timestamp_from_datetime("2022-07-12 17:00")  # Tue
        task.reset_duration(location.calendar())
        assert task["duration"] == 6 * 480

        # TODO: tests for
        # Weekday exception to be isWorking=True
        # Exception being a portion of a day
