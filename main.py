"""
Video: https://www.youtube.com/watch?v=nXSUSkm0UC4
To update the script to run it on a local repo change 
1. the extensions on line 55
2. the # weeks on line 56
3. the dirpath on line 59
Git blame increases in time with > commits in a repo: https://bugs.chromium.org/p/git/issues/detail?id=18
"""

import time
import os
import re
from typing import List, Generator, Set, Optional, Tuple
from pathlib import Path
from collections import defaultdict
import logging
from pprint import pprint

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv('LOGLEVEL', 'DEBUG'))


# Compile the re used to grab the committer once for later use.
git_line_porcelain_action_re = re.compile('^(?P<action>committer) (?P<value>.*)$')

def get_contributors_for_file(filepath: Path,
                              weeks: Optional[int] = None) -> Set:
    """
    given a file, use `git blame` to identify the committer for each line in
    the file.  Accumulate the distinct committers and return them
    :param filepath: The file to investigate with `git blame`
    :param weeks: Parameter to `git blame` see `--since` option
    :return: return a set of distinct committers.
    """
    # Step 2: If there is a weeks argument, add the since arg to the git command
    since = f"--since={weeks}.weeks" if weeks else ""
    directory = filepath.parent
    # Step 3: Do the git blame command and get the output
    # use '--line-porcelain' to reduce the parsing burden
    command = f"git -C {directory} blame --line-porcelain {since} -- {filepath}"
    # "git -C /Users/etoor/dir blame /Users/etoor/specificfile.ext"

    # Step 4: Get the output from all lines
    try:
        ret = set()
        line_count = 0
        for line in os.popen(command).readlines():
            line = line.strip()
            if porcelain_info := git_line_porcelain_action_re.search(line):
                if porcelain_info.group('action') == 'committer':
                    ret.add(porcelain_info.group('value'))
        return ret
    except UnicodeDecodeError as uedc:
        logger.warning("could not process file: {f} error: {uedc}")
        return set()

def all_files_by_extension(dirpath: Path,
                           extensions: Set[str],
                           exclude_dirs: Optional[Set[str]]=None) -> Generator[Path,None,None]:
    """
    :param dirpath: The base directory for a git repository `git rev-parse --show-toplevel`
    :param extensions: the files that have these extensions will be included.
    :param exclude_dirs: any subdirectory by this name will be excluded. (for example, .git or .venv)  If not
    supplied then do not exclude any
    :return: Generator that wil provide all files in the directory and any sub-directory meeting the critera.
    """
    if not dirpath.exists():
        raise ValueError(f"dirpath must exist {dirpath}")
    exclude_dirs = exclude_dirs if exclude_dirs else []
    for base, dirnames, files in os.walk(dirpath):
        # don't go down directories that are excluded at any level.
        # have to use del here on dirnames (see docs for os.walk)
        for exclude_dir in exclude_dirs:
            try:
                item_idx = dirnames.index(exclude_dir)
                del dirnames[item_idx]
            except ValueError:
                # excluded_dir doesn't exist in dirnames.  Throws Value error and it is ignored.
                pass

        for file in [dirpath.joinpath(base, f).absolute() for f in files if Path(f).suffix in extensions]:
            yield file

def main():
    # Define hmap, extensions we want to get, weeks we want to read, dirpath
    contributors_hmap = defaultdict(int)
    extensions = {".c", ".py", ".txt"}
    exclude_directories = {'.git'}
    weeks = 52
    start_time = time.time()

    dirpath = Path("/Users/brucelowther/src/NetHack")

    print(f"Processing Git Directory:{dirpath}")
    # Step 1: Walk the file tree (get all files)
    # Step 2: For each file, run the git blame and get the authors of each line 
    # Step 3: Aggregate the results of the git blame into a hashmap
    for file_index, f in enumerate(all_files_by_extension(dirpath, extensions, exclude_dirs=exclude_directories)):
        print(f"{file_index}:{f}")
        for name in get_contributors_for_file(f, weeks):
            contributors_hmap[name] += 1
    print(f"Results obtained in:{time.time() - start_time} seconds")
    contributors_total = sum(contributors_hmap.values())
    print(f"Contributor total lines: {contributors_total}")
    pprint(contributors_hmap, sort_dicts=True)

if __name__ == "__main__":
    main()


