import projectal
import datetime
from projectal.errors import ProjectalException, UsageException
from tests.base_test import BaseTest
from tests.common import CommonTester
from projectal.enums import DateLimit


class TestStaff(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Staff)
        self.staff = self.make_staff()

    def test_create_contract(self):
        contracted_staff_uuid = self.staff.create_contract(
            self.staff.get("uuId"), {"position": "Updated"}
        )
        contracted_staff = projectal.Staff.get(
            contracted_staff_uuid, links=["CONTRACT"]
        )
        assert len(contracted_staff.get("contractList")) == 2

        contracted_staff_uuid_2 = projectal.Staff.create_contract(
            contracted_staff.get("uuId"), {"position": "Updated2"}
        )
        contracted_staff_2 = projectal.Staff.get(
            contracted_staff_uuid_2, links=["CONTRACT"]
        )
        assert len(contracted_staff_2.get("contractList")) == 3

    def test_create_contract_empty_payload(self):
        contracted_staff_uuid = self.staff.create_contract(self.staff.get("uuId"))
        contracted_staff = projectal.Staff.get(
            contracted_staff_uuid, links=["CONTRACT"]
        )
        assert len(contracted_staff.get("contractList")) == 2

    def test_modifying_contract_directly_fails(self):
        contracted_staff_uuid = self.staff.create_contract(
            self.staff.get("uuId"), {"position": "Updated"}
        )
        contracted_staff = projectal.Staff.get(
            contracted_staff_uuid, links=["CONTRACT"]
        )
        assert len(contracted_staff.get("contractList")) == 2

        contracted_staff.get("contractList").pop()
        # Modifying Contract link directly is not supported,
        # so saving modified contractList should throw an exception
        self.assertRaises(ProjectalException, contracted_staff.save)

    def test_end_current_flag(self):
        contracted_staff_uuid = self.staff.create_contract(
            self.staff.get("uuId"),
            {"position": "Updated"},
            end_current_contract=True,
        )
        contracted_staff = projectal.Staff.get(
            contracted_staff_uuid, links=["CONTRACT"]
        )
        assert len(contracted_staff.get("contractList")) == 2

        date_today = datetime.datetime.today().strftime("%Y-%m-%d")
        first_staff_updated = projectal.Staff.get(self.staff.get("uuId"))
        assert first_staff_updated.get("endDate") == date_today

    def test_start_new_flag(self):
        contracted_staff_uuid = self.staff.create_contract(
            self.staff.get("uuId"),
            {"position": "Updated"},
            start_new_contract=True,
        )
        contracted_staff = projectal.Staff.get(
            contracted_staff_uuid, links=["CONTRACT"]
        )
        assert len(contracted_staff.get("contractList")) == 2

        date_today = datetime.datetime.today().strftime("%Y-%m-%d")
        assert contracted_staff.get("startDate") == date_today
        assert contracted_staff.get("endDate") == DateLimit.Max

    def test_start_new_end_current_flags(self):
        contracted_staff_uuid = self.staff.create_contract(
            self.staff.get("uuId"),
            {"position": "Updated"},
            end_current_contract=True,
            start_new_contract=True,
        )
        contracted_staff = projectal.Staff.get(
            contracted_staff_uuid, links=["CONTRACT"]
        )
        assert len(contracted_staff.get("contractList")) == 2

        # Check that result is the same for new contract when using both flags
        date_today = datetime.datetime.today().strftime("%Y-%m-%d")
        assert contracted_staff.get("startDate") == date_today
        assert contracted_staff.get("endDate") == DateLimit.Max

        # Check that result is the same for old contract when using both flags
        first_staff_updated = projectal.Staff.get(self.staff.get("uuId"))
        assert first_staff_updated.get("endDate") == date_today

    def test_end_current_flag_invalid_date_fails(self):
        contracted_staff_uuid = self.staff.create_contract(
            self.staff.get("uuId"),
            {"position": "Updated"},
            end_current_contract=True,
        )
        contracted_staff = projectal.Staff.get(
            contracted_staff_uuid, links=["CONTRACT"]
        )
        assert len(contracted_staff.get("contractList")) == 2

        date_tomorrow = (
            datetime.datetime.today() + datetime.timedelta(days=1)
        ).strftime("%Y-%m-%d")
        contracted_staff["startDate"] = date_tomorrow
        contracted_staff.save()

        # Should raise usage exception when ending the
        # current contract with an invalid date
        self.assertRaises(
            UsageException,
            contracted_staff.create_contract,
            contracted_staff.get("uuId"),
            {"position": "Updated"},
            True,  # end_current_contract
            False,  # start_new_contract
        )
