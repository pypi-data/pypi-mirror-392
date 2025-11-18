import projectal
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestCustomer(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Customer)
        # Reuse for links
        self.customer = projectal.Customer.create(
            {"name": "customer", "description": "desc"}
        )

    def test_crud(self):
        new = {"name": "Test customer (python API wrapper)", "nickName": "Test Nick"}
        uuId = self.common.test_create(new)
        entity = self.common.test_get(uuId)
        changed = {"uuId": uuId, "name": "Updated customer", "nickName": "Updated Nick"}
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_link_location(self):
        location = projectal.Location.create({"name": "Location"})
        projectal.Customer.link_location(self.customer, location)
        projectal.Customer.unlink_location(self.customer, location)

    def test_link_contact(self):
        customer = projectal.Customer.create({"name": "Holder"})
        contact = projectal.Contact.create(
            customer["uuId"],
            {
                "firstName": "First",
                "lastName": "Last",
            },
        )
        projectal.Customer.link_contact(self.customer, contact)
        projectal.Customer.unlink_contact(self.customer, contact)

    def test_link_file(self):
        file = projectal.File.create(b"testdata", {"name": "File"})
        projectal.Customer.link_file(self.customer, file)
        projectal.Customer.unlink_file(self.customer, file)

    def test_link_tag(self):
        tag = self.make_tag()
        self.customer.link_tag(tag)
        self.customer.unlink_tag(tag)

    # Reverse linkers

    def test_link_project(self):
        project = self.make_project()
        self.customer.link_project(project)
        self.customer.unlink_project(project)

    # Empty linkers
    def test_link_note(self):
        note = projectal.Note.create(self.customer, {"text": "Note"})
        assert len(self.customer["noteList"]) == 1
        assert self.customer["noteList"][0]["uuId"] == note["uuId"]
        assert self.customer["noteList"][0]["text"] == note["text"]

        customer = projectal.Customer.get(self.customer, links=["note"])
        projectal.Note.create(customer, {"text": "Note 2"})
        assert len(customer["noteList"]) == 2

    def test_history(self):
        self.customer["name"] = "History1"
        projectal.Customer.update(self.customer)
        assert len(self.customer.history()) == 2

    def test_clone(self):
        uuId = self.customer.clone({"name": "Cloned"})
        clone = projectal.Customer.get(uuId)
        assert clone
        assert clone["uuId"] != self.customer["uuId"]
        assert clone["description"] == self.customer["description"]
        assert clone["name"] == "Cloned"

    def test_list(self):
        self.common.test_list()
