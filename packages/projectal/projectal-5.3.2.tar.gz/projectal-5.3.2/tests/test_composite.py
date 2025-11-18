import projectal
from tests.base_test import BaseTest


class TestComposite(BaseTest):
    def test_composite(self):
        # Composite script example.
        # Query for a company
        # Create a project
        # Link company and project
        payload = [
            {
                "note": "Query for any company",
                "invoke": "/api/query/match",
                "body": {
                    "name": "First company",
                    "select": [["COMPANY.uuId"], ["COMPANY.name"]],
                },
                "vars": [
                    {"name": "v_comp_uuid", "path": "$.resultList[0].array[0]"},
                    {"name": "v_comp_name", "path": "$.resultList[0].array[1]"},
                ],
            },
            {
                "invoke": "/api/project/add",
                "body": [
                    {
                        "name": "Composite Project",
                    }
                ],
                "vars": [
                    {"name": "v_proj_uuid", "path": "$.feedbackList[0].uuId"},
                ],
            },
            {
                "invoke": "/api/company/link/project/add",
                "body": {
                    "uuId": "@{v_comp_uuid}",
                    "projectList": [{"uuId": "@{v_proj_uuid}"}],
                },
            },
        ]
        projectal.post("/api/composite?track=true", payload)
