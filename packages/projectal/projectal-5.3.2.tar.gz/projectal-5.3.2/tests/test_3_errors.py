from projectal.errors import ProjectalException

import projectal

from tests.base_test import BaseTest
from tests.common import CommonTester


class TestErrors(BaseTest):
    """
    This class tests our error message extraction system. Projectal
    has many error types and we need to pass on the correct details
    to the client code whenever we can.
    """

    def setUp(self):
        self.common = CommonTester(projectal.User)

    def test_not_found(self):
        try:
            projectal.Project.get("fakeid")
        except ProjectalException as e:
            assert e.message.startswith("BAD_REQUEST")

    def test_bad_payload(self):
        try:
            projectal.query("[{]]")
        except ProjectalException as e:
            assert e.message.startswith("Internal server error")

    def test_feedback(self):
        # This is a "Clue Exception" with a feedbackList
        try:
            projectal.post("/api/project/get", [{}, {}])
        except ProjectalException as e:
            assert e.message.startswith("UNPROCESSABLE_ENTITY")
            assert "Clue" in e.message
            assert len(e.feedback) == 2

        # Middle one is real
        p = projectal.Project.create({"name": "project"})
        try:
            projectal.post("/api/project/get", [{}, p, {}])
        except ProjectalException as e:
            assert e.message.startswith("MULTI_STATUS")
            assert "Clue 1 of 2" in e.message
            assert len(e.feedback) == 3

    def test_400_with_feedback(self):
        # Some 4xx errors have a json body with clues
        try:
            projectal.User.create({"firstName": "First", "lastName": "Last"})
        except ProjectalException as e:
            assert "Missing_argument" in e.message
