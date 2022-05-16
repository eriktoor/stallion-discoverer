"""
To update the script to run it on a local repo change 
1. the extensions on line 55
2. the # weeks on line 56
3. the dirpath on line 59
Git blame increases in time with > commits in a repo: https://bugs.chromium.org/p/git/issues/detail?id=18
"""

import time, os, pathlib, re

num_files = 0 

def get_contributors_for_file(directory, filepath, extensions, weeks):
    # Step 1: if the file doesn't have the correct extension, return
    if pathlib.Path(filepath).suffix not in extensions: return []

    global num_files 
    num_files += 1 

    # Step 2: If there is a weeks argument, add the since arg to the git command
    since = "--since={weeks}.weeks -- ".format(weeks=weeks)
    if weeks == 0: since = ""

    # Step 3: Do the git blame command and get the output
    command = "git -C {directory} blame {since}{filepath}".format(directory=directory, filepath=filepath, since=since)
    # "git -C /Users/etoor/dir blame /Users/etoor/specificfile.ext"
    all_lines  = os.popen(command).readlines()

    # Step 4: Get the output from all lines
    ret = []
    for line in all_lines:
        # https://stackoverflow.com/questions/42539892/git-blame-see-changes-after-a-certain-date
        if line and line[0] == "^": continue # any line before the since arg will start with ^ 
        if "(" in line and ")" in line: 
            blame = line.split("(")[1].split(")")[0]
            user = re.split('[\d]{4}-[\d]{2}', blame)[0].strip()
            ret.append(user)

    return ret

def get_all_files(dirpath): 
    all_files = []

    for dirpath, dnames, fnames in os.walk(dirpath):
        for f in fnames: 
            full_file = os.path.join(dirpath, f)
            all_files.append((dirpath, full_file))

    return all_files
 

def main():
    # Define hmap, extensions we want to get, weeks we want to read, dirpath
    contributors_hmap = {}
    extensions = [".go", ".py"]
    weeks = 50  
    start_time = time.time()

    dirpath = "/Users/etoor/Desktop/open-source/go-ethereum"

    # Step 1: Walk the file tree (get all files)
    all_dirs_and_files = get_all_files(dirpath)

    # Step 2: For each file, run the git blame and get the authors of each line 
    # Step 3: Aggregate the results of the git blame into a hashmap 
    for dirpath, filepath in all_dirs_and_files:
        list_of_contributors = get_contributors_for_file(dirpath, filepath, extensions, weeks)
        for name in list_of_contributors:
            if name in contributors_hmap: 
                contributors_hmap[name] += 1 
            else: 
                contributors_hmap[name] = 1 


    print(contributors_hmap)
    print("Results obtained in:", time.time() - start_time, "seconds")
    print(num_files, "files blamed")
    total = 0 
    for name in contributors_hmap: 
        total += contributors_hmap[name]
    print(total, "total lines")

if __name__ == "__main__":
    main()
