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
import unittest

from simulator_worker.app_logging import LogLevel, setup_logging


class TestLogging(unittest.TestCase):
    def tearDown(self) -> None:
        import logging
        from importlib import reload

        logging.shutdown()
        reload(logging)
        return super().tearDown()

    def test_start_app_info(self) -> None:
        try:
            setup_logging(LogLevel.parse("INFO"), colors=True)
        except Exception as e:
            self.fail(f"simulator_worker.start_app() raised an exception: {e}")

    def test_start_app_debug(self) -> None:
        try:
            setup_logging(LogLevel.parse("DEBUG"), colors=False)
            pass
        except Exception as e:
            self.fail(f"simulator_worker.start_app() raised an exception: {e}")

    def test_start_app_wrong_logtype(self) -> None:
        with self.assertRaises(ValueError):
            setup_logging(LogLevel.parse("WRONG_LOG_TYPE"), colors=False)
