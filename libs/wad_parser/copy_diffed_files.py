import json
import os
import shutil
from natsort import natsorted
from itertools import tee


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def split_all(path):
    return os.path.normpath(path).split(os.path.sep)


def copy_file(filename, versions, directory):
     versions = natsorted(versions.items())
     first_version, first_path = versions[0][0], split_all(versions[0][1])
     _directory = os.path.join(directory, *first_path)
     _head, _ = os.path.split(_directory)
     #print(_head)
     os.makedirs(_head, exist_ok=True)
     #print(os.path.join(*first_path), _directory)
     shutil.copy(os.path.join(*first_path), _directory)

     for (pversion, ppath), (nversion, npath) in pairwise(versions):
         if npath != ppath:
             npath = split_all(npath)
             _directory = os.path.join(directory, *npath)
             _head, _ = os.path.split(_directory)
             #print(_head)
             os.makedirs(_head, exist_ok=True)
             #print(os.path.join(*npath), _directory)
             shutil.copy(os.path.join(*npath), _directory)


def main():
    with open("differ_results.json") as f:
        diffed_files = json.load(f)

    #filename = "rcp-be-lol-game-data/global/default/v1/champion-ability-icons/shadowninja_w.png"
    for i, (filename, versions) in enumerate(diffed_files.items()):
        print(i, len(diffed_files), filename)
        copy_file(filename, versions, "versions")


if __name__ == "__main__":
    main()