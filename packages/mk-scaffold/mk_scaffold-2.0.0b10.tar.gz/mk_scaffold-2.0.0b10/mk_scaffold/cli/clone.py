import sys

import cloup

from .. import answers, jinja, layout, questions, template
from .cli import cli


def validate_template_file(_ctx, _param, value):
    if value.startswith("/"):
        sys.exit(f'error: template filename "{value}" must be relative path to template directory')
    return value


#
# mk-scaffold clone [OPTIONS] TEMPLATE
#
@cli.command(help="Clone and templatize a repository.")
@cloup.option(
    "-i",
    "--input-file",
    "answer_file",
    metavar="FILE",
    type=cloup.Path(exists=True, dir_okay=False, readable=True),
    help="Location of a yaml input file, usually named '.answers.yml', with answers to the questions.",
)
@cloup.option(
    "-o",
    "--output-dir",
    metavar="DIR",
    default=".",
    type=cloup.Path(file_okay=False, dir_okay=True),
    show_default=False,
    help="Where to output the generated files. [default: current directory]",
)
@cloup.option(
    "--filename",
    "template_filename",
    metavar="FILENAME",
    default="scaffold.yml",
    show_default=True,
    callback=validate_template_file,
    help="Filename of the scaffold file to use.",
)
@cloup.option(
    "-b",
    "--branch",
    metavar="BRANCH",
    default=None,
    show_default=False,
    help="Checkout git BRANCH of git repository",
)
@cloup.argument(
    "template_path",
    nargs=1,
    metavar="TEMPLATE",
    type=cloup.Path(),
    help="Directory or git repository that contains 'scaffold.yml' template file",
)
def clone(**kwargs):
    # Load the answers with a default jinja
    env, ctx = jinja.create()

    answer = answers.load(kwargs.get("answer_file"))
    answer = answers.validate(answer)
    ctx = answers.process(answer, env, ctx)

    tpl = template.Template(**kwargs)
    tpl = template.find(tpl)
    tpl = template.load(tpl)

    tpl, env, ctx = questions.prompt(tpl, ctx)

    tpl = layout.clone(tpl, env, ctx, **kwargs)
    tpl = layout.process(tpl, env, ctx, **kwargs)
