from libs.wad_parser.get_default_wad import download_wad_file, decompress_wad
from libs.differ.diff_directories import diff_directories
from libs.wad_parser.parser import extract_header_info, save_files, identify_unknown_file_types
from natsort import natsorted
import os



def extract(version):
    import json
    import zlib

    with open('hashes.json') as f:
        file_hashes = json.load(f)
    with open('signatures.json') as f:
        signatures = json.load(f)
    with open('ignore.json') as f:
        ignore = json.load(f)

    directory = version.replace(".", "_")
    os.makedirs(directory, exist_ok=True)
    wad_filename = f"{version.replace('.', '_')}-default-assets.wad"

    print("Loading data...")
    with open(wad_filename, "rb") as f:
        data = f.read()
    if wad_filename.endswith(".compressed"):
        print("Decompressing data...")
        data = zlib.decompress(data)

    print("Loading headers...")
    headers = extract_header_info(data, file_hashes, signatures)
    print(f"Got {len(headers)} headers/files.")

    print("Saving files...")
    save_files(directory, data, headers, ignore=ignore)

    print("Identifying the type of unknown files...")
    identify_unknown_file_types(directory)



def main():
    import urllib.error
    import wget
    import shutil
    import json

    versions_url = "http://l3cdn.riotgames.com/releases/live/projects/lol_game_client/releases/releaselisting"
    wget.download(versions_url, "solution_versions.txt")
    with open("solution_versions.txt") as f:
        versions = f.readlines()
        versions = [line.strip() for line in versions]
    os.remove("solution_versions.txt")
    versions = natsorted(versions, reverse=True)
    #print(versions)

    #filename, output_filename = ("default-assets.wad.compressed", "0_0_1_85-default-assets.wad")
    #print("Decompressing...")
    #decompress_wad(filename, output_filename)

    #filename, output_filename = ("default-assets.wad (1).compressed", "0_0_1_83-default-assets.wad")
    #print("Decompressing...")
    #decompress_wad(filename, output_filename)

    #filename, output_filename = ("default-assets.wad (2).compressed", "0_0_1_81-default-assets.wad")
    #print("Decompressing...")
    #decompress_wad(filename, output_filename)


    download = False
    if download:
        bad_versions = []
        successful = 0
        for version in versions:
            try:
                filename = download_wad_file(version)
                successful += 1
                print(f"Versions {bad_versions} don't exist :(")
            except urllib.error.HTTPError:
                bad_versions.append(version)
                print(f"Versions {bad_versions} don't exist :(")
                continue
            if filename.endswith(".compressed"):
                output_filename = filename[:-len(".compressed")]
                output_version = version.replace(".", "_")
                output_filename = f"{output_version}-{output_filename}"
                print("Decompressing...")
                decompress_wad(filename, output_filename)
                os.remove("default-assets.wad.compressed")
        #    if successful >= 3:
        #        break


    already_pulled = []
    for fn in os.listdir("."):
        if "-default-assets.wad" in fn and ".compressed" not in fn:
            version = fn[:-len("-default-assets.wad")].replace("_", ".")
            already_pulled.append(version)
    #print(already_pulled)

    for version in already_pulled:
        direc = version.replace(".", "_")
        if not (os.path.exists(direc) and os.path.isdir(direc)):
            extract(version)

    direc = "."
    direcs = [fn for fn in os.listdir(".") if os.path.isdir(fn) and fn.count("_") == 3]
    direcs = natsorted(direcs)
    print(direcs)

    results = diff_directories(directory_list=direcs, base_path=direc)

    def all_same(items):
        return all(x == items[0] for x in items)

    cutdown = {
        fn: stuff for fn, stuff in results.items()
        if not all_same(list(stuff.values()))
    }

    dump = json.dumps(cutdown, indent=2)
    #print(dump)
    with open("differ_results.json", "w") as f:
        json.dump(cutdown, f, indent=2)

if __name__ == "__main__":
    main()
