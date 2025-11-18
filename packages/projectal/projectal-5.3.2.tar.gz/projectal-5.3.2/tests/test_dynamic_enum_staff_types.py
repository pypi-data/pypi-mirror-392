import projectal
from projectal.enums import StaffType
from tests.base_test import BaseTest


class TestStaffTypes(BaseTest):
    def tearDown(self):
        default_staff_types = {
            StaffType.Casual: 1,
            StaffType.Contractor: 2,
            StaffType.Consultant: 3,
            StaffType.Freelance: 4,
            StaffType.Intern: 5,
            StaffType.FullTime: 11,
            StaffType.PartTime: 12,
        }
        projectal.StaffTypes.set(default_staff_types)

    def test_staff_types_get_default_values(self):
        staff_types = projectal.StaffTypes.get()

        assert len(staff_types) == 7
        assert staff_types[StaffType.Casual] == 1
        assert staff_types[StaffType.Contractor] == 2
        assert staff_types[StaffType.Consultant] == 3
        assert staff_types[StaffType.Freelance] == 4
        assert staff_types[StaffType.Intern] == 5
        assert staff_types[StaffType.FullTime] == 11
        assert staff_types[StaffType.PartTime] == 12

    def test_staff_types_set_type_add(self):
        staff_types_add_type = {
            StaffType.Casual: 1,
            StaffType.Contractor: 2,
            StaffType.Consultant: 3,
            StaffType.Freelance: 4,
            StaffType.Intern: 5,
            StaffType.FullTime: 11,
            StaffType.PartTime: 12,
            # Add staff type: "Temporary"
            "Temporary": 13,
        }
        projectal.StaffTypes.set(staff_types_add_type)
        updated_staff_types = projectal.StaffTypes.get()

        assert len(updated_staff_types) == len(staff_types_add_type)

        for k, v in staff_types_add_type.items():
            assert updated_staff_types[k] == v

    def test_staff_types_set_type_rename(self):
        staff_types_rename_type = {
            # "Casual" -> "Super_Casual"
            "Super_Casual": 1,
            StaffType.Contractor: 2,
            StaffType.Consultant: 3,
            StaffType.Freelance: 4,
            StaffType.Intern: 5,
            StaffType.FullTime: 11,
            StaffType.PartTime: 12,
        }
        projectal.StaffTypes.set(staff_types_rename_type)
        updated_staff_types = projectal.StaffTypes.get()

        assert len(updated_staff_types) == len(staff_types_rename_type)

        for k, v in staff_types_rename_type.items():
            assert updated_staff_types[k] == v

    def test_staff_types_set_type_delete(self):
        staff_types_delete_type = {
            StaffType.Casual: 1,
            StaffType.Contractor: 2,
            StaffType.Consultant: 3,
            StaffType.Freelance: 4,
            StaffType.Intern: 5,
            StaffType.FullTime: 11,
            # "Part_Time" removed
        }
        projectal.StaffTypes.set(staff_types_delete_type)
        updated_staff_types = projectal.StaffTypes.get()

        assert len(updated_staff_types) == len(staff_types_delete_type)

        for k, v in staff_types_delete_type.items():
            assert updated_staff_types[k] == v
