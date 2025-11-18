import projectal
from projectal.enums import StaffType, PayFrequency, DateLimit
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestDepartment(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Department)
        # Reuse for links
        self.department = projectal.Department.create(
            {
                "name": "Department",
            }
        )

    def test_crud(self):
        uuId = self.common.test_create({"name": "Test department (python API wrapper)"})
        entity = self.common.test_get(uuId)
        changed = {"uuId": uuId, "name": "Updated department"}
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_link_staff(self):
        staff = self.make_staff()
        projectal.Department.link_staff(self.department, staff)
        projectal.Department.unlink_staff(self.department, staff)

    def test_link_department(self):
        department = projectal.Department.create({"name": "Department"})
        projectal.Department.link_department(self.department, department)
        projectal.Department.unlink_department(self.department, department)

    def test_history(self):
        self.department["name"] = "History1"
        projectal.Department.update(self.department)
        assert len(self.department.history()) == 2

    def test_clone(self):
        uuId = self.department.clone({"name": "Cloned"})
        clone = projectal.Department.get(uuId)
        assert clone["uuId"] != self.department["uuId"]
        assert clone["name"] == "Cloned"

    def test_tree(self):
        projectal.Department.delete(projectal.Department.list())

        # Our test tree:
        # Company
        # - dep1
        #   - subdep1
        # - dep2
        #   - subdep2 ('staff: active1, inactive1')
        #     - subdep3
        company = projectal.Company.get_primary_company()

        d1 = projectal.Department.create({"name": "d1"})
        sd1 = projectal.Department.create({"name": "sd1"})
        d1.link_company(company)
        d1.link_department(sd1)

        d2 = projectal.Department.create({"name": "d2"})
        sd2 = projectal.Department.create({"name": "sd2"})
        sd3 = projectal.Department.create({"name": "sd3"})
        d2.link_company(company)
        d2.link_department(sd2)
        sd2.link_department(sd3)

        staffa = projectal.Staff.create(
            {
                "email": "test.staff.link.{}@example.com".format(self.random()),
                "firstName": "Active",
                "lastName": "Active",
                "staffType": StaffType.Consultant,
                "payFrequency": PayFrequency.Weekly,
                "payAmount": 200,
                "startDate": DateLimit.Min,
                "endDate": DateLimit.Max,
            }
        )

        staffi = projectal.Staff.create(
            {
                "email": "test.staff.link.{}@example.com".format(self.random()),
                "firstName": "Inactive",
                "lastName": "Inctive",
                "staffType": StaffType.Consultant,
                "payFrequency": PayFrequency.Weekly,
                "payAmount": 200,
                "startDate": "1990-01-01",
                "endDate": "1990-01-05",
            }
        )
        sd2.link_staff(staffa)
        sd2.link_staff(staffi)

        # There are two top-level departments
        tree_deep = projectal.Department.tree()
        assert len(tree_deep) == 2
        # And there is one sub-level in the first level
        assert "departmentList" in tree_deep[0]
        assert len(tree_deep[0]["departmentList"]) == 1

        tree_first = projectal.Department.tree(holder=company, level=True)
        # Still have 2 in top level
        assert len(tree_first) == 2
        # But now we don't include sub-departments
        assert "departmentList" not in tree_first[0]

        # dep 2 has 1 child dep (sd2)
        tree = projectal.Department.tree(holder=d2)
        assert tree[0]["uuId"] == sd2["uuId"]
        # and sd2 has 1 child (sd3)
        assert len(tree[0]["departmentList"]) == 1
        assert tree[0]["departmentList"][0]["uuId"] == sd3["uuId"]
        # both our staff should be in the result (default is true for both types)
        assert "staffList" in tree[0]
        assert len(tree[0]["staffList"]) == 2

        # We have one active staff in dep2
        tree = projectal.Department.tree(holder=d2, inactive_staff=False)
        assert "staffList" in tree[0]
        assert len(tree[0]["staffList"]) == 1
        assert tree[0]["staffList"][0]["uuId"] == staffa["uuId"]

        # We have one inactive staff in dep2
        tree = projectal.Department.tree(holder=d2, active_staff=False)
        assert "staffList" in tree[0]
        assert len(tree[0]["staffList"]) == 1
        assert tree[0]["staffList"][0]["uuId"] == staffi["uuId"]

        # subdep 3 has no child deps
        tree = projectal.Department.tree(holder=sd3)
        assert len(tree) == 0

    def test_list(self):
        self.common.test_list()

    def test_link_tag(self):
        tag = self.make_tag()
        self.department.link_tag(tag)
        self.department.unlink_tag(tag)

    # Reverse linkers
    def test_link_company(self):
        company = self.make_company()
        self.department.link_company(company)
        self.department.unlink_company(company)

    # Empty linkers
    def test_link_note(self):
        note = projectal.Note.create(self.department, {"text": "Note"})
        assert len(self.department["noteList"]) == 1
        assert self.department["noteList"][0]["uuId"] == note["uuId"]
        assert self.department["noteList"][0]["text"] == note["text"]

        department = projectal.Department.get(self.department, links=["note"])
        projectal.Note.create(department, {"text": "Note 2"})
        assert len(department["noteList"]) == 2
