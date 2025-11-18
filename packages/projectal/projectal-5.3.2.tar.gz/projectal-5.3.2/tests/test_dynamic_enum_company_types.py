import projectal
from projectal.enums import CompanyType
from tests.base_test import BaseTest


class TestCompanyTypes(BaseTest):
    def tearDown(self):
        default_company_types = {
            CompanyType.Primary: 0,
            CompanyType.Subsidiary: 1,
            CompanyType.Contractor: 2,
            CompanyType.Partner: 3,
            CompanyType.Affiliate: 4,
            CompanyType.Office: 5,
            CompanyType.Division: 6,
        }
        projectal.CompanyTypes.set(default_company_types)

    def test_company_types_get_default_values(self):
        company_types = projectal.CompanyTypes.get()

        assert len(company_types) == 7
        assert company_types[CompanyType.Primary] == 0
        assert company_types[CompanyType.Subsidiary] == 1
        assert company_types[CompanyType.Contractor] == 2
        assert company_types[CompanyType.Partner] == 3
        assert company_types[CompanyType.Affiliate] == 4
        assert company_types[CompanyType.Office] == 5
        assert company_types[CompanyType.Division] == 6

    def test_company_types_set_type_add(self):
        company_types_add_type = {
            CompanyType.Primary: 0,
            CompanyType.Subsidiary: 1,
            CompanyType.Contractor: 2,
            CompanyType.Partner: 3,
            CompanyType.Affiliate: 4,
            CompanyType.Office: 5,
            CompanyType.Division: 6,
            "Sub-Contractor": 7,
        }
        projectal.CompanyTypes.set(company_types_add_type)
        updated_company_types = projectal.CompanyTypes.get()

        assert len(updated_company_types) == len(company_types_add_type)

        for k, v in company_types_add_type.items():
            assert updated_company_types[k] == v

    def test_company_types_set_type_rename(self):
        company_types_rename_type = {
            CompanyType.Primary: 0,
            # "Subsidiary" -> "Sub-Contractor"
            "Sub-Contractor": 1,
            CompanyType.Contractor: 2,
            CompanyType.Partner: 3,
            CompanyType.Affiliate: 4,
            CompanyType.Office: 5,
            CompanyType.Division: 6,
        }
        projectal.CompanyTypes.set(company_types_rename_type)
        updated_company_types = projectal.CompanyTypes.get()

        assert len(updated_company_types) == len(company_types_rename_type)

        for k, v in company_types_rename_type.items():
            assert company_types_rename_type[k] == v

    def test_company_types_set_type_delete(self):
        company_types_delete_type = {
            CompanyType.Primary: 0,
            CompanyType.Subsidiary: 1,
            CompanyType.Contractor: 2,
            CompanyType.Partner: 3,
            CompanyType.Affiliate: 4,
            # "Office" removed
            CompanyType.Division: 6,
        }
        projectal.CompanyTypes.set(company_types_delete_type)
        updated_company_types = projectal.CompanyTypes.get()

        assert len(updated_company_types) == len(company_types_delete_type)

        for k, v in company_types_delete_type.items():
            assert updated_company_types[k] == v

    # TODO test disallowed behaviours are disallowed
