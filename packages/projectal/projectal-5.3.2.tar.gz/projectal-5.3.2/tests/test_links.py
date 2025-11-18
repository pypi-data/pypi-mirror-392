import logging

import projectal
from projectal import ProjectalException, UsageException
from projectal.enums import (
    StaffType,
    PayFrequency,
    DateLimit,
    SkillLevel,
    Currency,
    ConstraintType,
    TaskType,
    CompanyType,
)
from tests.base_test import BaseTest


class LinksTest(BaseTest):
    """
    These tests are for the interface of entity links. This library provides
    an abstraction on top of the links APIs and automatically performs conflict
    resolution to determine the appropriate add/remove/update API calls to
    perform in order to result in a matching link list on the server.

    Things to test:
    - Direct linking in bulk (with object, list, dict: same as Entity)
    - Conflict resolution
    - Tracking if we have fetched with or without the link
        - Fetching the links if not (network request)
    - Tracking if the entity is New to avoid fetching attempt
    - Stripping payload on requests
    - Linking during entity creation (and cache updates for it)

    We will use skills as our test link because it has data in it, so it's
    more complex than most.
    """

    def test_bulk(self):
        staff = self.make_staff()

        # Single
        skill1 = self.make_skill("Skill1")
        staff.link_skill(skill1)

        staff = projectal.Staff.get(staff, links=["SKILL"])
        assert len(staff["skillList"]) == 1

        # List
        skill2 = self.make_skill("Skill2")
        skill3 = self.make_skill("Skill3")
        skill4 = self.make_skill("Skill4")
        staff.link_skill([skill2, skill3, skill4])
        staff = projectal.Staff.get(staff, links=["SKILL"])
        assert len(staff["skillList"]) == 4

        # Dict instead of object
        skill5 = self.make_skill("Skill5")
        staff.link_skill(
            {"uuId": skill5["uuId"], "skillLink": {"level": SkillLevel.Senior}}
        )
        staff = projectal.Staff.get(staff, links=["SKILL"])
        assert len(staff["skillList"]) == 5

    def test_conflict_resolution(self):
        staff = self.make_staff()
        staff = projectal.Staff.get(staff, links=["SKILL"])

        # Start by setting a new list

        skill1 = self.make_skill("Skill1")
        skill2 = self.make_skill("Skill2")
        skill3 = self.make_skill("Skill3")
        skill4 = self.make_skill("Skill4")

        staff["skillList"] = [skill1, skill2, skill3, skill4]
        staff.save()
        staff = projectal.Staff.get(staff, links=["SKILL"])
        assert len(staff["skillList"]) == 4

        # For these tests, we test the cached representation
        # as well as what the server comes back with. Should
        # be the same. Note: the order from the server is
        # not guaranteed, so don't rely on it.

        # Set new list with two removed
        staff["skillList"] = [skill2, skill4]
        staff.save()
        assert len(staff["skillList"]) == 2
        assert staff["skillList"][0]["uuId"] == skill2["uuId"]
        assert staff["skillList"][1]["uuId"] == skill4["uuId"]
        staff = projectal.Staff.get(staff, links=["SKILL"])
        assert len(staff["skillList"]) == 2
        assert skill2["uuId"] in [s["uuId"] for s in staff["skillList"]]
        assert skill4["uuId"] in [s["uuId"] for s in staff["skillList"]]

        # Set new list with 1 remove and 2 add
        staff["skillList"] = [skill2, skill1, skill3]
        staff.save()
        assert len(staff["skillList"]) == 3
        assert staff["skillList"][0]["uuId"] == skill2["uuId"]
        assert staff["skillList"][1]["uuId"] == skill1["uuId"]
        assert staff["skillList"][2]["uuId"] == skill3["uuId"]
        staff = projectal.Staff.get(staff, links=["SKILL"])
        assert len(staff["skillList"]) == 3
        assert skill2["uuId"] in [s["uuId"] for s in staff["skillList"]]
        assert skill1["uuId"] in [s["uuId"] for s in staff["skillList"]]
        assert skill3["uuId"] in [s["uuId"] for s in staff["skillList"]]

        # Update the data property of the link (not the entity itself)
        skill3["skillLink"]["level"] = SkillLevel.Senior
        staff["skillList"] = [skill2, skill1, skill3]
        staff.save()
        assert len(staff["skillList"]) == 3
        for skill in staff["skillList"]:
            if skill["uuId"] == skill3["uuId"]:
                assert skill["skillLink"]["level"] == SkillLevel.Senior
        staff = projectal.Staff.get(staff, links=["SKILL"])
        assert len(staff["skillList"]) == 3
        for skill in staff["skillList"]:
            if skill["uuId"] == skill3["uuId"]:
                assert skill["skillLink"]["level"] == SkillLevel.Senior

        # Change two lists in the same save
        staff = projectal.Staff.get(staff, links=["skill", "location"])
        staff["skillList"] = [skill1, skill2, skill3]
        staff["locationList"] = [self.make_location(), self.make_location()]
        staff.save()
        staff = projectal.Staff.get(staff, links=["skill", "location"])
        assert len(staff["skillList"]) == 3
        assert len(staff["locationList"]) == 2

    def test_links_on_create(self):
        # Links should be created with the entity if part of the initial data
        project = projectal.Project.create(
            {
                "name": "Project",
                "locationList": [self.make_location(), self.make_location()],
            }
        )
        project = projectal.Project.get(project, links=["LOCATION"])
        assert len(project["locationList"]) == 2

        # Test again, but start with an Entity (we may enforce this in future)
        project = projectal.Project(
            {
                "name": "Project 2",
                "locationList": [self.make_location(), self.make_location()],
            }
        )
        project = projectal.Project.create(project)
        project = projectal.Project.get(project, links=["LOCATION"])
        assert len(project["locationList"]) == 2

        # Test links that aren't lists (the API complains about these
        # if they are part of the payload). In general, we should not
        # be sending links as part of the payload anyway, regardless
        # of the type.
        project = self.make_project()
        stage = self.make_stage()
        project["stageList"] = [stage]
        project.save()

        # If we include 'stage', API returns 'Property "stage" is only for reading'.
        # The payload must strip it.
        projectal.Task.create(
            project,
            {
                "constraintType": ConstraintType.ASAP,
                "name": "Task",
                "taskType": TaskType.Task,
                "duration": 1000,
                "stage": stage,
            },
        )

    def test_circular_ref(self):
        # Links can be full objects with all sorts of references, including
        # the linking object. This causes a JSON serialization error due to
        # a circular reference. We need a strategy to avoid this. We should
        # only send over the uuId and the data attribute of the link (if it
        # has one).
        # As a bonus, this completely strips the payload of anything unrelated.

        company = projectal.Company.create(
            {"name": "C", "type": CompanyType.Contractor}
        )
        staff = projectal.Staff.create(
            {
                "email": "test.staff.link.{}@example.com".format(self.random()),
                "firstName": "FirstName",
                "lastName": "Lastname",
                "staffType": StaffType.Consultant,
                "payFrequency": PayFrequency.Weekly,
                "payAmount": 600,
                "startDate": "2020-03-04",
                "endDate": DateLimit.Max,
            }
        )
        # This is one way to trigger it
        staff["companyList"] = [company]
        company.link_staff(staff)
        try:
            company.link_staff(staff)
        except ProjectalException as e:
            assert "already_have_edge" in e.message.lower()

    def test_link_data_updates(self):
        # Tests for each of the "inner" data dictionaries that could exist within links.
        # Update them in various ways.

        # --- Set up entities first
        skill = self.make_skill("Skill")
        staff = self.make_staff()
        resource = self.make_resource()
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
        # --- Do tests
        # Skill (starts as intermediate)
        task.link_skill(skill)
        skill = projectal.Skill.get(skill)
        skill["skillLink"] = {"level": SkillLevel.Senior}
        task["skillList"] = [skill]
        task.save()
        task = projectal.Task.get(task, links=["SKILL", "RESOURCE"])
        assert task["skillList"][0]["skillLink"]["level"] == SkillLevel.Senior

        # Resource
        resource["resourceLink"] = {"quantity": 2, "utilization": 0.3}
        task.link_resource(resource)
        resource = projectal.Resource.get(resource)
        resource["resourceLink"] = {"quantity": 5, "utilization": 0.6}
        task["resourceList"] = [resource]
        task.save()
        task = projectal.Task.get(task, links=["RESOURCE"])
        assert task["resourceList"][0]["resourceLink"]["quantity"] == 5
        assert task["resourceList"][0]["resourceLink"]["utilization"] == 0.6

        # Staff
        resource1 = self.make_resource()
        resource2 = self.make_resource()
        resource3 = self.make_resource()
        resource1["resourceLink"] = {"quantity": 1, "utilization": 0.1}
        resource2["resourceLink"] = {"quantity": 2, "utilization": 0.2}
        resource3["resourceLink"] = {"quantity": 3, "utilization": 0.3}
        staff["resourceList"] = [resource1, resource2, resource3]
        staff.save()
        staff = projectal.Staff.get(staff, links=["RESOURCE"])
        for r in staff["resourceList"]:
            rl = r["resourceLink"]
            if r["uuId"] == resource1["uuId"]:
                rl["quantity"] = 1
                rl["utilization"] = 0.1
            if r["uuId"] == resource2["uuId"]:
                rl["quantity"] = 2
                rl["utilization"] = 0.2
            if r["uuId"] == resource3["uuId"]:
                rl["quantity"] = 3
                rl["utilization"] = 0.3
        staff.save()
        for r in staff["resourceList"]:
            rl = r["resourceLink"]
            if r["uuId"] == resource1["uuId"]:
                assert rl["quantity"] == resource1["resourceLink"]["quantity"]
                assert rl["utilization"] == resource1["resourceLink"]["utilization"]
            if r["uuId"] == resource2["uuId"]:
                assert rl["quantity"] == resource2["resourceLink"]["quantity"]
                assert rl["utilization"] == resource2["resourceLink"]["utilization"]
            if r["uuId"] == resource3["uuId"]:
                assert rl["quantity"] == resource3["resourceLink"]["quantity"]
                assert rl["utilization"] == resource3["resourceLink"]["utilization"]
        staff = projectal.Staff.get(staff, links=["RESOURCE"])
        for r in staff["resourceList"]:
            rl = r["resourceLink"]
            if r["uuId"] == resource1["uuId"]:
                assert rl["quantity"] == resource1["resourceLink"]["quantity"]
                assert rl["utilization"] == resource1["resourceLink"]["utilization"]
            if r["uuId"] == resource2["uuId"]:
                assert rl["quantity"] == resource2["resourceLink"]["quantity"]
                assert rl["utilization"] == resource2["resourceLink"]["utilization"]
            if r["uuId"] == resource3["uuId"]:
                assert rl["quantity"] == resource3["resourceLink"]["quantity"]
                assert rl["utilization"] == resource3["resourceLink"]["utilization"]

        # Task - todo
        # TaskTemplate - todo

    def test_link_data_reuse(self):
        """
        Test change detection when the change is made within the existing object
        instead of setting a new object/dict entirely. We have to keep track of
        the old link data as well in order to pull this off.
        """

        skill = self.make_skill("Skill")
        staff = self.make_staff()
        skill["skillLink"] = {"level": SkillLevel.Junior}
        staff.link_skill(skill)

        # Get a fresh copy
        task = projectal.Staff.get(staff, links=["SKILL"])
        # Change the inner link data and save
        task["skillList"][0]["skillLink"]["level"] = SkillLevel.Mid
        task.save()
        # Make sure the change was recognized
        task = projectal.Staff.get(staff, links=["SKILL"])
        assert task["skillList"][0]["skillLink"]["level"] == SkillLevel.Mid

    def test_auto_fetch(self):
        skill1 = self.make_skill("Skill1")
        skill2 = self.make_skill("Skill2")
        skill3 = self.make_skill("Skill3")
        skill4 = self.make_skill("Skill4")
        skill5 = self.make_skill("Skill5")

        staff = self.make_staff()
        staff["skillList"] = [skill1, skill2, skill3, skill4]
        with self.assertLogs(level=logging.WARN) as ctx:
            # This should be the only warning logged
            logging.warning("placeholder")
            staff.save()
        assert len(ctx.output) == 1

        # Get a fresh copy of staff but fetch without skill links
        # This should issue a fetch only with the missing link
        staff = projectal.Staff.get(staff, links=["LOCATION"])

        # Now set a new list which contains a remove, update, and add
        skill3["skillLink"] = {"level": SkillLevel.Senior}
        with self.assertLogs() as ctx:
            # This should internally fetch the skill list and resolve conflicts
            # without us noticing. A warning is logged for the developer.
            staff["skillList"] = [skill2, skill3, skill5]
            staff.save()

        assert "Fetching STAFF again with missing links: skill" in [
            r.message for r in ctx.records
        ]

        # Now fetch again with links. We should match our new list
        staff = projectal.Staff.get(staff, links=["SKILL"])
        assert skill2["uuId"] in [s["uuId"] for s in staff["skillList"]]
        assert skill3["uuId"] in [s["uuId"] for s in staff["skillList"]]
        assert skill5["uuId"] in [s["uuId"] for s in staff["skillList"]]
        assert SkillLevel.Senior in [
            s["skillLink"]["level"]
            for s in staff["skillList"]
            if s["uuId"] == skill3["uuId"]
        ]

    def test_dupe_in_list(self):
        staff = self.make_staff()
        skill1 = self.make_skill("Skill1")
        skill2 = self.make_skill("Skill2")
        staff["skillList"] = [skill1, skill2, skill1]
        try:
            staff.save()
        except projectal.UsageException as e:
            assert e.args[0] == "Duplicate skill in skillList"

    def test_link_as_dict(self):
        # Some links like project stage manifest as dicts instead of
        # lists of dicts. Test our handling of these cases

        # Start with nothing and add
        project = projectal.Project.create({"name": "Project"})
        stage = projectal.Stage.create({"name": "Stage"})
        project["stage"] = stage
        project.save()

        # Set to same
        stage = projectal.Stage.get(stage)
        project["stage"] = stage
        project.save()

        # Set to different
        stage2 = projectal.Stage.create({"name": "Stage2"})
        project["stage"] = stage2
        project.save()
        project = projectal.Project.get(project, links=["STAGE"])
        assert project["stage"]["uuId"] == stage2["uuId"]

        # Set to None
        project["stage"] = None
        project.save()
        project = projectal.Project.get(project, links=["STAGE"])
        assert project.get("stage") is None

        # Test direct links since caching behavior differs to lists
        project.link_stage(stage2)
        assert project["stage"]["uuId"] == stage2["uuId"]
        project.unlink_stage(stage2)
        assert project.get("stage") is None

    def test_link_wrong_type(self):
        # Throw informative exceptions when link type is wrong

        project = projectal.Project.create({"name": "Project"})
        stage = projectal.Stage.create({"name": "Stage"})

        # Expect list, give dict
        try:
            project["stageList"] = stage
            project.save()
        except projectal.UsageException as e:
            assert "Expecting 'stageList' to be" in e.args[0]

        # Expect list, give None
        try:
            project = projectal.Project.get(project, links=["STAGE_LIST"])
            project["stageList"] = None
            project.save()
        except projectal.UsageException as e:
            assert "Expecting 'stageList' to be" in e.args[0]

        # Expect dict, give list
        try:
            project = projectal.Project.get(project, links=["STAGE"])
            project["stage"] = [stage]
            project.save()
        except projectal.UsageException as e:
            assert "Expecting 'stage' to be" in e.args[0]

        # Expect dict, give None (this is allowed)
        project["stage"] = None
        project.save()

    def test_get_list_invalid(self):
        # Throw an exception if a requested link fetch is not valid
        task = self.make_task()
        # Empty is fine
        task = projectal.Task.get(task, links=[])
        assert task

        # All valid
        task = projectal.Task.get(task, links=["rebate", "skill"])
        assert task

        # Some invalid
        try:
            projectal.Task.get(task, links=["rebate", "invalid"])
            raise Exception("Should not reach here")
        except UsageException as e:
            assert "invalid" in e.args[0]

        # Valid, but not correct format
        try:
            projectal.Task.get(task, links=["rebate, skill"])
            raise Exception("Should not reach here")
        except UsageException as e:
            assert "invalid" in e.args[0]

        # Must be alist
        try:
            projectal.Task.get(task, links="rebate")
            raise Exception("Should not reach here")
        except UsageException as e:
            assert "list" in e.args[0]

    def test_history_report(self):
        # Test the changes method. It should report changes in the object if
        # the links list has changed or if fields within the link data have
        # changed.

        staff = self.make_staff()
        staff = projectal.Staff.get(staff, links=["SKILL"])
        # No changes yet
        changes = staff.changes()
        assert len(changes) == 0

        # Change only a basic field
        staff["lastName"] = "changes"
        changes = staff.changes()
        assert len(changes) == 1
        assert "lastName" in changes

        # Change a link list as well
        skill1 = self.make_skill("Skill1")
        skill2 = self.make_skill("Skill2")

        staff["skillList"] = [skill1, skill2]
        changes = staff.changes()

        assert len(changes) == 2
        assert "skillList" in changes

        # Be sure to test changes to a link of type dict instead of list
        task = self.make_task()
        stage = self.make_stage()
        changes = task.changes()
        assert len(changes) == 0
        task["stage"] = stage
        changes = task.changes()
        assert len(changes) == 1
        assert "stage" in changes

    def test_history_report_format(self):
        # Test the content of the changes dict when links and link data changes.
        # We want to know exactly what changed, not the full list of objects each time.

        resource1 = self.make_resource("Resource1")
        resource2 = self.make_resource("Resource2")
        resource3 = self.make_resource("Resource3")
        resource4 = self.make_resource("Resource4")

        resource1["resourceLink"] = {"utilization": 0.1, "quantity": 1}
        resource2["resourceLink"] = {"utilization": 0.2, "quantity": 2}
        resource3["resourceLink"] = {"utilization": 0.3, "quantity": 3}
        resource4["resourceLink"] = {"utilization": 0.4, "quantity": 4}

        staff = self.make_staff()
        staff = projectal.Staff.get(staff, links=["RESOURCE"])

        # No changes yet
        changes = staff.changes()
        assert len(changes) == 0

        # Add three skills.
        staff["resourceList"] = [resource1, resource2, resource3]
        changes = staff.changes()

        # We always have these three change lists for links
        assert "added" in changes["resourceList"]
        assert "removed" in changes["resourceList"]
        assert "updated" in changes["resourceList"]

        # We just added 3
        assert len(changes["resourceList"]["added"]) == 3
        assert len(changes["resourceList"]["removed"]) == 0
        assert len(changes["resourceList"]["updated"]) == 0

        # Update values inside two of them.
        staff.save()
        resource1["resourceLink"]["utilization"] = 0.9
        resource3["resourceLink"]["quantity"] = 8
        changes = staff.changes()
        assert len(changes["resourceList"]["added"]) == 0
        assert len(changes["resourceList"]["removed"]) == 0
        assert len(changes["resourceList"]["updated"]) == 2

        # Drill down into the changeset of the data attribute
        for updated in changes["resourceList"]["updated"]:
            if updated["uuId"] == resource1["uuId"]:
                assert "utilization" in updated["resourceLink"]
                assert len(updated["resourceLink"]) == 1
                assert updated["resourceLink"]["utilization"]["old"] == 0.1
                assert updated["resourceLink"]["utilization"]["new"] == 0.9

            if updated["uuId"] == resource3["uuId"]:
                assert "quantity" in updated["resourceLink"]
                assert len(updated["resourceLink"]) == 1
                assert updated["resourceLink"]["quantity"]["old"] == 3
                assert updated["resourceLink"]["quantity"]["new"] == 8

        # Remove a resource
        staff.save()
        del staff["resourceList"][1]
        changes = staff.changes()
        assert len(changes["resourceList"]["added"]) == 0
        assert len(changes["resourceList"]["removed"]) == 1
        assert len(changes["resourceList"]["updated"]) == 0

        # All 3 at once
        staff.save()
        resource3["resourceLink"]["quantity"] = 5
        staff["resourceList"] = [resource3, resource4]
        changes = staff.changes()
        assert len(changes["resourceList"]["added"]) == 1
        assert len(changes["resourceList"]["removed"]) == 1
        assert len(changes["resourceList"]["updated"]) == 1

        # Test changes to entities with no data attribute
        tag = projectal.Tag.create({"name": self.random()})
        staff["tagList"] = [tag]
        changes = staff.changes()
        assert "tagList" in changes
        assert len(changes["tagList"]["added"][0]) == 2  # UUID and Name only

        # Entities with no name attribute
        projectal.Note.create(staff, {"text": "here is a note"})
        staff["noteList"] = []
        changes = staff.changes()
        assert "noteList" in changes

    def test_dict_autotyping(self):
        # Test passing in a dict instead of an Entity.
        # We internally do the conversion since we know the type
        staff = self.make_staff()
        company = self.make_company()
        company.link_staff({"uuId": staff["uuId"]})
        assert len(company["staffList"]) == 1

        # Test with Access Policy, because its name has an _ in it
        ap = projectal.AccessPolicy.create({"name": "AP"})
        auth = projectal.auth_details()
        perm = projectal.User.get_permissions(auth)[0]
        ap.link_permission({"uuId": perm["uuId"]})

    def test_reverse_link(self):
        # There's only one link method to cater to both sides of the
        # relationship. We automatically use the right one regardless
        # of which entity is saving the link.

        # This is the standard method from the api
        staff = self.make_staff()
        # primary company is linked by default, unlink it to test linking new company
        staff.unlink_company(projectal.Company.get_primary_company())
        company = projectal.Company.create(
            {"name": "C1", "type": CompanyType.Subsidiary}
        )
        company["staffList"] = [staff]
        company.save()
        staff = projectal.Staff.get(staff, links=["COMPANY"])
        company = projectal.Company.get(company, links=["STAFF"])
        assert len(staff["companyList"]) == 1
        assert len(company["staffList"]) == 1

        # This is the reverse link. There is no official staff->company link api
        staff = self.make_staff()
        staff.unlink_company(projectal.Company.get_primary_company())
        company = projectal.Company.create(
            {"name": "C2", "type": CompanyType.Affiliate}
        )
        staff["companyList"] = [company]
        staff.save()
        staff = projectal.Staff.get(staff, links=["company"])
        company = projectal.Company.get(company, links=["staff"])
        assert len(staff["companyList"]) == 1
        assert len(company["staffList"]) == 1

        # Do it again, but pass in a list. Internally it does these 1 API call at a time.
        # No other way for now.
        staff = self.make_staff()
        staff.unlink_company(projectal.Company.get_primary_company())
        company1 = self.make_company()
        company2 = self.make_company()
        company3 = self.make_company()
        staff["companyList"] = [company1, company3, company2]
        staff.save()
        staff = projectal.Staff.get(staff, links=["company"])
        company1 = projectal.Company.get(company1, links=["staff"])
        company2 = projectal.Company.get(company2, links=["staff"])
        company3 = projectal.Company.get(company3, links=["staff"])
        assert len(staff["companyList"]) == 3
        assert len(company1["staffList"]) == 1
        assert len(company2["staffList"]) == 1
        assert len(company3["staffList"]) == 1

        # Reverse link, but use directly
        staff = self.make_staff()
        staff.unlink_company(projectal.Company.get_primary_company())
        company = self.make_company()
        staff.link_company(company)
        assert len(staff["companyList"]) == 1

        # Reverse link, but pass in dict instead of Entity
        staff = self.make_staff()
        staff.unlink_company(projectal.Company.get_primary_company())
        company = self.make_company()
        staff.link_company({"uuId": company["uuId"]})
        assert len(staff["companyList"]) == 1

    def test_empty_exists(self):
        # The backend may not return a key:value for links that we ask for
        # if there are no links. It would be saner if it returned an empty
        # list or a null value. Since we know what links we are asking for
        # and what its expected type is, we can add in defaults ourselves.
        staff = self.make_staff()
        staff = projectal.Staff.get(staff, links=["location", "task"])
        assert staff._link_def_by_name["location"]["link_key"] in staff
        assert staff._link_def_by_name["task"]["link_key"] in staff

        task = self.make_task()
        task = projectal.Task.get(task, links=["resource", "skill", "file", "stage"])
        assert task._link_def_by_name["resource"]["link_key"] in task
        assert task._link_def_by_name["skill"]["link_key"] in task
        assert task._link_def_by_name["file"]["link_key"] in task
        assert task._link_def_by_name["stage"]["link_key"] in task

        # Types
        assert len(task[task._link_def_by_name["skill"]["link_key"]]) == 0
        assert task[task._link_def_by_name["stage"]["link_key"]] is None

    def test_get_available_links(self):
        # Get a list of entity names that are available for linking by this library.
        # I.e., our validator will reject anything not in this list.
        try:
            projectal.Staff.get(projectal.Staff.list(), links=["user"])
            raise Exception("Should not reach here")
        except UsageException as e:
            assert "invalid" in e.args[0]

        links = projectal.Staff.get_link_definitions()
        assert "skill" in links
        assert "user" not in links

        # None of the links we claim to exist should throw an error when fetching with them
        projectal.Staff.get(projectal.Staff.list(), links=links.keys())
