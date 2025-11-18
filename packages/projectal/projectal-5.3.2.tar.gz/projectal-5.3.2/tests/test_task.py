import projectal
from projectal.enums import (
    TaskType,
    ConstraintType,
    PayFrequency,
    Currency,
    SkillLevel,
    GanttLinkType,
)
from projectal.errors import ProjectalException
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestTask(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Task)
        self.project = projectal.Project.create(
            {
                "name": "API test (for tasks)",
            }
        )
        self.task = projectal.Task.create(
            self.project["uuId"],
            {
                "identifier": "TestIdentifier",
                "constraintType": ConstraintType.ASAP,
                "name": "Test task (python API wrapper)",
                "taskType": TaskType.Task,
                "duration": 1000,
            },
        )

    def test_crud(self):
        new = projectal.Task.create(
            self.project["uuId"],
            {
                "identifier": "TestIdentifier",
                "constraintType": ConstraintType.ASAP,
                "name": "Test task (python API wrapper)",
                "taskType": TaskType.Task,
            },
        )
        assert new["uuId"]
        uuId = new["uuId"]
        entity = self.common.test_get(uuId)

        # Change only some details
        changed = {"uuId": uuId, "name": "Updated task", "taskType": TaskType.Milestone}
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_parents(self):
        # Create a 5-task hierarchy
        holder = self.project["uuId"]

        def make(name, parent=None):
            task = {
                "name": name,
                "taskType": TaskType.Task,
                "constraintType": ConstraintType.ASAP,
            }
            if parent:
                task["parent"] = parent["uuId"]
            return projectal.Task.create(holder, task)

        p1 = make("Parent 1")
        p2 = make("Parent 2", p1)
        p3 = make("Parent 3", p2)
        p4 = make("Parent 4", p3)
        p5 = make("Parent 5", p4)

        # Test the immediate parent from payload
        assert p2["uuId"] == p3["parent"]

        # From Parent 1, no parents
        parents = p1.parents()
        assert len(parents) == 0

        # From Parent 3, has parents 1-2
        parents = p3.parents()
        assert len(parents) == 2
        assert parents[0][1] == p1["uuId"]
        assert parents[1][1] == p2["uuId"]

        # From Child 5, has parents 1-4
        parents = p5.parents()
        assert len(parents) == 4
        assert parents[0][1] == p1["uuId"]
        assert parents[1][1] == p2["uuId"]
        assert parents[2][1] == p3["uuId"]
        assert parents[3][1] == p4["uuId"]

        # Parent deletes children
        projectal.Task.delete(p1)

    def test_get_project_id(self):
        holder = self.project["uuId"]
        task = {
            "name": "Task",
            "taskType": TaskType.Task,
            "constraintType": ConstraintType.ASAP,
        }
        task = projectal.Task.create(holder, task)
        assert task.project_uuId() == holder

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
        self.task.link_resource(resource)
        resource["resourceLink"] = {"quantity": 4, "utilization": 0.5}
        self.task.relink_resource(resource)
        self.task.unlink_resource(resource)

    def test_link_skill(self):
        skill = self.make_skill()
        skill["skillLink"] = {"level": SkillLevel.Mid}
        self.task.link_skill(skill)
        skill["skillLink"] = {"level": SkillLevel.Senior}
        self.task.relink_skill(skill)
        self.task.unlink_skill(skill)

    def test_link_file(self):
        file = projectal.File.create(b"testdata", {"name": "File"})
        self.task.link_file(file)
        self.task.unlink_file(file)

    def test_link_stage(self):
        stage = projectal.Stage.create({"name": "Stage"})
        # Can only link stages that the parent project is
        # also linked to, so link it first
        self.project.link_stage_list([stage])
        self.task.link_stage(stage)
        self.task.unlink_stage(stage)

    def test_link_staff(self):
        staff = self.make_staff()
        staff["resourceLink"] = {"utilization": 0.6}
        self.task.link_staff(staff)
        staff["resourceLink"] = {"utilization": 0.8, "duration": 2400}
        self.task.relink_staff(staff)
        # Test the duration is saved
        task = projectal.Task.get(self.task, links=["STAFF"])
        assert "duration" in task["staffList"][0]["resourceLink"]
        assert task["staffList"][0]["resourceLink"]["duration"] == 2400
        self.task.unlink_staff(staff)

    def test_link_rebate(self):
        rebate = projectal.Rebate.create({"name": "Rebate", "rebate": "0.2"})
        self.task.link_rebate(rebate)
        self.task.unlink_rebate(rebate)

    def test_history(self):
        self.task["name"] = "History1"
        projectal.Task.update(self.task)
        assert len(self.task.history()) == 2

    def test_link_predecessor_task(self):
        other = projectal.Task.create(
            self.project["uuId"],
            {
                "constraintType": ConstraintType.ASAP,
                "name": "Other Task",
                "taskType": TaskType.Task,
            },
        )
        other["planLink"] = {"lag": 5, "type": GanttLinkType.StartToFinish}
        self.task.link_predecessor_task(other)
        other["planLink"] = {"lag": 3, "type": GanttLinkType.StartToStart}
        self.task.relink_predecessor_task(other)
        self.task.unlink_predecessor_task(other)

        # fetching self.task with links should now be empty
        task_fetch_with_links = projectal.Task.get(
            self.task["uuId"], links=["PREDECESSOR_TASK"]
        )
        assert len(task_fetch_with_links["taskList"]) == 0

        # Test link one task without planLink -> Should throw exception
        pred_task_no_planlink = projectal.Task.create(
            self.project["uuId"],
            {
                "constraintType": ConstraintType.ASAP,
                "name": "pred_task_no_planlink",
                "taskType": TaskType.Task,
            },
        )
        try:
            task_fetch_with_links.link_predecessor_task(pred_task_no_planlink)
        except KeyError as e:
            # Make sure the KeyError is for the expected key
            assert e.args[0] == "planLink"

        # Test pred task containing planLink key but missing required field
        pred_task_bad_planlink = projectal.Task.create(
            self.project["uuId"],
            {
                "constraintType": ConstraintType.ASAP,
                "name": "pred_task_bad_planlink",
                "taskType": TaskType.Task,
            },
        )
        pred_task_bad_planlink["planLink"] = {}
        try:
            task_fetch_with_links.link_predecessor_task(pred_task_bad_planlink)
        except ProjectalException as e:
            assert e.message.startswith("UNPROCESSABLE_ENTITY - Clue: Cannot_be_blank")

        # Test linking one task with planLink using link method -> Should succeed
        pred_task_with_planlink_1 = projectal.Task.create(
            self.project["uuId"],
            {
                "constraintType": ConstraintType.ASAP,
                "name": "pred_task_no_planlink_1",
                "taskType": TaskType.Task,
            },
        )
        pred_task_with_planlink_1["planLink"] = {
            "lag": 1,
            "type": GanttLinkType.FinishToStart,
        }
        task_fetch_with_links.link_predecessor_task(pred_task_with_planlink_1)

        task_fetch_with_links = projectal.Task.get(
            self.task["uuId"], links=["PREDECESSOR_TASK"]
        )
        assert len(task_fetch_with_links["taskList"]) == 1

        # Test linking one task with planLink by appending to taskList, calling save() -> Should succeed
        pred_task_with_planlink_2 = projectal.Task.create(
            self.project["uuId"],
            {
                "constraintType": ConstraintType.ASAP,
                "name": "pred_task_no_planlink_2",
                "taskType": TaskType.Task,
            },
        )
        pred_task_with_planlink_2["planLink"] = {
            "lag": 2,
            "type": GanttLinkType.FinishToStart,
        }
        task_fetch_with_links["taskList"].append(pred_task_with_planlink_2)
        task_fetch_with_links.save()

        task_fetch_with_links = projectal.Task.get(
            self.task["uuId"], links=["PREDECESSOR_TASK"]
        )
        assert len(task_fetch_with_links["taskList"]) == 2

        # Test linking multiple tasks with planLink using link method -> Should succeed
        pred_task_with_planlink_3 = projectal.Task.create(
            self.project["uuId"],
            {
                "constraintType": ConstraintType.ASAP,
                "name": "pred_task_no_planlink_3",
                "taskType": TaskType.Task,
            },
        )
        pred_task_with_planlink_3["planLink"] = {
            "lag": 3,
            "type": GanttLinkType.FinishToStart,
        }
        pred_task_with_planlink_4 = projectal.Task.create(
            self.project["uuId"],
            {
                "constraintType": ConstraintType.ASAP,
                "name": "pred_task_no_planlink_4",
                "taskType": TaskType.Task,
            },
        )
        pred_task_with_planlink_4["planLink"] = {
            "lag": 4,
            "type": GanttLinkType.FinishToStart,
        }
        task_fetch_with_links.link_predecessor_task(
            [pred_task_with_planlink_3, pred_task_with_planlink_4]
        )

        task_fetch_with_links = projectal.Task.get(
            self.task["uuId"], links=["PREDECESSOR_TASK"]
        )
        assert len(task_fetch_with_links["taskList"]) == 4

        # Test linking multiple tasks with planLink by appending to taskList, calling save() -> Should succeed
        pred_task_with_planlink_5 = projectal.Task.create(
            self.project["uuId"],
            {
                "constraintType": ConstraintType.ASAP,
                "name": "pred_task_no_planlink_5",
                "taskType": TaskType.Task,
            },
        )
        pred_task_with_planlink_5["planLink"] = {
            "lag": 5,
            "type": GanttLinkType.FinishToStart,
        }
        pred_task_with_planlink_6 = projectal.Task.create(
            self.project["uuId"],
            {
                "constraintType": ConstraintType.ASAP,
                "name": "pred_task_no_planlink_6",
                "taskType": TaskType.Task,
            },
        )
        pred_task_with_planlink_6["planLink"] = {
            "lag": 6,
            "type": GanttLinkType.FinishToStart,
        }
        task_fetch_with_links["taskList"].append(pred_task_with_planlink_5)
        task_fetch_with_links["taskList"].append(pred_task_with_planlink_6)
        task_fetch_with_links.save()

        task_fetch_with_links = projectal.Task.get(
            self.task["uuId"], links=["PREDECESSOR_TASK"]
        )
        assert len(task_fetch_with_links["taskList"]) == 6

        # Check that the data attributes are present for all tasks in taskList
        # and match the original lag value as well
        for task in task_fetch_with_links["taskList"]:
            assert "planLink" in task
            if task["uuId"] == pred_task_with_planlink_1["uuId"]:
                assert (
                    task["planLink"]["lag"]
                    == pred_task_with_planlink_1["planLink"]["lag"]
                )
            if task["uuId"] == pred_task_with_planlink_2["uuId"]:
                assert (
                    task["planLink"]["lag"]
                    == pred_task_with_planlink_2["planLink"]["lag"]
                )
            if task["uuId"] == pred_task_with_planlink_3["uuId"]:
                assert (
                    task["planLink"]["lag"]
                    == pred_task_with_planlink_3["planLink"]["lag"]
                )
            if task["uuId"] == pred_task_with_planlink_4["uuId"]:
                assert (
                    task["planLink"]["lag"]
                    == pred_task_with_planlink_4["planLink"]["lag"]
                )
            if task["uuId"] == pred_task_with_planlink_5["uuId"]:
                assert (
                    task["planLink"]["lag"]
                    == pred_task_with_planlink_5["planLink"]["lag"]
                )
            if task["uuId"] == pred_task_with_planlink_6["uuId"]:
                assert (
                    task["planLink"]["lag"]
                    == pred_task_with_planlink_6["planLink"]["lag"]
                )

        # Test mutating taskList links then saving, see if they are correct after fetching again:

        # changing lag data attribute
        for task in task_fetch_with_links["taskList"]:
            if task["uuId"] == pred_task_with_planlink_1["uuId"]:
                # change lag from 1 to 0
                task["planLink"]["lag"] = 0
                break
        task_fetch_with_links.save()

        task_fetch_with_links = projectal.Task.get(
            self.task["uuId"], links=["PREDECESSOR_TASK"]
        )
        for task in task_fetch_with_links["taskList"]:
            if task["uuId"] == pred_task_with_planlink_1["uuId"]:
                assert task["planLink"]["lag"] == 0
                break

        # changing type data attribute
        for task in task_fetch_with_links["taskList"]:
            if task["uuId"] == pred_task_with_planlink_2["uuId"]:
                # change type from FinishToStart to StartToFinish
                task["planLink"]["type"] = GanttLinkType.StartToFinish
                break
        task_fetch_with_links.save()

        task_fetch_with_links = projectal.Task.get(
            self.task["uuId"], links=["PREDECESSOR_TASK"]
        )
        for task in task_fetch_with_links["taskList"]:
            if task["uuId"] == pred_task_with_planlink_2["uuId"]:
                assert task["planLink"]["type"] == GanttLinkType.StartToFinish
                break

        task_fetch_with_links["taskList"].pop(0)
        task_fetch_with_links.save()
        task_fetch_with_links = projectal.Task.get(
            self.task["uuId"], links=["PREDECESSOR_TASK"]
        )
        assert len(task_fetch_with_links["taskList"]) == 5

    def test_link_tag(self):
        tag = self.make_tag()
        task = self.make_task()
        task.link_tag(tag)
        task.unlink_tag(tag)

    # Empty linkers
    def test_link_note(self):
        task = self.make_task()
        note = projectal.Note.create(task, {"text": "Note"})
        assert len(task["noteList"]) == 1
        assert task["noteList"][0]["uuId"] == note["uuId"]
        assert task["noteList"][0]["text"] == note["text"]

        task = projectal.Task.get(task["uuId"], links=["note"])
        projectal.Note.create(task, {"text": "Note 2"})
        assert len(task["noteList"]) == 2

    # def test_clone(self):
    #     uuId = projectal.Task.clone(self.task['uuId'], {
    #         'name': 'Cloned',
    #     })
    #     clone = projectal.Task.get(uuId)
    #     assert clone['uuId'] != self.task['uuId']
    #     assert clone['name'] == 'Cloned'
    #

    def test_add_task_template(self):
        project = projectal.Project.create(
            {
                "name": "999Project",
                "scheduleStart": "1642809600000",
                "scheduleFinish": "1643587200000",
            }
        )

        p_template = projectal.ProjectTemplate.create({"name": "Project Template"})
        projectal.TaskTemplate.create(
            p_template["uuId"],
            {
                "name": "Task Template",
                "startTime": "1642751600000",
                "closeTime": "1642787400000",
                "constraintType": ConstraintType.ASAP,
                "taskType": TaskType.Milestone,
            },
        )

        # Insert project template into project
        # Note: it's in the task api
        projectal.Task.add_task_template(project, p_template)

        # TODO: Need to test carry-over of fields on insert

    def test_list(self):
        self.common.test_list()

    def test_date_time(self):
        task = projectal.Task.create(
            self.project["uuId"],
            {
                "constraintType": ConstraintType.ASAP,
                "name": "Other Task",
                "taskType": TaskType.Task,
                "autoScheduling": False,
            },
        )

        # Date can be set with date string, no time
        task["startTime"] = "2022-03-18"
        task.save()
        task = projectal.Task.get(task)
        assert task["startTime"] == projectal.timestamp_from_date("2022-03-18")

        # Date can be a timestamp
        ts = projectal.timestamp_from_date("2022-03-20")
        task["startTime"] = ts
        task.save()
        task = projectal.Task.get(task)
        assert task["startTime"] == ts

    def test_delete_all(self):
        projectal.Task.delete(projectal.Task.list())

    def test_readonly_on_create(self):
        # Tasks should always refer to their parent and project. We don't get this information
        # from the creation api method, but we can insert them ourselves because we know what
        # they are.
        project = self.make_project()

        # Create without parent = project is parent
        task = projectal.Task.create(
            project,
            {
                "constraintType": ConstraintType.ASAP,
                "name": "Test task",
                "taskType": TaskType.Task,
            },
        )
        assert "projectRef" in task
        assert "parent" in task
        assert task["projectRef"] == project["uuId"]
        assert task["parent"] == project["uuId"]

        # Create with parent = parent differs from projectRef
        task2 = projectal.Task.create(
            project,
            {
                "constraintType": ConstraintType.ASAP,
                "name": "Test task",
                "taskType": TaskType.Task,
                "parent": task["uuId"],
            },
        )
        assert "projectRef" in task
        assert "parent" in task
        assert task2["projectRef"] == project["uuId"]
        assert task2["parent"] == task["uuId"]

        # And they should NOT be marked as changes. They are readonly
        assert len(task2.changes()) == 0
