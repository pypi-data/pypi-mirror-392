import copy
import json
import os
import sys

import yaml

from .. import constants as c
from . import schema
from .methods import directory, git


class Template:
    def __init__(self, **kwargs):
        self.path = kwargs.get("template_path")
        self.filename = kwargs.get("template_filename", c.TEMPLATE_FILENAME)
        self.branch = kwargs.get("branch")
        self.workpath = kwargs.get("workpath")
        self.includes = None
        self.data = None

    def __repr__(self):
        return json.dumps(
            {
                "path": self.path,
                "filename": self.filename,
                "branch": self.branch,
                "workpath": self.workpath,
            },
        )

    @property
    def actions(self):
        if self.data is None:
            return []
        # pylint: disable=unsubscriptable-object
        return self.data["actions"]

    @property
    def children(self):
        """
        Return only the includes for this template
        """
        if not self.data:
            return

        # By reversing the list, we'll be building the list
        # of questions in the right order
        items = reversed(self.data.get("includes", []))
        for item in items:
            path = item["include"]
            filename = item.get("filename")
            branch = item.get("branch")
            workpath = item.get("workpath")

            yield Template(template_path=path, template_filename=filename, branch=branch, workpath=workpath)

    @property
    def dependencies(self):
        # By reversing the list, we'll be building the list
        # of questions in the right order
        items = reversed(self._dependencies)
        yield from items


def find(tpl):
    for func in [directory.find, git.find]:
        tpl.workpath = func(tpl)
        if tpl.workpath:
            return tpl
    sys.exit(f'error: no "{tpl.filename}" file found in "{tpl.path}"')


def _load(tpl):
    path = os.path.join(tpl.workpath, tpl.filename)
    try:
        with open(path, encoding="UTF-8") as fd:
            data = yaml.safe_load(fd) or {}
    except Exception as err:
        sys.exit(f"error: failed to open '{tpl.workpath}': {err}")
    return data


def _reduce(data):
    # Reduce to relevant sections.
    # This allows a user to add whatever he wants to a scaffold.yml file
    retval = {
        "actions": data.get("actions", []),
        "answers": data.get("answers", {}),
        "includes": data.get("includes", []),
        "jinja2": data.get("jinja2", {}),
        "questions": data.get("questions", []),
    }
    return retval


def _validate(data):
    # TODO: merge with answers into utils
    yaml_schema = yaml.safe_load(schema.SCHEMA)
    validator = schema.LocalValidator(yaml_schema)

    if not validator.validate(data):
        locations = str(json.dumps(validator.errors, indent=2))
        raise SystemExit(f"error: YAML schema validation error. Location:\n{locations}") from None

    return validator.normalized(data)


def load(tpl, root=None):
    if root is None:
        root = tpl

    data = _load(tpl)
    data = _reduce(data)
    data = _validate(data)
    tpl.data = data

    # Keep a list of all encountered children
    if root.includes is None:
        root.includes = []
    root.includes += [tpl]

    # In order to load the questions, we need to recurse into
    # all files and build the questions list by priority, the
    # inclusion order
    return _recurse(tpl, root)


def _recurse(tpl, root):
    for other in tpl.children:
        other = find(other)
        other = load(other, root)
        tpl = _merge(tpl, other)
    return tpl


def _merge(tpl, other):
    # Merge questions.
    # Since the "name" must be unique, we use it as a key
    # other has priority on self
    result = {i["name"]: i for i in other.data["questions"]}
    for question in tpl.data["questions"]:
        result[question["name"]] = question
    tpl.data["questions"] = [v for k, v in result.items()]

    # Sort by order if present
    tpl.data["questions"] = sorted(tpl.data["questions"], key=lambda item: item.get("order", 0))

    return tpl
