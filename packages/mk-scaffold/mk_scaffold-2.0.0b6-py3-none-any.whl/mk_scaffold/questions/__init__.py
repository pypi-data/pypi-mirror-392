"""
Ask questions and answer them by prompting the user

Special cases to be handled:
- ctrl-d: Set value to None

"""

import sys
from contextlib import nullcontext

import prompt_toolkit
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.validation import ValidationError, Validator

from .. import jinja, utils
from .validators import allowed, max_length, max_value, min_length, min_value, nullable, vartype

bindings = KeyBindings()


# pylint: disable=redefined-outer-name
def _stdin_input(prompt):
    """
    Convenience function in order to mock the builtin
    """
    return input(prompt)


def _validate(value, schema):
    """
    Validate the answer and return modified answer if needed.

    Return value + stop (True/False)
    """
    # Order matters. By checking nullable and default first
    # we can make assumptions on values (null? not null? etc.)
    validators = [
        vartype,
        nullable,
        allowed,
        max_length,
        min_length,
        min_value,
        max_value,
    ]

    # Returns (value, True) if we are to stop iterating,
    # we are to replace value by a new value
    for validator in validators:
        value, stop = validator.validate(value, schema)
        if stop is True:
            return value
    return value


def _prepare(question, env, ctx):
    """
    Determine if the question is to be asked, and
    if so, build a prompt

    Return true if question is to be asked.
    """

    # Prepare all values in order to have an json snapshot of
    # every question
    name = question["name"]

    # Schema might not be present by default
    schema = question.get("schema", {})
    question["schema"] = schema

    prompt = name
    prompt = str(utils.eval_string(prompt, env, ctx))
    prompt += ": "
    question["prompt"] = prompt

    description = question.get("description")
    question["description"] = str(utils.eval_string(description, env, ctx))

    hidden = question.get("hidden", False)
    question["hidden"] = utils.eval_string(hidden, env, ctx)

    # Will we prompt this question?
    condition = question.get("if")
    condition = utils.eval_string(condition, env, ctx)
    if condition is not None:
        question["if"] = condition
        if not condition:
            return False

    # Set the answer as the "default", override if necessary
    # any previous "default" value
    # It will be eval'd during the "default" code block
    answer = ctx["scaffold"].get(question["name"])
    if answer is not None:
        schema["default"] = answer

    # Prepare the default value
    default = schema.get("default")
    default = utils.eval_string(default, env, ctx)
    if default is None:
        schema.pop("default", None)
    else:
        schema["default"] = default
    return True


def prompt(tpl, ctx):
    """
    For every question in the input file, ask the question
    and record the answer in the context
    """
    env, _ = jinja.create(tpl.data["jinja2"])

    questions = tpl.data["questions"]
    for question in questions:
        if not _prepare(question, env, ctx):
            continue

        name, value = _prompt(question)

        question["value"] = value
        ctx = jinja.ctx_add(ctx, name, value)

    return tpl, env, ctx


def _prompt(question):
    """
    Ask the question until it is answered or canceled

    Returns key, value
    """
    name = question.get("name")
    prompt = question.get("prompt")
    hidden = question.get("hidden")
    description = question.get("description")
    schema = question.get("schema")
    default = schema.get("default")

    def prevalidate(x, schema):
        # Exceptions are raised, always return True
        _validate(x, schema)
        return True

    validator = Validator.from_callable(lambda x: prevalidate(x, schema))

    while True:
        try:
            # if hidden, then return default, which was previously set to
            # the value in answer if present, and otherwise
            # to the default from scaffold.yml
            if hidden:
                answer = default
            elif sys.stdin.isatty():
                kwargs = {}
                if default is not None:
                    kwargs["default"] = str(default)

                answer = prompt_toolkit.prompt(
                    prompt,
                    validator=validator,
                    bottom_toolbar=description,
                    key_bindings=bindings,
                    validate_while_typing=False,
                    **kwargs,
                )
            else:
                answer = _stdin_input(prompt)
            answer = _validate(answer, schema)
            return name, answer

        except EOFError:
            # ctrl-d was used
            try:
                answer = _validate(None, schema)
                return name, answer
            except ValidationError:
                continue
