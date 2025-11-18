import atexit
import os
import shutil
import subprocess
import sys
import tempfile

from . import directory


def _get_git():
    retval = shutil.which("git")
    if retval is None:
        print('warning: "git" executable was not found', file=sys.stderr)
    return retval


def _get_tmpdir():
    """
    Create a temporary folder to be deleted at exit
    """
    tmpdir = tempfile.mkdtemp(prefix="scaffold-git-")

    def remove_tmpdir():
        shutil.rmtree(tmpdir)

    atexit.register(remove_tmpdir)
    return tmpdir


def _clone(tpl):
    git = _get_git()
    tmpdir = _get_tmpdir()

    path = tpl.path
    cmdline = [git, "clone", "--single-branch"]
    if tpl.branch:
        cmdline += ["--branch", tpl.branch]
    if os.path.exists(tpl.path) and os.path.isdir(tpl.path):
        # This is a local repository and git prefers with the
        # "file://"
        path = f"file://{tpl.path}"
    else:
        cmdline += ["--depth", "1"]
    cmdline += [path, "repository"]

    try:
        subprocess.run(cmdline, cwd=tmpdir, check=True)
    except subprocess.CalledProcessError as err:
        sys.exit(f'error: failed to clone git repository "{tpl.path}": {err}')

    dirpath = os.path.join(tmpdir, "repository")
    return directory.accept(tpl, dirpath)


def find(tpl):
    """
    path can be a remote git+ssh, or git+http, or even a local path
    if branch is None, we checkout the default branch, usually main or master
    """
    git = _get_git()
    if not git:
        return False
    return _clone(tpl)
