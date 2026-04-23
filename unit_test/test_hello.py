#  Copyright (c) 2023. {cookiecutter.cookiecutter.maintainer_name}}
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Test script for python template."""
import datetime
import logging
import math
import unittest

import pandas
from parameterized import parameterized  # type: ignore[import-not-found]

from simulator_worker.utils import (
    add_datetime_index,
    _parse_bool_config,
    _parse_float_config,
)


class TestParseBoolConfig(unittest.TestCase):
    @parameterized.expand([
        ("present_true", {"flag": True}, "flag", False, True),
        ("present_false", {"flag": False}, "flag", True, False),
        ("absent_key", {}, "flag", True, True),
        ("string_false", {"flag": "false"}, "flag", True, False),
        ("string_true", {"flag": "true"}, "flag", False, True),
        ("unrecognized_string", {"flag": "maybe"}, "flag", True, False),
    ])
    def test_parse_bool_config(
        self, _name: str, config: dict, key: str, default: bool, expected: bool
    ) -> None:
        result = _parse_bool_config(config, key, default)
        self.assertEqual(result, expected)


class TestParseFloatConfig(unittest.TestCase):
    @parameterized.expand([
        ("present_float", {"lifetime": 25.0}, "lifetime", 30.0, 25.0),
        ("present_int", {"lifetime": 25}, "lifetime", 30.0, 25.0),
        ("present_string", {"lifetime": "25.0"}, "lifetime", 30.0, 25.0),
        ("absent_key", {}, "lifetime", 30.0, 30.0),
        ("zero_value", {"discount_rate": 0.0}, "discount_rate", 5.0, 0.0),
        ("non_numeric", {"lifetime": None}, "lifetime", 30.0, 30.0),
        ("invalid_string", {"lifetime": "not-a-number"}, "lifetime", 30.0, 30.0),
    ])
    def test_parse_float_config(
        self, _name: str, config: dict, key: str, default: float, expected: float
    ) -> None:
        result = _parse_float_config(config, key, default)
        self.assertEqual(result, expected)

    def test__present_int_value__returns_float_type(self) -> None:
        # Arrange
        config: dict = {"lifetime": 25}

        # Act
        result = _parse_float_config(config, "lifetime", 30.0)

        # Assert
        self.assertIsInstance(result, float)

    def test__absent_key_with_warn_msg__emits_warning(self) -> None:
        # Arrange
        config: dict = {}

        # Act / Assert
        with self.assertLogs("simulator_worker", level=logging.WARNING) as cm:
            _parse_float_config(config, "lifetime", 30.0, warn_msg="missing 'lifetime'.")

        self.assertTrue(any("missing" in msg for msg in cm.output))

    def test__present_key_with_warn_msg__no_warning(self) -> None:
        # Arrange
        config: dict = {"lifetime": 25.0}

        # Act — no warning should be emitted
        with self.assertNoLogs("simulator_worker", level=logging.WARNING):
            result = _parse_float_config(
                config, "lifetime", 30.0, warn_msg="missing 'lifetime'."
            )

        # Assert
        self.assertEqual(result, 25.0)


class TestHelloWorld(unittest.TestCase):
    def test__hello_world(self) -> None:
        print("Hello world!")

    def test__add_datetime_index__happy_path(self) -> None:
        # Arrange
        df = pandas.DataFrame()
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(hours=1)
        timestep = datetime.timedelta(minutes=30)

        # Act
        result_df = add_datetime_index(
            df, start_time, end_time, math.floor(timestep.total_seconds())
        )

        # Assert
        self.assertEqual(len(result_df), 2)
