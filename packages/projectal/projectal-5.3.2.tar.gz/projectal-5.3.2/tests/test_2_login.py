import projectal
from tests.base_test import BaseTest


class TestLogin(BaseTest):
    def test_login(self):
        assert projectal.login()

    def test_cookie(self):
        """Test an api call after login to check if cookie is stored correctly"""
        projectal.login()
        assert projectal.auth_details()

    # The default timeout is very long (1 hour), so turn this test off.
    # You can run it manually when needed. Set the dev Projectal instance to
    # expire JWTs after 10 seconds (config: access.token.expiry.interval=10000).
    # def test_expired_retry(self):
    #     """Test automatic login after JWT expiry"""
    #     projectal.login()
    #     import time
    #
    #     loop_count = 0
    #     # Use this for an extended test.
    #     # while True:
    #     while loop_count < 10:
    #         time.sleep(8)
    #         print("cookies before query:")
    #         print(projectal.cookies)
    #         l = projectal.User.list()
    #         print("cookies after query:")
    #         print(projectal.cookies)
    #         assert len(l) > 0
    #         time.sleep(8)
    #         print("cookies before query:")
    #         print(projectal.cookies)
    #         details = projectal.User.current_user_details()  # different error
    #         print("cookies after query:")
    #         print(projectal.cookies)
    #         loop_count += 1
    #         print(f"Loop completed {loop_count} times.")

    # Simulate expired JWT by clearing the cookie between requests.
    # This is similar to a browser where the cookie is automatically
    # removed after expiry and is never sent in the request.
    def test_expired_retry_nocookie(self):
        """Test automatic login after JWT expiry"""
        old = projectal.login
        projectal.__no_jwt = False

        def wrapper():
            old()
            if projectal.__no_jwt:
                projectal.__no_jwt = False
                projectal.cookies = None

        projectal.login = wrapper

        projectal.login()
        projectal.User.list()  # Normal
        projectal.cookies = None
        projectal.__no_jwt = True
        l = projectal.User.list()  # Recover from no JWT
        assert len(l) > 0

        projectal.cookies = None
        projectal.__no_jwt = True
        projectal.login()
        details = (
            projectal.User.current_user_details()
        )  # different error (anonymousUser)
        assert details["uuId"]

        projectal.login = old
