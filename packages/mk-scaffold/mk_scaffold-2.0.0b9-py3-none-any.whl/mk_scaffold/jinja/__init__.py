from datetime import datetime
from pathlib import Path

from .environment import StrictNativeEnvironment


def create(opts=None):
    opts = opts or {}
    ctx = {
        "scaffold": {},
        "year": datetime.now().year,
        "curdir": str(Path.cwd()),
    }
    env = StrictNativeEnvironment(**opts)
    return env, ctx


def ctx_add(ctx, key, value):
    ctx["scaffold"][key] = value
    return ctx
