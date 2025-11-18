import zipfile
from io import BytesIO

import projectal
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestFile(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.File)

    def test_crud(self):
        file_data = b"binary data goes here"
        # Create
        new = projectal.File.create(
            file_data, {"name": "filename.txt", "description": "anything"}
        )
        assert new["uuId"]

        # Get entity
        file = projectal.File.get(new["uuId"])
        assert new["uuId"] == file["uuId"]

        # Get file data and compare
        downloaded = projectal.File.get_file_data(new["uuId"])
        assert downloaded == file_data

        # Update entity, no file
        file["name"] = "new name"
        file["description"] = "new desc"
        projectal.File.update(file)
        file = projectal.File.get(file["uuId"])
        assert file["name"] == "new name"
        assert file["description"] == "new desc"
        # Data is the same
        downloaded = projectal.File.get_file_data(new["uuId"])
        assert downloaded == file_data

        # Update entity, new file
        file_data = b"new file"
        file["name"] = "new data"
        projectal.File.update(file, file_data=file_data)
        file = projectal.File.get(file["uuId"])
        assert file["name"] == "new data"
        # File data is new data
        downloaded = projectal.File.get_file_data(new["uuId"])
        assert downloaded == file_data

        # Raw response object. Not useful for API, but still need to test
        response = projectal.File.download_to_browser(file["uuId"])
        assert response.content == file_data

        projectal.File.delete(file["uuId"])

    def test_download_zip(self):
        file1 = projectal.File.create(b"file1data", {"name": "file1.data"})
        file2 = projectal.File.create(b"file2data", {"name": "file2.data"})
        zip = projectal.File.download_multiple([file1, file2])
        assert zipfile.is_zipfile(BytesIO(zip))

    def test_history(self):
        file = projectal.File.create(b"file1data", {"name": "file1.data"})
        file["description"] = "new desc 321"
        projectal.File.update(file)
        assert len(file.history()) == 2

    def test_list(self):
        self.common.test_list()

    def test_link_tag(self):
        tag = self.make_tag()
        file = projectal.File.create(b"file1data", {"name": "file1.data"})
        file.link_tag(tag)
        file.unlink_tag(tag)

    # Reverse linkers
    def test_link_company(self):
        file = projectal.File.create(b"file1data", {"name": "file1.data"})
        company = self.make_company()
        file.link_company(company)
        file.unlink_company(company)

    def test_link_customer(self):
        file = projectal.File.create(b"file1data", {"name": "file1.data"})
        customer = projectal.Customer.create({"name": "Holder"})
        file.link_customer(customer)
        file.unlink_customer(customer)

    def test_link_folder(self):
        file = projectal.File.create(b"file1data", {"name": "file1.data"})
        folder = projectal.Folder.create({"name": "Folder"})
        file.link_folder(folder)
        file.unlink_folder(folder)

    def test_link_project(self):
        file = projectal.File.create(b"file1data", {"name": "file1.data"})
        project = self.make_project()
        file.link_project(project)
        file.unlink_project(project)

    def test_link_staff(self):
        file = projectal.File.create(b"file1data", {"name": "file1.data"})
        staff = self.make_staff()
        file.link_staff(staff)
        file.unlink_staff(staff)

    def test_link_task(self):
        file = projectal.File.create(b"file1data", {"name": "file1.data"})
        task = self.make_task()
        file.link_task(task)
        file.unlink_task(task)

    def test_link_task_template(self):
        file = projectal.File.create(b"file1data", {"name": "file1.data"})
        task_template = self.make_task_template()
        file.link_task_template(task_template)
        file.unlink_task_template(task_template)

    # Empty linkers
    def test_link_note(self):
        file = projectal.File.create(b"file1data", {"name": "file1.data"})
        note = projectal.Note.create(file, {"text": "Note"})
        assert len(file["noteList"]) == 1
        assert file["noteList"][0]["uuId"] == note["uuId"]
        assert file["noteList"][0]["text"] == note["text"]

        file = projectal.File.get(file["uuId"], links=["note"])
        projectal.Note.create(file, {"text": "Note 2"})
        assert len(file["noteList"]) == 2
