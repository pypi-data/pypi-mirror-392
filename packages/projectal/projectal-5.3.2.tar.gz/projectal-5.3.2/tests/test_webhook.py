import projectal
from tests.base_test import BaseTest


class TestWebhook(BaseTest):
    def setUp(self):
        projectal.Webhook.delete(projectal.Webhook.list())

    def test_crud(self):
        webhook = projectal.Webhook.create(
            {"entity": "TASK", "action": "UPDATE", "url": self.WEBHOOK_URL}
        )
        old = webhook
        webhook = projectal.Webhook.get(webhook)
        assert old["uuId"] == webhook["uuId"]
        webhook["url"] = "https://updates.example.com"
        projectal.Webhook.update(webhook)
        webhook = projectal.Webhook.get(webhook)
        assert old["url"] != webhook["url"]
        changed = {
            "uuId": webhook["uuId"],
            "entity": "TASK",
            "action": "UPDATE",
            "url": "https://changed.example.com",
        }
        projectal.Webhook.update(changed)

        projectal.Webhook.delete(webhook)

    def test_list(self):
        projectal.Webhook.create(
            {"entity": "TASK", "action": "CREATE", "url": self.WEBHOOK_URL}
        )
        projectal.Webhook.create(
            {"entity": "TASK", "action": "UPDATE", "url": self.WEBHOOK_URL}
        )
        projectal.Webhook.create(
            {"entity": "TASK", "action": "DELETE", "url": self.WEBHOOK_URL}
        )
        list_ = projectal.Webhook.list(start=0, limit=3)
        # server may already have some
        assert len(list_) == 3

    def test_all(self):
        # Commented out entities are not supported by design.
        all = [
            "ACCESS_POLICY",
            "ACTIVITY",
            "BOOKING",
            # "CALENDAR",
            "COMPANY",
            "CONTACT",
            "CUSTOMER",
            "DEPARTMENT",
            "STORAGE_FILE",
            # "STORAGE_FOLDER"
            "LOCATION",
            "NOTE",
            # "PERMISSION",
            "PROJECT",
            "PROJECT_TEMPLATE",
            "REBATE",
            "RESOURCE",
            "SKILL",
            "STAFF",
            "STAGE",
            "TAG",
            "TASK",
            "TASK_TEMPLATE",
            "USER",
            # "WEBHOOK",
        ]
        all_good = True
        for entity in all:
            try:
                projectal.Webhook.create(
                    {"entity": entity, "action": "CREATE", "url": self.WEBHOOK_URL}
                )
                projectal.Webhook.create(
                    {"entity": entity, "action": "UPDATE", "url": self.WEBHOOK_URL}
                )
                projectal.Webhook.create(
                    {"entity": entity, "action": "DELETE", "url": self.WEBHOOK_URL}
                )
            except Exception as e:
                print(f"Failed at: {entity}: {e}")
                all_good = False
        assert all_good

    def test_tag_add(self):
        tag = self.make_tag()
        task = self.make_task()
        task.link_tag(tag)
        task.unlink_tag(tag)
