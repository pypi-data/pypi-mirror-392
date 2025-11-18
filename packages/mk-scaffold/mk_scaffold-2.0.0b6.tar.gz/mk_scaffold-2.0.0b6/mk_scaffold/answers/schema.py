# vim: foldmarker=[[,]] foldmethod=marker
import cerberus

# https://docs.python-cerberus.org/en/stable/validation-rules.html
SCHEMA = r"""
---
answers: # [[
  type: dict
  default: {}
  nullable: true
  keysrules:
    type: string
    regex: '[a-zA-Z0-9_]+'
# ]]
"""


class LocalValidator(cerberus.Validator):
    pass
