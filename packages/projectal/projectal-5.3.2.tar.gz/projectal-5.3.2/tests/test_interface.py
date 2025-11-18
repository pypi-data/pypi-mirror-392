from copy import copy

from projectal.enums import StaffType, PayFrequency, DateLimit, ConstraintType, TaskType

import projectal
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestProject(BaseTest):
    """
    These tests are for the interface of Entity CRUD.
    We allow: single uuid, list of uuid, single dict, list of dict

    Need to correctly detect the input choice and return the expected
    result for that type. I.e., input 1, get dict. Input list, get list.
    """

    def setUp(self):
        self.common = CommonTester(projectal.Project)
        self.project = projectal.Project.create({"name": "Project"})

    def test_create(self):
        p1 = projectal.Project.create({"name": "Test Project"})
        assert isinstance(p1, projectal.Project)

        # Input with list of 1 should return list, not dict
        p1 = projectal.Project.create([{"name": "Test Project"}])
        assert isinstance(p1, list)
        assert isinstance(p1[0], projectal.Project)

        projects = []
        for i in range(0, 5):
            projects.append({"name": "1of5"})
        projects = projectal.Project.create(projects)
        assert isinstance(projects, list)
        assert len(projects) == 5
        assert isinstance(projects[0], projectal.Project)

        # Input with empty list should return empty lst
        projects = projectal.Project.create([])
        assert isinstance(projects, list)
        assert len(projects) == 0

    def test_get(self):
        p1 = projectal.Project.create({"name": "P1"})
        p2 = projectal.Project.create({"name": "P2"})
        p3 = projectal.Project.create({"name": "P3"})
        p4 = projectal.Project.create({"name": "P4"})

        # By string uuId
        uuId = p1["uuId"]
        got = projectal.Project.get(uuId)
        assert isinstance(got, dict)
        assert got["uuId"] == uuId

        # By list of uuIds
        ids = [p["uuId"] for p in [p1, p2, p3, p4]]
        gotmany = projectal.Project.get(ids)
        assert isinstance(gotmany, list)
        assert len(gotmany) == 4
        assert isinstance(gotmany[2], projectal.Project)

        # Get one with single dict
        got = projectal.Project.get(gotmany[0])
        assert isinstance(got, projectal.Project)

        # Get many using list of dict
        gotmany = projectal.Project.get(gotmany)
        assert isinstance(gotmany, list)
        assert len(gotmany) == 4
        assert isinstance(gotmany[3], projectal.Project)

        # Input with empty list should return empty lst
        projects = projectal.Project.get([])
        assert isinstance(projects, list)
        assert len(projects) == 0

        # Entities are dicts. They must use the dict get.
        assert p1.get("notrealfield", "defaultval") == "defaultval"
        assert p1.get("notrealfield") is None

    def test_update(self):
        p1 = projectal.Project.create({"name": "P1"})
        p2 = projectal.Project.create({"name": "P2"})
        p3 = projectal.Project.create({"name": "P3"})
        p1["name"] = "new1"
        p2["name"] = "new2"
        p3["name"] = "new3"

        # Update dict
        assert projectal.Project.update(p1)

        # Update list dict
        assert projectal.Project.update([p1, p2, p3])

        got = projectal.Project.get(p2)
        assert got["name"] == "new2"

        # Entities are dicts. They must use the dict update.
        p1.update({"red": "green"})
        assert p1["red"] == "green"

        # Input with empty list should not fail
        projectal.Project.update([])

        # Instances can update themselves with save
        p2["name"] = "saved"
        p2.save()
        p = projectal.Project.get(p2)
        assert p["name"] == "saved"

    def test_delete(self):
        # Errors throw exceptions, so no need to compare anything

        # Delete uuid
        p = projectal.Project.create({"name": "P"})
        projectal.Project.delete(p["uuId"])

        # Delete dict
        p = projectal.Project.create({"name": "P"})
        projectal.Project.delete(p)

        # Delete list uuid
        p1 = projectal.Project.create({"name": "P1"})
        p2 = projectal.Project.create({"name": "P2"})

        # ['uuid1', 'uuid2']
        ids = [p["uuId"] for p in [p1, p2]]
        projectal.Project.delete(ids)

        # Delete list dict
        p1 = projectal.Project.create({"name": "P1"})
        p2 = projectal.Project.create({"name": "P2"})
        projectal.Project.delete([p1, p2])

        # Input with empty list should not fail
        projectal.Project.delete([])

        # Instances can delete themselves
        p1 = projectal.Project.create({"name": "P1"})
        assert p1.delete()

    def test_link_typing(self):
        # When getting an entity with links, the objects in the
        # link list should be typed
        r1 = projectal.Rebate.create({"name": "Rebate", "rebate": 0.3})
        r2 = projectal.Rebate.create({"name": "Rebate", "rebate": 0.3})
        r3 = projectal.Rebate.create({"name": "Rebate", "rebate": 0.3})
        project = projectal.Project.create({"name": "Project"})
        project.link_rebate(r1)
        project.link_rebate(r2)
        project.link_rebate(r3)
        project = projectal.Project.get(project, links=["REBATE"])
        assert isinstance(project["rebateList"][0], projectal.Rebate)

        # Some links are not lists. Test Stage is correctly typed.
        # Create state and add to project
        stage = self.make_stage()
        stage2 = self.make_stage()
        project["stageList"] = [stage, stage2]
        project.save()

        # stage_list should be typed to Stage
        project = projectal.Project.get(project, links=["stage_list"])
        assert isinstance(project["stageList"][0], projectal.Stage)

        # Now add it to the task
        task = self.make_task(project)
        task["stage"] = stage
        task.save()
        task = projectal.Task.get(task, links=["stage"])
        assert isinstance(task["stage"], projectal.Stage)

    def test_link_cache_after_change(self):
        # When modifying entity links, the entity object's list of links should
        # also be updated to match what was sent to the server.
        project = projectal.Project.create({"name": "Project"})
        task = projectal.Task.create(
            project["uuId"],
            {
                "identifier": "TestIdentifier",
                "constraintType": ConstraintType.ASAP,
                "name": "Test task (python API wrapper)",
                "taskType": TaskType.Task,
            },
        )
        staff = projectal.Staff.create(
            {
                "email": "test.staff.{}@example.com".format(self.random()),
                "firstName": "1",
                "lastName": "1",
                "staffType": StaffType.Consultant,
                "payFrequency": PayFrequency.Weekly,
                "payAmount": 200,
                "startDate": DateLimit.Min,
                "endDate": DateLimit.Max,
            }
        )
        staff["resourceLink"] = {"utilization": 0.1}

        # We should have an empty staffList
        task = projectal.Task.get(task, links=["STAFF"])
        assert "staffList" in task
        assert len(task["staffList"]) == 0

        # Link staff. staffList should now have it without fetching again
        task.link_staff(staff)
        assert len(task["staffList"]) == 1
        assert task["staffList"][0]["uuId"] == staff["uuId"]

        #  Let's add another two.
        staff2 = projectal.Staff.create(
            {
                "email": "test.staff.{}@example.com".format(self.random()),
                "firstName": "2",
                "lastName": "2",
                "staffType": StaffType.Consultant,
                "payFrequency": PayFrequency.Weekly,
                "payAmount": 200,
                "startDate": DateLimit.Min,
                "endDate": DateLimit.Max,
            }
        )
        staff2["resourceLink"] = {"utilization": 0.2}
        staff3 = projectal.Staff.create(
            {
                "email": "test.staff.{}@example.com".format(self.random()),
                "firstName": "3",
                "lastName": "3",
                "staffType": StaffType.Consultant,
                "payFrequency": PayFrequency.Weekly,
                "payAmount": 200,
                "startDate": DateLimit.Min,
                "endDate": DateLimit.Max,
            }
        )
        staff3["resourceLink"] = {"utilization": 0.3}
        task.link_staff(staff2)
        task.link_staff(staff3)
        assert len(task["staffList"]) == 3

        # Update staff2. Order stays the same, utilization is changed
        staff2["resourceLink"] = {"utilization": 0.9}
        task.relink_staff(staff2)

        assert len(task["staffList"]) == 3
        assert task["staffList"][0]["uuId"] == staff["uuId"]
        assert task["staffList"][1]["uuId"] == staff2["uuId"]
        assert task["staffList"][1]["resourceLink"]["utilization"] == 0.9
        assert task["staffList"][2]["uuId"] == staff3["uuId"]

        # Delete staff2. Order stays the same, staff spliced out
        task.unlink_staff(staff2)
        assert len(task["staffList"]) == 2
        assert task["staffList"][0]["uuId"] == staff["uuId"]
        assert task["staffList"][1]["uuId"] == staff3["uuId"]

        # Test deleting when not fetched with links
        department = projectal.Department.create({"name": "Department"})
        department.link_staff(staff)
        department = projectal.Department.get(department)
        department.unlink_staff(staff)

    def test_partial_updates(self):
        # Test scenarios where we save an entity we fetched
        p1 = projectal.Project.create({"name": "P1"})
        p2 = projectal.Project.create({"name": "P2"})
        p3 = projectal.Project.create({"name": "P3"})

        # Change nothing (do nothing)
        p2 = projectal.Project.get(p2)
        p2.save()

        # Add new field
        p3 = projectal.Project.get(p3)
        p3["description"] = "new val"
        p3.save()

        # Change 1 existing field
        p3 = projectal.Project.get(p3)
        p3["description"] = "changed val"
        p3.save()

        # Save many, but only 1 has changes in it
        p1 = projectal.Project.get(p1)
        p2 = projectal.Project.get(p2)
        p3 = projectal.Project.get(p3)
        p3["name"] = "new name"
        projectal.Project.update([p1, p2, p3])

        # Pass in a list of changes directly
        changes = {
            "uuId": p3["uuId"],
            "name": "custom name",
            "description": "custom desc",
        }
        projectal.Project.update(changes)

    def test_chunking(self):
        # Start fresh
        projectal.Location.delete(projectal.Location.list())

        # Set chunk size to 20 to make tests quicker
        cs = projectal.chunk_size_read = projectal.chunk_size_write = 20

        # Create 0
        projectal.Location.create([])
        assert len(projectal.Location.list()) == 0

        # Create 1
        projectal.Location.create({"name": "Location"})
        assert len(projectal.Location.list()) == 1
        projectal.Location.delete(projectal.Location.list())

        # One less
        stash = [{"name": "Location%d" % n} for n in range(0, 1000)]
        projectal.Location.create(stash[: cs - 1])
        assert len(projectal.Location.list()) == cs - 1
        projectal.Location.delete(projectal.Location.list())

        # Exact
        stash = [{"name": "Location%d" % n} for n in range(0, 1000)]
        projectal.Location.create(stash[:cs])
        assert len(projectal.Location.list()) == cs
        projectal.Location.delete(projectal.Location.list())

        # One more
        stash = [{"name": "Location%d" % n} for n in range(0, 1000)]
        projectal.Location.create(stash[: cs + 1])
        assert len(projectal.Location.list()) == cs + 1
        projectal.Location.delete(projectal.Location.list())

        # x4 (80 items)
        stash = [{"name": "Location%d" % n} for n in range(0, 1000)]
        projectal.Location.create(stash[: cs * 4])
        assert len(projectal.Location.list()) == cs * 4

        # Test the other functions at least once. Assume the logic is reused and is correct.
        # We have 80 items
        got = projectal.Location.get(projectal.Location.list())
        assert len(got) == 80
        # Update them and check if they all got updated
        map = {}
        for g in got:
            map[g["uuId"]] = copy(g)
            g["name"] = g["name"] + "2"

        projectal.Location.update(got)
        got = projectal.Location.get(projectal.Location.list())
        for g in got:
            assert map[g["uuId"]]["name"] + "2" == g["name"]

        # Delete them
        projectal.Location.delete(projectal.Location.list())
        assert len(projectal.Location.list()) == 0
