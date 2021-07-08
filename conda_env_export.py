"""
Export a Conda environment with --from-history, but also append
Pip-installed dependencies

For `conda env export`, we dont use the following two commands, but this py file instead.

Reasons:
- `Conda env export --from-history -f conda_env.yaml` does not contain pip installments
- `Conda env export -f conda_env.yaml` pins dependencies too hard (add conda build number,
which is os dependent, add os-denpendent libs as well).

This is adopted from https://gist.github.com/gwerbin/dab3cf5f8db07611c6e0aeec177916d8

Example:
    In root folder of this repo:
    >>> which python # make sure you are in the right virtual env
    >>> python conda_env_export.py # a better alternative than `conda env export`
"""

import subprocess
import logging

logger = logging.getLogger(__name__)


def export_env(history_only=False, include_builds=False):
    """Capture `conda env export` output"""
    cmd = ["conda", "env", "export"]
    if history_only:
        cmd.append("--from-history")
        if include_builds:
            raise ValueError('Cannot include build versions with "from history" mode')
    if not include_builds:
        cmd.append("--no-builds")
    cp = subprocess.run(cmd, stdout=subprocess.PIPE)
    output = cp.stdout.decode("utf-8")

    # get header and conda dependencies from history-only mode, and pip dependencies from non history_only mode:
    is_useful = (
        True if history_only else False
    )  # retain the header and conda part if history_only
    result = []
    for line in output.splitlines():
        is_useful = set_usefulness(
            line, is_useful, history_only
        )  # remove none pip parts if in history only mode
        result.append(line) if is_useful else None
    return "\n".join(result)


def set_usefulness(line, is_useful, history_only):
    if "pip" in line and "pip=" not in line:
        is_useful = False if history_only else True  # get pip if not history only
    if "prefix" in line:
        is_useful = False  # remove prefix what-so-ever
    return is_useful


def main():
    env_data_pip = export_env(history_only=False)
    env_data_conda = export_env(history_only=True)
    env_data = env_data_conda + "\n" + env_data_pip
    with open("conda_env.yml", "w") as f:
        f.write(env_data)
    print(
        """
        Conda env export successfully done.
        Please check file 'conda_env.yml' before push to pip, making sure no un-safe dependencies are accidentally
        listed in the dependency file.
        """
    )


if __name__ == "__main__":
    main()
