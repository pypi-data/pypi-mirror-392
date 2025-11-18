import projectal
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestFolder(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Folder)

    def test_crud(self):
        uuId = self.common.test_create({"name": "Test folder"})
        entity = self.common.test_get(uuId)
        changed = {"uuId": uuId, "name": "Updated folder"}
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_link_folder(self):
        folder1 = projectal.Folder.create({"name": "Folder1"})
        folder2 = projectal.Folder.create({"name": "Folder2"})
        folder1.link_folder(folder2)
        folder1.unlink_folder(folder2)

    def test_link_file(self):
        folder = projectal.Folder.create({"name": "Folder1"})
        file = projectal.File.create(b"testdata", {"name": "File"})
        folder.link_file(file)
        folder.unlink_file(file)

    def test_link_tag(self):
        tag = self.make_tag()
        folder = projectal.Folder.create({"name": "Folder1"})
        folder.link_tag(tag)
        folder.unlink_tag(tag)

    # Empty linkers
    def test_link_note(self):
        folder = projectal.Folder.create({"name": "Folder1"})
        note = projectal.Note.create(folder, {"text": "Note"})
        assert len(folder["noteList"]) == 1
        assert folder["noteList"][0]["uuId"] == note["uuId"]
        assert folder["noteList"][0]["text"] == note["text"]

        folder = projectal.Folder.get(folder["uuId"], links=["note"])
        projectal.Note.create(folder, {"text": "Note 2"})
        assert len(folder["noteList"]) == 2

    def test_list(self):
        self.common.test_list()
