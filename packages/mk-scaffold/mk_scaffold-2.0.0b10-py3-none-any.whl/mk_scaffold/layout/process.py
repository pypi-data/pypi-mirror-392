import os
import shutil


def _if(item, env, ctx):
    retval = item["if"]
    if retval not in [True, False]:
        retval = env.from_string(retval).render(**ctx)
    return retval


def _action_move(item, env, ctx, output_dir):

    src = str(env.from_string(item["src"]).render(**ctx))
    src = os.path.join(output_dir, src)

    dst = str(env.from_string(item["dst"]).render(**ctx))
    dst = os.path.join(output_dir, dst)
    # Ensure path is subpath
    # TODO   if not Path(dst).is_relative_to(output_dir):
    #        print(f'warning: skipping path "{dst_orig}" as it is not relative to output path.', file=sys.stderr)
    #        return

    if _if(item, env, ctx):
        if os.path.exists(src):
            shutil.move(src, dst)
    elif item.get("else") == "remove":
        # TODO if not Path(src).is_relative_to(output_dir):
        # TODO     print(f'warning: skipping path "{src}" as it is not relative to output path.', file=sys.stderr)
        # TODO     return
        if os.path.exists(src):
            os.remove(src)


def _action_remove(item, env, ctx, output_dir):
    if not _if(item, env, ctx):
        return

    for path in item["path"]:
        path = str(env.from_string(path).render(**ctx))
        path = os.path.join(output_dir, path)

        # Ensure path is subpath
        # TODOif not Path(path).is_relative_to(output_dir):
        # TODO    print(f'warning: skipping path "{path_orig}" as it is not relative to output path.', file=sys.stderr)
        # TODO    continue

        if os.path.islink(path) or os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)


def _action_remove_nl(item, env, ctx, output_dir):
    if not _if(item, env, ctx):
        return

    for path in item["path"]:
        path = str(env.from_string(path).render(**ctx))
        path = os.path.join(output_dir, path)

        with open(path, encoding="UTF-8") as fd:
            data = fd.read()
        data = data.rstrip()
        with open(path, mode="w", encoding="UTF-8") as fd:
            fd.write(data)


def _process(tpl, env, ctx, output_dir):
    for item in tpl.actions:
        action = item["action"]
        if action == "move":
            _action_move(item, env, ctx, output_dir)
        elif action == "remove":
            _action_remove(item, env, ctx, output_dir)
        elif action == "remove-trailing-newline":
            _action_remove_nl(item, env, ctx, output_dir)
        else:
            assert False
    return tpl


def process(tpl, env, ctx, **kwargs):
    output_dir = kwargs["output_dir"]

    items = reversed(tpl.includes)
    for item in items:
        _process(item, env, ctx, output_dir)

    return tpl
