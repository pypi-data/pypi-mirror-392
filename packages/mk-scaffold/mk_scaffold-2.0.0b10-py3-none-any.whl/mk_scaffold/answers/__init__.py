import copy
import json
import sys

import yaml

from .. import constants as c
from .. import jinja, utils
from . import schema


def load(filepath):
    if not filepath:
        return None

    try:
        with open(filepath, encoding="UTF-8") as fd:
            data = yaml.safe_load(fd)
    except Exception as err:
        sys.exit(f"error: failed to open '{filepath}': {err}")

    if data is None:
        data = {}
    data = {"answers": data.get("answers")}

    return data


def validate(data):
    yaml_schema = yaml.safe_load(schema.SCHEMA)
    validator = schema.LocalValidator(yaml_schema)

    if data is None:
        data = {}
    else:

        if not validator.validate(data):
            locations = str(json.dumps(validator.errors, indent=2))
            raise SystemExit(f"error: YAML answer file schema validation error. Location:\n{locations}") from None

    return validator.normalized(data)


def process(data, env, ctx):
    if data is None:
        return ctx

    answers = data.get("answers", {})
    if answers is None:
        return ctx

    for k, v in answers.items():
        v = utils.eval_string(v, env, ctx)
        ctx = jinja.ctx_add(ctx, k, v)
    return ctx
