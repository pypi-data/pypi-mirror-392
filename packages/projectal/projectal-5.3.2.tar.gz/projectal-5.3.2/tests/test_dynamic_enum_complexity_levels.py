import projectal
from projectal.enums import ComplexityLevel
from tests.base_test import BaseTest


class TestComplexityLevels(BaseTest):
    def tearDown(self):
        default_complexity_levels = {
            ComplexityLevel.Low: 1,
            ComplexityLevel.Medium: 2,
            ComplexityLevel.High: 3,
        }
        projectal.ComplexityLevels.set(default_complexity_levels)

    def test_complexity_levels_get_default_values(self):
        complexity_levels = projectal.ComplexityLevels.get()

        assert len(complexity_levels) == 3
        assert complexity_levels[ComplexityLevel.Low] == 1
        assert complexity_levels[ComplexityLevel.Medium] == 2
        assert complexity_levels[ComplexityLevel.High] == 3

    def test_complexity_levels_set_level_add(self):
        complexity_levels_add_level = {
            ComplexityLevel.Low: 1,
            ComplexityLevel.Medium: 2,
            ComplexityLevel.High: 3,
            # Add complexity level: "Very_High"
            "Very_High": 4,
        }
        projectal.ComplexityLevels.set(complexity_levels_add_level)
        updated_complexity_levels = projectal.ComplexityLevels.get()

        assert len(updated_complexity_levels) == len(complexity_levels_add_level)

        for k, v in complexity_levels_add_level.items():
            assert updated_complexity_levels[k] == v

    def test_complexity_levels_set_level_rename(self):
        complexity_levels_rename_level = {
            # "Low" -> "Very_Low"
            "Very_Low": 1,
            ComplexityLevel.Medium: 2,
            ComplexityLevel.High: 3,
        }
        projectal.ComplexityLevels.set(complexity_levels_rename_level)
        updated_complexity_levels = projectal.ComplexityLevels.get()

        assert len(updated_complexity_levels) == len(complexity_levels_rename_level)

        for k, v in complexity_levels_rename_level.items():
            assert updated_complexity_levels[k] == v

    def test_complexity_levels_set_level_delete(self):
        complexity_levels_delete_level = {
            ComplexityLevel.Low: 1,
            ComplexityLevel.Medium: 2,
            # "High" removed
        }
        projectal.ComplexityLevels.set(complexity_levels_delete_level)
        updated_complexity_levels = projectal.ComplexityLevels.get()

        assert len(updated_complexity_levels) == len(complexity_levels_delete_level)

        for k, v in complexity_levels_delete_level.items():
            assert updated_complexity_levels[k] == v
