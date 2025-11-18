import os
import sys
import urllib


def accept(tpl, dirpath):
    """
    Uses dirpath and not tpl.path
    """
    # Has to be a directory
    if not os.path.isdir(dirpath):
        return False

    # filepath is the path of the scaffold.yml file, and
    # must exist
    filepath = os.path.join(dirpath, tpl.filename)
    if not os.path.isfile(filepath):
        return False

    # Ensure that filepath is relative to the tpl.path
    real_dirpath = os.path.realpath(dirpath)
    real_filepath = os.path.realpath(filepath)
    if not real_filepath.startswith(real_dirpath):
        sys.exit(f'error: File "{tpl.filename}" is not relative to the template path "{dirpath}"')

    return real_dirpath


def find(tpl):
    # A local directory can also be a git repository
    # So if a branch is specified, don't look for a local
    # directory, but return directly to force the git handler
    if tpl.branch:
        return False

    # If a scheme is detected, it's also not a local directory
    urlpath = urllib.parse.urlparse(tpl.path)
    if urlpath.scheme in ["https", "http"]:
        return False

    if os.path.isfile(tpl.path):
        sys.exit(
            "error: positional argument TEMPLATE should point to a directory, or remote git repository, and not a file",
        )

    return accept(tpl, tpl.path)
