from main import (
    all_files_by_extension,
    get_contributors_for_file,
    all_files_by_extension_git,
    get_git_toplevel,
)

from collections import Counter
from os import popen
from pathlib import Path
from collections import defaultdict


def test_get_all_files():
    dirpath = Path('tests/data/walk_test')
    extensions = {".go", ".py", ".txt"}
    directory_exclusions = {'.pytest_cache',
                            '.venv',
                            '.idea',
                            '.git'}
    top_level_path = get_git_toplevel(dirpath=dirpath)
    file_list = list(all_files_by_extension(top_level_path=top_level_path,
                                            extensions=extensions,
                                            exclude_dirs=directory_exclusions))

    assert len(file_list) == 7

def test_get_contributors_for_file():
    top_level_path = get_git_toplevel('.')
    dirpath = top_level_path / 'tests/data/walk_test/test01/test03/test01.go'
    actual_result = Counter(get_contributors_for_file(top_level_path=top_level_path, filepath=dirpath, weeks=1))
    expected_result = Counter({'Bruce W. Lowther': 2})
    assert actual_result == expected_result


