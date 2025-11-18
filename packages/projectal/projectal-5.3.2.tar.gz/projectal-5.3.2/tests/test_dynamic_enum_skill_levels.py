import projectal
from projectal.enums import SkillLevel
from tests.base_test import BaseTest


class TestSkillLevels(BaseTest):
    def tearDown(self):
        default_skill_levels = {
            SkillLevel.Senior: 10,
            SkillLevel.Mid: 20,
            SkillLevel.Junior: 30,
        }
        projectal.SkillLevels.set(default_skill_levels)

    def test_skill_levels_get_default_values(self):
        skill_levels = projectal.SkillLevels.get()

        assert len(skill_levels) == 3
        assert skill_levels[SkillLevel.Senior] == 10
        assert skill_levels[SkillLevel.Mid] == 20
        assert skill_levels[SkillLevel.Junior] == 30

    def test_skill_levels_set_level_add(self):
        skill_levels_add_level = {
            SkillLevel.Senior: 10,
            SkillLevel.Mid: 20,
            SkillLevel.Junior: 30,
            # Add skill level: "Trainee"
            "Trainee": 100,
        }
        projectal.SkillLevels.set(skill_levels_add_level)
        updated_skill_levels = projectal.SkillLevels.get()

        assert len(updated_skill_levels) == len(skill_levels_add_level)

        for k, v in skill_levels_add_level.items():
            assert updated_skill_levels[k] == v

    def test_skill_levels_set_level_rename(self):
        skill_levels_rename_level = {
            # "Senior" -> "Expert"
            "Expert": 10,
            SkillLevel.Mid: 20,
            SkillLevel.Junior: 30,
        }
        projectal.SkillLevels.set(skill_levels_rename_level)
        updated_skill_levels = projectal.SkillLevels.get()

        assert len(updated_skill_levels) == len(skill_levels_rename_level)

        for k, v in skill_levels_rename_level.items():
            assert updated_skill_levels[k] == v

    def test_skill_levels_set_level_delete(self):
        skill_levels_delete_level = {
            SkillLevel.Senior: 10,
            SkillLevel.Mid: 20,
            # "Junior" removed
        }
        projectal.SkillLevels.set(skill_levels_delete_level)
        updated_skill_levels = projectal.SkillLevels.get()

        assert len(updated_skill_levels) == len(skill_levels_delete_level)

        for k, v in skill_levels_delete_level.items():
            assert updated_skill_levels[k] == v
