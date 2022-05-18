from main import all_files_by_extension, get_contributors_for_file
from os import popen
from pathlib import Path


def test_get_all_files():
    dirpath = Path('tests/data/walk_test')
    extensions = {".go", ".py", ".txt"}
    directory_exclusions = {'.pytest_cache',
                            '.venv',
                            '.idea',
                            '.git'}
    file_list = list(all_files_by_extension(dirpath=dirpath, extensions=extensions,
                                            exclude_dirs=directory_exclusions))

    os_command = f'find {dirpath} -type f'
    expected_files_stream = popen(os_command)
    expected_files = expected_files_stream.readlines()

    assert len(file_list) == 5

def test_get_contributors_for_file():
    dirpath = Path('tests/data/walk_test/test01/test03/test01.go').absolute()
    actual_result = get_contributors_for_file(dirpath, 1)
    expected_result = {'Bruce Lowther'}
    assert actual_result == expected_result