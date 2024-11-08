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
import math
import unittest

import pandas

from simulator_worker.utils import add_datetime_index


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
