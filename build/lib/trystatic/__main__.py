#!/usr/bin/python3
import monkeytype
from trystatic import util
import sys
import argparse
import os
import re
import subprocess
from collections import defaultdict
sys.path.append("../")


# def remove_clone_archive(path, clone_path, is_fatal):
#     """Remove temporary clone_archive git folder."""
#     try:
#         util.call(f"rm -rf {clone_path}", cwd=path)
#     except subprocess.CalledProcessError as err:
#         if is_fatal:
#             util.print_fatal("Unable to remove {}: {}".format(clone_path, err))


def main() -> None:
    cwd_root = os.getcwd()
    #cwd_root = "/insilications/build/git-clr/clazy-clr/build/"
    print(f"cwd_root: {cwd_root}")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--targetdir",
        action="store",
        dest="targetdir",
        default=cwd_root,
        help="Target root CWD",
    )
    parser.add_argument(
        "-i",
        "--ignorelibs",
        action="store",
        dest="ignorelibs",
        default="",
        help="Libraries to ignore: --ignorelibs=llibrary1,llibrary2,..",
    )
    parser.add_argument(
        "-f",
        "--files",
        action="store",
        dest="files_to_search",
        default=".cmake,Makefile,.txt",
        help="Files to search in (regex): --files=.cmake,Makefile,.txt,.. (Makefile matches Makefile2 too)",
    )
    args = parser.parse_args()
    targetdir = args.targetdir
    ignorelibs = args.ignorelibs
    files_to_search = args.files_to_search
    print(f"targetdir: {targetdir}")
    ignorelibs_list_tmp = []
    ignorelibs_list = []
    if ignorelibs:
        # print(f"ignorelibs: {ignorelibs}")
        ignorelibs_list_tmp = ignorelibs.split(",")
        ignorelibs_list_tmp = list(filter(None, ignorelibs_list_tmp))
        for lib in ignorelibs_list_tmp:
            if lib[1] == "l" and lib[2] != "l":
                ignorelibs_list.append(lib[1:])
            else:
                ignorelibs_list.append(lib)
        print(f"ignorelibs_list: {ignorelibs_list}")
    files_to_search_list = []
    if files_to_search:
        # print(f"files_to_search: {files_to_search}")
        files_to_search_list = files_to_search.split(",")
        files_to_search_list = list(filter(None, files_to_search_list))
        print(f"files_to_search_list: {files_to_search_list}")
    rg_cmd = r"rg -uu --type cmake --type txt --no-line-number --no-filename --only-matching  --replace '$2' '(\s\-l)(\w+)'"
    try:
        process = subprocess.run(
            rg_cmd,
            check=True,
            shell=True,
            stdout=subprocess.PIPE,
            text=True,
            universal_newlines=True,
            cwd=targetdir,
        )
    except subprocess.CalledProcessError as err:
        util.print_fatal(f"Unable to run rg to search for possible libraries inside {targetdir}: {err}")
        sys.exit(1)

    output_rg_cmd = process.stdout.rstrip("\n").split()
    util.write_out("output_rg_cmd.txt", str(output_rg_cmd))
    # print(output_rg_cmd)
    list_libs = list(set(output_rg_cmd))
    # print(f"list_libs: {list_libs}")
    lib_list_re_exclude_so_default = r"(c\b|GL\b|gomp\b|pthread\b|stdc\+\+\B|gcc_s\b|gcc_eh\b|gcc\b|rt\b|dl\b|m\b"
    if len(ignorelibs_list) > 0:
        for lib in ignorelibs_list:
            # print(f"lib: {lib}")
            lib_list_re_exclude_so_default = f"{lib_list_re_exclude_so_default}" r"|" f"{lib}" r"\b"
        lib_list_re_exclude_so_default = f"{lib_list_re_exclude_so_default}" r")"
    else:
        lib_list_re_exclude_so_default = r"(c\b|GL\b|gomp\b|pthread\b|stdc\+\+\B|gcc_s\b|gcc_eh\b|gcc\b|rt\b|dl\b|m\b)"
    print(f"lib_list_re_exclude_so_default: {lib_list_re_exclude_so_default}")
    lib_list_re_exclude_so = re.compile(lib_list_re_exclude_so_default)
    lib_list_re_transform = re.compile(r"(?<=lib)(\w+)(?=\.a)")
    libs_dict = defaultdict(list)
    list_libs_full_name = []
    for lib in list_libs:
        if re.search(lib_list_re_exclude_so, lib) is None:
            list_libs_full_name.append(f"lib{lib}.a")
    print(f"list_libs_full_name: {list_libs_full_name}\n")
    for dirpath, dirnames, filenames in os.walk("/usr/lib64", followlinks=True):
        for lib in list_libs_full_name:
            for filename in filenames:
                if lib == filename:
                    full_match = os.path.join(dirpath, filename)
                    libs_dict[lib].append(full_match)
                    # print(f"libs_dict[{lib}]: {full_match}")
                    break
    for key, value in libs_dict.items():
        lib_list_re_transform_result = re.search(lib_list_re_transform, key)
        if lib_list_re_transform_result is not None:
            match = r"\-l" f"{lib_list_re_transform_result.group(0)}"
            full_name = "".join(value)
            print(f"{key}: {full_name} - match: {match}")
            for search in files_to_search_list:
                sd_cmd = f"sd --flags m '{match}' '{full_name}' $(fd -uu {search})"
                try:
                    process = subprocess.run(
                        sd_cmd,
                        check=True,
                        shell=True,
                        stdout=subprocess.PIPE,
                        text=True,
                        universal_newlines=True,
                        cwd=targetdir,
                    )
                except subprocess.CalledProcessError as err:
                    util.print_fatal(f"cmd: {sd_cmd}")
                    util.print_fatal(f"Unable to run sd to replace libraries invocations inside {targetdir}: {err}")


if __name__ == "__main__":

    main()
    # collect_types.dump_stats("dump.json")
