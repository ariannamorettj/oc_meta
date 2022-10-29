#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2022, Silvio Peroni <essepuntato@gmail.com>, Arcangelo Massari <arcangelo.massari@unibo.it>
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.


from __future__ import annotations
from json import load, loads
from oc_meta.lib.file_manager import init_cache
from os import walk, sep
from os.path import isdir, basename
from typing import Tuple
import gzip
import tarfile


def get_all_files(is_dir_or_targz_file:str, cache_filepath:str|None=None) -> Tuple[list, tarfile.TarFile|None]:
    result = []
    targz_fd = None
    cache = init_cache(cache_filepath)
    if isdir(is_dir_or_targz_file):
        for cur_dir, _, cur_files in walk(is_dir_or_targz_file):
            for cur_file in cur_files:
                if (cur_file.endswith(".json") or cur_file.endswith(".json.gz")) and not basename(cur_file).startswith(".") and not cur_file in cache:
                    result.append(cur_dir + sep + cur_file)                    
    elif is_dir_or_targz_file.endswith("tar.gz"):
        targz_fd = tarfile.open(is_dir_or_targz_file, "r:gz", encoding="utf-8")
        for cur_file in targz_fd:
            if cur_file.name.endswith(".json") and not basename(cur_file.name).startswith(".") and not cur_file.name in cache:
                result.append(cur_file)
    else:
        print("It is not possible to process the input path.")
    return result, targz_fd

def load_json(file:str|tarfile.TarInfo, targz_fd:tarfile.TarFile) -> dict|None:
    result = None
    if targz_fd is None:
        if file.endswith(".json"):  # type: ignore
            with open(file, encoding="utf8") as f: # type: ignore
                result = load(f)
        elif file.endswith(".json.gz"): # type: ignore
            with gzip.open(file, 'r') as gzip_file: # type: ignore
                data = gzip_file.read()
                result = loads(data.decode('utf-8'))
    else:
        cur_tar_file = targz_fd.extractfile(file)
        json_str = cur_tar_file.read() # type: ignore
        # In Python 3.5 it seems that, for some reason, the extractfile method returns an 
        # object 'bytes' that cannot be managed by the function 'load' in the json package.
        # Thus, to avoid issues, in case an object having type 'bytes' is return, it is
        # transformed as a string before passing it to the function 'loads'. Please note
        # that Python 3.9 does not show this behaviour, and it works correctly without
        # any transformation.
        if type(json_str) is bytes:
            json_str = json_str.decode("utf-8")
        result = loads(json_str)
    return result
