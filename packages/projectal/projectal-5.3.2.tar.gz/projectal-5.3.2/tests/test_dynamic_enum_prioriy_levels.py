import projectal
from projectal.enums import PriorityLevel
from tests.base_test import BaseTest


class TestPriorityLevels(BaseTest):
    def tearDown(self):
        default_priority_levels = {
            PriorityLevel.Low: 1,
            PriorityLevel.Normal: 2,
            PriorityLevel.High: 3,
        }
        projectal.PriorityLevels.set(default_priority_levels)

    def test_priority_levels_get_default_values(self):
        priority_levels = projectal.PriorityLevels.get()

        assert len(priority_levels) == 3
        assert priority_levels[PriorityLevel.Low] == 1
        assert priority_levels[PriorityLevel.Normal] == 2
        assert priority_levels[PriorityLevel.High] == 3

    def test_priority_levels_set_level_add(self):
        priority_levels_add_level = {
            PriorityLevel.Low: 1,
            PriorityLevel.Normal: 2,
            PriorityLevel.High: 3,
            # Add priority level: "Very_High"
            "Very_High": 4,
        }
        projectal.PriorityLevels.set(priority_levels_add_level)
        updated_priority_levels = projectal.PriorityLevels.get()

        assert len(updated_priority_levels) == len(priority_levels_add_level)

        for k, v in priority_levels_add_level.items():
            assert updated_priority_levels[k] == v

    def test_priority_levels_set_level_rename(self):
        priority_levels_rename_level = {
            # "Low" -> "Very_Low"
            "Very_Low": 1,
            PriorityLevel.Normal: 2,
            PriorityLevel.High: 3,
        }
        projectal.PriorityLevels.set(priority_levels_rename_level)
        updated_priority_levels = projectal.PriorityLevels.get()

        assert len(updated_priority_levels) == len(priority_levels_rename_level)

        for k, v in priority_levels_rename_level.items():
            assert updated_priority_levels[k] == v

    def test_priority_levels_set_level_delete(self):
        priority_levels_delete_level = {
            PriorityLevel.Low: 1,
            PriorityLevel.Normal: 2,
            # "High" removed
        }
        projectal.PriorityLevels.set(priority_levels_delete_level)
        updated_priority_levels = projectal.PriorityLevels.get()

        assert len(updated_priority_levels) == len(priority_levels_delete_level)

        for k, v in priority_levels_delete_level.items():
            assert updated_priority_levels[k] == v
