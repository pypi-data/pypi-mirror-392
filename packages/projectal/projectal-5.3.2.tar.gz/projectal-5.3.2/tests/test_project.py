import projectal
from tests.base_test import BaseTest
from tests.common import CommonTester


class TestProject(BaseTest):
    def setUp(self):
        self.common = CommonTester(projectal.Project)
        self.project = projectal.Project.create({"name": "Project"})
        self.search_setup = False

    def test_crud(self):
        new = {
            "identifier": "TestIdentifier",
            "name": "Test project (python API wrapper)",
        }
        uuId = self.common.test_create(new)
        entity = self.common.test_get(uuId)

        # Change only some details
        changed = {
            "uuId": uuId,
            "identifier": "Updated identifier",
            "name": "Updated name",
        }
        self.common.test_update(old=entity, changed=changed)
        self.common.test_delete(uuId)

    def test_link_location(self):
        location = projectal.Location.create({"name": "Location"})
        self.project.link_location(location)
        self.project.unlink_location(location)

    def test_link_customer(self):
        customer = projectal.Customer.create({"name": "Customer"})
        self.project.link_customer(customer)
        self.project.unlink_customer(customer)

    def test_link_file(self):
        file = projectal.File.create(b"testdata", {"name": "File"})
        self.project.link_file(file)
        self.project.unlink_file(file)

    def test_link_stage(self):
        stage = projectal.Stage.create({"name": "Stage"})
        self.project.link_stage(stage)
        self.project.unlink_stage(stage)

    def test_link_rebate(self):
        rebate = projectal.Rebate.create({"name": "Rebate", "rebate": "0.2"})
        self.project.link_rebate(rebate)
        self.project.unlink_rebate(rebate)

    def test_link_stage_list(self):
        stage = projectal.Stage.create({"name": "Stage"})
        self.project.link_stage_list([stage])
        self.project.unlink_stage_list([stage])

    def test_link_tag(self):
        tag = self.make_tag()
        self.project.link_tag(tag)
        self.project.unlink_tag(tag)

    # Reverse linkers
    def test_link_company(self):
        company = self.make_company()
        self.project.link_company(company)
        self.project.unlink_company(company)

    # Empty linkers
    def test_link_note(self):
        project = self.make_project()
        note = projectal.Note.create(project, {"text": "Note"})
        assert len(project["noteList"]) == 1
        assert project["noteList"][0]["uuId"] == note["uuId"]
        assert project["noteList"][0]["text"] == note["text"]

        project = projectal.Project.get(project["uuId"], links=["note"])
        projectal.Note.create(project, {"text": "Note 2"})
        assert len(project["noteList"]) == 2

    def test_link_task(self):
        project = self.make_project()
        self.make_task(project)
        self.make_task(project)
        self.make_task(project)
        project = projectal.Project.get(project, links=["task"])
        assert "taskList" in project
        assert len(project["taskList"]) == 3

    def test_history(self):
        self.project["name"] = "History1"
        projectal.Project.update(self.project)
        assert len(self.project.history()) == 2

    def test_clone(self):
        uuId = self.project.clone({"name": "Cloned"})
        clone = projectal.Project.get(uuId)
        assert clone["uuId"] != self.project["uuId"]
        assert clone["name"] == "Cloned"

    def test_stage_order(self):
        stage1 = projectal.Stage.create({"name": "Stage1"})
        stage2 = projectal.Stage.create({"name": "Stage2"})
        stage3 = projectal.Stage.create({"name": "Stage3"})
        projectal.Project.link_stage_list(self.project, [stage1, stage2, stage3])

        projectal.Project.stage_order(self.project["uuId"], [stage2, stage3, stage1])
        p = projectal.Project.get(self.project["uuId"], links=["STAGE_LIST"])
        assert p["stageList"]
        assert p["stageList"][0]["uuId"] == stage2["uuId"]
        assert p["stageList"][1]["uuId"] == stage3["uuId"]
        assert p["stageList"][2]["uuId"] == stage1["uuId"]

    def test_autoschedule(self):
        # TODO: better test
        assert projectal.Project.autoschedule(self.project, mode="ALAP")

    def test_list(self):
        self.common.test_list()

    def set_up_search(self):
        if self.search_setup:
            return
        # Create search dataset for query testing
        # Delete existing data. Only search data from here.
        all = projectal.Project.list()
        projectal.Project.delete(all)
        c = projectal.Project.create
        c(
            {
                "name": "Zombies 2020",
                "identifier": "zmb-001",
                "description": "Film in  2020",
            }
        )
        c(
            {
                "name": "Zombies 2021",
                "identifier": "zmb-002",
                "description": "Sequel to 2020",
            }
        )
        c(
            {
                "name": "Zombies 2022",
                "identifier": "zmb-003",
                "description": "More zombies",
            }
        )
        c(
            {
                "name": "Zombies 2023",
                "identifier": "zmb-004",
                "description": "even more zombies",
            }
        )
        c(
            {
                "name": "Zombies 2024",
                "identifier": "zmb-005",
                "description": "far too much zombie",
            }
        )
        c(
            {
                "name": "Zombies 2025",
                "identifier": "zmb-006",
                "description": "getting sick of zombies",
            }
        )
        self.search_setup = True

    def test_match(self):
        self.set_up_search()
        projects = projectal.Project.match("identifier", "zmb-005")
        assert len(projects) == 1
        assert isinstance(projects[0], projectal.Project)
        projects = projectal.Project.match("identifier", "zmb-099")
        assert len(projects) == 0

    def test_match_starts(self):
        self.set_up_search()
        projects = projectal.Project.match_startswith("name", "Zomb")
        assert len(projects) == 6
        projects = projectal.Project.match_startswith("name", "20")
        assert len(projects) == 0

    def test_match_ends(self):
        projects = projectal.Project.match_endswith("identifier", "-003")
        assert len(projects) == 1
        projects = projectal.Project.match_endswith("identifier", "009")
        assert len(projects) == 0

    def test_search(self):
        self.set_up_search()
        # Appears in name, description
        projects = projectal.Project.search(["name", "description"], "2020")
        assert len(projects) == 2
        # Appears in name only
        projects = projectal.Project.search(["name", "description"], "2023")
        assert len(projects) == 1
        # Appears in description only
        projects = projectal.Project.search(["name", "description"], "sick")
        assert len(projects) == 1
        # Appears in none
        projects = projectal.Project.search(["name", "description"], "alien")
        assert len(projects) == 0
        # Match lowercase only
        projects = projectal.Project.search(
            ["name", "description"], "zombie", case_sensitive=True
        )
        assert len(projects) == 4

        # TODO: add tests for regex escape codes in search term
        # add code to auto-escape for us?
