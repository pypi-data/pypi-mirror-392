# MIT License
#
# Copyright (c) 2025
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import yaml
import click

from opswork.module.logger import Logger
from opswork.module.config import Config
from opswork.module.database import Database
from opswork.module.file_system import FileSystem
from opswork.command.recipes import Recipes


class Batch:
    """Batch operations for recipes"""

    def __init__(self):
        self.config = Config()
        self.database = Database()
        self.file_system = FileSystem()
        self.logger = Logger().get_logger(__name__)

    def init(self):
        """Init database and configs"""
        self.configs = self.config.load()
        self.database.connect(self.configs["database"]["path"])
        self.database.migrate()
        return self

    def _load_yaml(self, path):
        if not self.file_system.file_exists(path):
            raise click.ClickException(f"Batch file not found: {path}")

        content = self.file_system.read_file(path)

        try:
            data = yaml.load(content, Loader=yaml.Loader)
        except Exception as exc:
            raise click.ClickException(f"Invalid batch YAML: {exc}")

        if data is None:
            raise click.ClickException("Batch file is empty or invalid")

        return data

    def load_from_file(self, path, force=False):
        """Load recipes from a batch file into the database"""
        data = self._load_yaml(path)

        if "load" not in data or not isinstance(data["load"], list):
            raise click.ClickException("Batch file must include a 'load' list")

        loader = Recipes().init()

        for item in data["load"]:
            if not isinstance(item, dict):
                continue

            name = item.get("name", "").strip()
            path_value = item.get("path", "").strip()
            sub_value = item.get("sub", "").strip()
            tags_value = item.get("tags", [])

            if name == "" or path_value == "":
                raise click.ClickException("Each recipe must include 'name' and 'path'")

            # Normalize tags to list
            if isinstance(tags_value, str):
                tags_list = [
                    t for t in [x.strip() for x in tags_value.split(",")] if t != ""
                ]
            elif isinstance(tags_value, list):
                tags_list = tags_value
            else:
                tags_list = []

            loader.add(
                name,
                {"path": path_value, "sub": sub_value, "tags": tags_list},
                force,
            )

        click.echo("Batch recipes loaded successfully")

    def run_from_file(self, path, host_name="", tag="", var=()):
        """Run recipes listed under run in a batch file"""
        data = self._load_yaml(path)

        recipes_list = data.get("run", [])

        if not isinstance(recipes_list, list) or len(recipes_list) == 0:
            raise click.ClickException("Batch file must include a non-empty 'run' list")

        runner = Recipes().init()

        for recipe_name in recipes_list:
            if not isinstance(recipe_name, str) or recipe_name.strip() == "":
                continue

            runner.run(recipe_name.strip(), host_name, tag, var)

        click.echo("Batch recipes executed successfully")
