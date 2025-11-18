import projectal
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestNote(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Note)
        self.project = projectal.Project.create(
            {
                "name": "API test (for notes)",
            }
        )

    def test_crud(self):
        new = projectal.Note.create(
            self.project["uuId"], {"text": "This is a note for testing"}
        )
        assert new["uuId"]
        uuId = new["uuId"]
        entity = self.common.test_get(uuId)
        changed = {"uuId": uuId, "text": "New text"}
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_list(self):
        # Ensure we have one
        projectal.Note.create(
            self.project["uuId"], {"text": "This is a note for testing"}
        )
        self.common.test_list()

    def test_link_tag(self):
        tag = self.make_tag()
        note = projectal.Note.create(
            self.project["uuId"], {"text": "This is a note for testing"}
        )

        note.link_tag(tag)
        note.unlink_tag(tag)

    def test_readonly_on_create(self):
        # Notes have references to their holders that we must insert upon creation.
        # The server doesn't tell us in the response.
        project = self.make_project()

        note = projectal.Note.create(project, {"text": "a note"})
        note_got = projectal.Note.get(note)

        assert note_got["author"] == note["author"]
        assert note_got["authorRef"] == note["authorRef"]
        assert note_got["holderRef"] == note["holderRef"]
        assert note_got["created"] == note["created"]
        assert note_got["modified"] == note["modified"]
