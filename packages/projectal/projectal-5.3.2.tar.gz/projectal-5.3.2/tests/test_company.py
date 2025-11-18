import projectal
from projectal.enums import CompanyType, StaffType, PayFrequency, DateLimit
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestCompany(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Company)
        # Reuse for links
        self.company = projectal.Company.create(
            {"name": "Company", "type": CompanyType.Office}
        )

    def clear(self):
        primary = projectal.Company.get_primary_company()
        for c in projectal.Company.list():
            try:
                if c != primary["uuId"]:
                    projectal.Company.delete(c)
            except:
                # don't fail when deleting child of already-deleted parent
                pass

    def test_crud(self):
        uuId = self.common.test_create(
            {"name": "Test company (python API wrapper)", "type": CompanyType.Office}
        )
        entity = self.common.test_get(uuId)
        changed = {"uuId": uuId, "name": "Updated name", "type": CompanyType.Subsidiary}
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_link_location(self):
        location = projectal.Location.create({"name": "Location"})
        self.company.link_location(location)
        self.company.unlink_location(location)

    def test_link_staff(self):
        staff = self.make_staff()
        self.company.link_staff(staff)
        self.company.unlink_staff(staff)

    def test_link_company(self):
        company = projectal.Company.create(
            {"name": "Company", "type": CompanyType.Affiliate}
        )
        self.company.link_company(company)
        self.company.unlink_company(company)

    def test_link_department(self):
        department = projectal.Department.create({"name": "Department"})
        self.company.link_department(department)
        self.company.unlink_department(department)

    def test_link_project(self):
        project = projectal.Project.create({"name": "Project"})
        self.company.link_project(project)
        self.company.unlink_project(project)

    def test_link_contact(self):
        customer = projectal.Customer.create({"name": "Holder"})
        contact = projectal.Contact.create(
            customer["uuId"],
            {
                "firstName": "First",
                "lastName": "Last",
            },
        )
        self.company.link_contact(contact)
        self.company.unlink_contact(contact)

    def test_link_file(self):
        file = projectal.File.create(b"testdata", {"name": "File"})
        self.company.link_file(file)
        self.company.unlink_file(file)

    def test_link_tag(self):
        tag = self.make_tag()
        self.company.link_tag(tag)
        self.company.unlink_tag(tag)

    # Empty linkers
    def test_link_note(self):
        note = projectal.Note.create(self.company, {"text": "Note"})
        assert len(self.company["noteList"]) == 1
        assert self.company["noteList"][0]["uuId"] == note["uuId"]
        assert self.company["noteList"][0]["text"] == note["text"]

        company = projectal.Company.get(self.company, links=["note"])
        projectal.Note.create(company, {"text": "Note 2"})
        assert len(company["noteList"]) == 2

    def test_history(self):
        self.company["name"] = "History1"
        projectal.Company.update(self.company)
        assert len(self.company.history()) == 3

    def test_clone(self):
        uuId = self.company.clone({"name": "Cloned"})
        clone = projectal.Company.get(uuId)
        assert clone["uuId"] != self.company["uuId"]
        assert clone["name"] == "Cloned"

    def test_tree(self):
        # Purge old data
        self.clear()

        primary = projectal.Company.get_primary_company()

        # Our test tree:
        # Primary Company
        #  - comp1
        #    - subcomp1
        #  - comp2
        #    - subcomp2 ('department: subdep')
        #      - subcomp3
        c1 = projectal.Company.create({"name": "c1", "type": CompanyType.Office})
        sc1 = projectal.Company.create(
            {"name": "sc1", "type": CompanyType.Subsidiary, "parent": c1["uuId"]}
        )

        c2 = projectal.Company.create({"name": "c2", "type": CompanyType.Office})
        sc2 = projectal.Company.create(
            {"name": "sc2", "type": CompanyType.Subsidiary, "parent": c2["uuId"]}
        )
        sc3 = projectal.Company.create(
            {"name": "sc3", "type": CompanyType.Subsidiary, "parent": sc2["uuId"]}
        )

        dep = projectal.Department.create({"name": "subdep"})
        projectal.Company.link_department(sc2, dep)

        # There are two companies under primary
        tree_deep = projectal.Company.tree(uuId=primary["uuId"])
        assert len(tree_deep) == 2
        # And there is one sub-level in the first level
        assert "companyList" in tree_deep[0]
        assert len(tree_deep[0]["companyList"]) == 1

        tree_first = projectal.Company.tree(uuId=primary["uuId"], level=True)
        # Still have 2 in top level
        assert len(tree_first) == 2
        # But now  we don't include sub-companies
        assert "companyList" not in tree_first[0]

        # comp 2 has 1 child company (sc2)
        tree = projectal.Company.tree(uuId=c2["uuId"], include_department=True)
        assert tree[0]["uuId"] == sc2["uuId"]
        # and sc2 has 1 child (sc3)
        assert len(tree[0]["companyList"]) == 1
        assert tree[0]["companyList"][0]["uuId"] == sc3["uuId"]
        # And 1 dep, which we asked for
        assert tree[0]["departmentList"][0]["uuId"] == dep["uuId"]

        # subcomp3 has no child companies
        tree = projectal.Company.tree(uuId=sc3["uuId"])
        assert len(tree) == 0

    def test_primary_company(self):
        company = projectal.Company.get_primary_company()
        status = projectal.status()
        assert company["name"] == status["companyName"]

    def test_list(self):
        self.common.test_list()
