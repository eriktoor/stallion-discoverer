"""
Video: https://www.youtube.com/watch?v=nXSUSkm0UC4
To update the script to run it on a local repo change 
1. the extensions on line 55
2. the # weeks on line 56
3. the dirpath on line 59
Git blame increases in time with > commits in a repo: https://bugs.chromium.org/p/git/issues/detail?id=18
"""
import asyncio

import time
import os
import re
from typing import List, Generator, Set, Optional, Tuple, Iterable
from pathlib import Path
from collections import defaultdict, Counter
from itertools import chain
import asyncio
import io
import locale
import subprocess

import logging
from pprint import pprint

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv('LOGLEVEL', 'WARNING'))

# Compile the re used to grab the committer once for later use.
git_line_porcelain_action_re = re.compile('^(?P<action>committer) (?P<value>.*)$')
git_blame_command_template = "git -C {directory} blame --line-porcelain {since} -- {filepath}"


# not my code
# from: https://github.com/BobBuildTool/bob
async def asyncio_popen(args, universal_newlines=False, check=False, shell=False, **kwargs):
    """Provide the subprocess.run() function as asyncio corouting.

    This takes care of the missing 'universal_newlines' and 'check' options.
    Everything else is passed through. Will also raise the same exceptions as
    subprocess.run() to act as a drop-in replacement.
    """

    if shell:
        proc = await asyncio.create_subprocess_shell(args, **kwargs)
    else:
        proc = await asyncio.create_subprocess_exec(*args, **kwargs)
    stdout, stderr = await proc.communicate()

    if universal_newlines and (stdout is not None):
        stdout = io.TextIOWrapper(io.BytesIO(stdout)).read()
    if universal_newlines and (stderr is not None):
        stderr = io.TextIOWrapper(io.BytesIO(stderr)).read()

    if check and (proc.returncode != 0):
        raise subprocess.CalledProcessError(proc.returncode, args,
                                            stdout, stderr)

    return subprocess.CompletedProcess(args, proc.returncode, stdout,
                                       stderr)


async def get_contributors_for_file(top_level_path: Path,
                                    filepath: Path,
                                    weeks: Optional[int] = None) -> List[str]:
    """
    given a file, use `git blame` to identify the committer for each line in
    the file.  Accumulate the distinct committers and return them
    :param top_level_path: must provide the base git repo directory path
    :param filepath: The file to investigate with `git blame`
    :param weeks: Parameter to `git blame` see `--since` option
    :return: return a list committers.
    """
    # Step 2: If there is a weeks argument, add the since arg to the git command
    since = f"--since={weeks}.weeks" if weeks else ""
    # Step 3: Do the git blame command and get the output
    # use '--line-porcelain' to reduce the parsing burden
    command = git_blame_command_template.format(directory=top_level_path, since=since, filepath=filepath)
    # Step 4: Get the output from all lines
    try:
        ret = list()
        completed_process = await asyncio_popen(command,
                                                shell=True,
                                                universal_newlines=True,
                                                stdout=subprocess.PIPE)

        for line in completed_process.stdout.splitlines():
            line = line.strip()
            if porcelain_info := git_line_porcelain_action_re.search(line):
                if porcelain_info.group('action') == 'committer':
                    ret.append(porcelain_info.group('value'))
        return ret
    except UnicodeDecodeError as uedc:
        logger.warning(f"could not process file {filepath}. error: {uedc}")
        return []


async def all_files_by_extension_git(top_level_path: Path, extensions: Optional[Set[str]] = None) -> Generator[
    Path, None, None]:
    """
    dirpath must be the root directory for the git repo.  Should be same as `git -C {directory} rev-parse
    --show-toplevel`
    ```
    brucelowther@bruces-mbp NetHack % git -C . rev-parse --show-toplevel
    /Users/brucelowther/src/NetHack
    ```
    Use `git ls-tree -r --full-name --name-only HEAD`
    to fetch all the filenames that are managed in this git repo.
    Rather than searching
    """
    git_ls_tree_command_template = 'git -C {directory} ls-tree -r --full-name --name-only HEAD'

    if not top_level_path.exists():
        raise ValueError(f"dirpath must exist {top_level_path}")
    toplevel_dir = get_git_toplevel(top_level_path)
    if top_level_path != toplevel_dir:
        raise ValueError(f"dirpath must be root of git repository. git says {toplevel_dir} is root")

    command = git_ls_tree_command_template.format(directory=top_level_path.absolute())
    for line in os.popen(command).readlines():
        filename = top_level_path.joinpath(line.strip()).absolute()
        if extensions is None:
            yield filename
        else:
            if filename.suffix in extensions:
                yield filename


def get_git_toplevel(dirpath: Path) -> Path:
    git_toplevel_command_template = 'git -C {directory} rev-parse --show-toplevel'
    toplevel_dir = os.popen(git_toplevel_command_template.format(directory=dirpath)).readline().strip()
    return Path(toplevel_dir)


async def all_files_by_extension(top_level_path: Path,
                                 extensions: Set[str],
                                 exclude_dirs: Optional[Set[str]] = None) -> Generator[Path, None, None]:
    """
    :param dirpath: The base directory for a git repository `git rev-parse --show-toplevel`
    :param extensions: the files that have these extensions will be included.
    :param exclude_dirs: any subdirectory by this name will be excluded. (for example, .git or .venv)  If not
    supplied then do not exclude any
    :return: Generator that wil provide all files in the directory and any sub-directory meeting the critera.
    """
    if not top_level_path.exists():
        raise ValueError(f"dirpath must exist {top_level_path}")
    exclude_dirs = exclude_dirs if exclude_dirs else []
    for base, dirnames, files in os.walk(top_level_path):
        # don't go down directories that are excluded at any level.
        # have to use del here on dirnames (see docs for os.walk)
        for exclude_dir in exclude_dirs:
            try:
                item_idx = dirnames.index(exclude_dir)
                del dirnames[item_idx]
            except ValueError:
                # excluded_dir doesn't exist in dirnames.  Throws Value error and it is ignored.
                pass

        for file in [Path(base).joinpath(f) for f in files if Path(f).suffix in extensions]:
            yield file


async def main():
    # Define hmap, extensions we want to get, weeks we want to read, dirpath
    contributors_hmap = Counter()
    extensions = {".c", ".py", ".txt"}
    exclude_directories = {'.git'}
    weeks = 52
    start_time = time.time()

    dirpath = Path("/Users/brucelowther/src/NetHack")

    print(f"Processing Git Directory:{dirpath}")
    # Step 1: Walk the file tree (get all files)
    # Step 2: For each file, run the git blame and get the authors of each line 
    # Step 3: Aggregate the results of the git blame into a hashmap
    result_set_corlist = [get_contributors_for_file(top_level_path=dirpath, filepath=f, weeks=weeks)
                          async for f in
                          all_files_by_extension(dirpath, extensions)]

    #Run all the files in parallel and finish when they have all completed.
    file_info_result_list = await asyncio.gather(*result_set_corlist, return_exceptions=False)
    for l in file_info_result_list:
        contributors_hmap = contributors_hmap + Counter(l)

    # contributors_hmap = Counter(chain(*file_info_result_list))
    print(f"Results obtained in:{time.time() - start_time} seconds")
    contributors_total = sum(contributors_hmap.values())
    print(f"Contributor total lines: {contributors_total}")
    pprint(contributors_hmap, sort_dicts=True)


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
