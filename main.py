import subprocess
import tempfile
import re 
import os
from pathlib import Path

# "git -C /Users/etoor/... blame /Users/etoor/..."

def get_git_blame_for_file(directory, filepath, extensions, weeks):
    has_ext = False 
    for ext in extensions: 
        if Path(filepath).suffix == ext: has_ext = True 
    if not has_ext: return []

    since = "--since={weeks}.weeks -- ".format(weeks=weeks)
    if weeks == 0:
        since = ""
    

    command = "git -C {directory} blame {since}{filepath}".format(directory = directory, filepath = filepath, since=since)
    commands = command.split(" ")
    with tempfile.TemporaryFile() as tempf:
        proc = subprocess.Popen(commands, stdout=tempf)
        proc.wait()
        tempf.seek(0)
        contents = tempf.read().decode("utf-8")
        all_lines = contents.split("\n")

    ret = []
    for line in all_lines: 
        if line and line[0] == "^": # any line before the time will start with ^
            # https://stackoverflow.com/questions/42539892/git-blame-see-changes-after-a-certain-date
            continue
        if "(" in line and ")" in line: 
            blame = line.split("(")[1].split(")")[0]
            user = re.split('[\d]{4}-[\d]{2}-[\d]{2}', blame)[0].strip()
            ret.append(user)
    
    return ret



def get_all_files(dirpath):
    ret = []
    for dirpath, dnames, fnames in os.walk(dirpath):
        for f in fnames: 
            full_file = os.path.join(dirpath, f)
            ret.append((dirpath, full_file))
            # git -C dirpath blame full_file

    return ret




def main(): 
    hmap = {}

    extensions = [".go", ".js", ".py"]
    weeks = 50 
    dirpath = "/Users/etoor/Desktop/open-source"
    all_dirs_and_files = get_all_files(dirpath)

    for dirpath, filepath in all_dirs_and_files: 
        list_of_contributors = get_git_blame_for_file(dirpath, filepath, extensions, weeks)
        for name in list_of_contributors: 
            if name in hmap: 
                hmap[name] += 1 
            else: 
                hmap[name] = 1 

    print(hmap)


if __name__ == "__main__":
    main()
