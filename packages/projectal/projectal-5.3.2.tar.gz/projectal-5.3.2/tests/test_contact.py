import projectal
from tests.base_test import BaseTest

from tests.common import CommonTester


class TestContact(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Contact)
        # Need customer to serve as holder
        self.customer = projectal.Customer.create({"name": "Holder"})

    def test_crud(self):
        new = projectal.Contact.create(
            self.customer["uuId"],
            {"firstName": "First", "lastName": "Last", "position": "Custom position"},
        )
        assert new["uuId"]
        uuId = new["uuId"]

        entity = self.common.test_get(uuId)
        changed = {"uuId": uuId, "position": "Updated position"}
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_history(self):
        contact = projectal.Contact.create(
            self.customer["uuId"],
            {
                "firstName": "First",
                "lastName": "Last",
            },
        )
        contact["firstName"] = "History1"
        projectal.Contact.update(contact)
        assert len(contact.history()) == 3

    def test_clone(self):
        contact = projectal.Contact.create(
            self.customer["uuId"],
            {
                "firstName": "First",
                "lastName": "Last",
            },
        )
        location = projectal.Location.create({"name": "Location"})
        uuId = projectal.Contact.clone(
            contact["uuId"],
            location["uuId"],
            {"firstName": "Cloned", "lastName": "Cloned"},
        )
        clone = projectal.Contact.get(uuId)
        assert clone["uuId"] != contact["uuId"]
        assert clone["firstName"] == "Cloned"

    def test_list(self):
        self.common.test_list()

    def test_link_tag(self):
        contact = self.make_contact()
        tag = self.make_tag()
        contact.link_tag(tag)
        contact.unlink_tag(tag)

    # Reverse linkers

    def test_link_company(self):
        contact = self.make_contact()
        company = self.make_company()
        contact.link_company(company)
        contact.unlink_company(company)

    def test_link_customer(self):
        contact = self.make_contact()
        customer = projectal.Customer.create({"name": "Holder"})
        contact.link_customer(customer)
        contact.unlink_customer(customer)

    # Empty linkers
    def test_link_note(self):
        contact = self.make_contact()
        note = projectal.Note.create(contact, {"text": "Note"})
        assert len(contact["noteList"]) == 1
        assert contact["noteList"][0]["uuId"] == note["uuId"]
        assert contact["noteList"][0]["text"] == note["text"]

        contact = projectal.Contact.get(contact, links=["note"])
        projectal.Note.create(contact, {"text": "Note 2"})
        assert len(contact["noteList"]) == 2
