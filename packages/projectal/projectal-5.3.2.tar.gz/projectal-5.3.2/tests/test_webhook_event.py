import projectal
from tests.base_test import BaseTest
from projectal import UsageException, ProjectalException
import time


class TestWebhookEvent(BaseTest):
    def test_1_list(self):
        projectal.Webhook.create(
            {"entity": "PROJECT", "action": "*", "url": self.WEBHOOK_URL}
        )

        project = self.make_project()
        project.delete()

        seconds_slept = 0
        webhook_events = projectal.Webhook.list_events(
            entityId=project["uuId"], format=False
        )
        while len(webhook_events) < 2 and seconds_slept <= 20:
            time.sleep(1)
            seconds_slept += 1
            webhook_events = projectal.Webhook.list_events(
                entityId=project["uuId"], format=False
            )

        assert len(webhook_events) >= 2

    def test_get_after_project_delete(self):
        projectal.Webhook.create(
            {"entity": "PROJECT", "action": "*", "url": self.WEBHOOK_URL}
        )
        project = projectal.Project.create(
            {"name": "Project", "identifier": "customvalue"}
        )
        project.delete()

        seconds_slept = 0
        webhook_events = projectal.Webhook.list_events(
            entityId=project["uuId"], format=False
        )
        while len(webhook_events) < 2 and seconds_slept <= 20:
            time.sleep(1)
            seconds_slept += 1
            webhook_events = projectal.Webhook.list_events(
                entityId=project["uuId"], format=False
            )
        webhook = webhook_events[-1]

        deleted_project = projectal.Project.get(
            webhook["entityUuid"], deleted_at=webhook["eventTime"]
        )
        assert deleted_project["identifier"] == "customvalue"

    def test_get_after_task_delete(self):
        projectal.Webhook.create(
            {"entity": "TASK", "action": "*", "url": self.WEBHOOK_URL}
        )
        project = self.make_project()
        task = projectal.Task.create(
            project["uuId"],
            {
                "name": "Task",
                "taskType": "Task",
                "constraintType": "As_soon_as_possible",
                "identifier": "customtask",
            },
        )
        task.delete()

        seconds_slept = 0
        webhook_events = projectal.Webhook.list_events(
            entityId=task["uuId"], format=False
        )
        while len(webhook_events) < 2 and seconds_slept <= 20:
            time.sleep(1)
            seconds_slept += 1
            webhook_events = projectal.Webhook.list_events(
                entityId=task["uuId"], format=False
            )
        webhook = webhook_events[-1]

        deleted_task = projectal.Task.get(
            webhook["entityUuid"], deleted_at=webhook["eventTime"]
        )
        assert deleted_task["identifier"] == "customtask"

    def test_get_after_note_delete(self):
        projectal.Webhook.create(
            {"entity": "NOTE", "action": "*", "url": self.WEBHOOK_URL}
        )
        project = self.make_project()
        note = projectal.Note.create(
            project["uuId"], {"text": "note text", "identifier": "customnote"}
        )
        note.delete()

        seconds_slept = 0
        webhook_events = projectal.Webhook.list_events(
            entityId=note["uuId"], format=False
        )
        while len(webhook_events) < 2 and seconds_slept <= 20:
            time.sleep(1)
            seconds_slept += 1
            webhook_events = projectal.Webhook.list_events(
                entityId=note["uuId"], format=False
            )
        webhook = webhook_events[-1]

        deleted_note = projectal.Note.get(
            webhook["entityUuid"], links=["tag"], deleted_at=webhook["eventTime"]
        )
        assert deleted_note["identifier"] == "customnote"

    def test_get_deleted_at_param(self):
        project = self.make_project()
        try:
            projectal.Project.get(project["uuId"], deleted_at="abcdef")
            raise Exception("Should not reach here")
        except UsageException as e:
            assert "deleted_at must be a number" in e.args[0]
