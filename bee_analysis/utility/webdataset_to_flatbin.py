#!/usr/bin/env python3
"""
Convert one or more WebDataset .tar files into flat .bin files.
This script strips the long "<key>.0.png" names down to "0.png", "1.png", ...
then packages them via dataloaderToFlatbin().
"""

import argparse
import webdataset as wds
import torch
import sys
import os

# adjust this to wherever your flatbin_dataset lives
sys.path.append("/research/projects/grail/ajs787/target/2025-06-06_2025-06-09/Unified-bee-Runner/bee-analysis/utility")

from flatbin_dataset import (
    dataloaderToFlatbin,
    getPatchHeaderNames,
    getPatchDatatypes
)

from flatbin_dataset import (
    dataloaderToFlatbin,
    getPatchHeaderNames,
    getPatchDatatypes
)


def strip_prefix(sample):
    out = {}
    for meta in ("__key__", "__url__", "__local_path__"):
        if meta in sample:
            out[meta] = sample[meta]

    key = sample["__key__"]
    if isinstance(key, bytes):
        key = key.decode("utf-8")
    prefix = key + "."

    for full_name, data in sample.items():
        if full_name in out:
            continue
        if full_name.startswith(prefix):
            suffix = full_name[len(prefix):]
        else:
            suffix = full_name.lstrip(".")
        out[suffix] = data

    return out


def getImageInfo(tar_list):
    image_info = getPatchHeaderNames()
    ds = (
        wds.WebDataset(tar_list)
           .map(strip_prefix)
           .to_tuple(*image_info)
    )
    example = next(iter(ds))
    datatypes = getPatchDatatypes()
    return {
        name: (float(val) if dt is float else int(val))
        for name, val, dt in zip(image_info, example, datatypes)
    }


def convertWebdataset(dataset, entries, output, shuffle, shardshuffle, overrides):
    patch_info = {}

    # Build pipeline: use single-arg handlers because this WebDataset version
    loader = (
        wds.WebDataset(dataset)
           .shuffle(shuffle)
           # .shardshuffle(shardshuffle)  # unsupported
           .decode(
               wds.handle_extension("cls",   lambda data: data),
               wds.handle_extension("png",   lambda data: data),
               wds.handle_extension("txt",   lambda data: data),
               wds.handle_extension("numpy", lambda data: data),
           )
           .map(strip_prefix)
           .to_tuple(*entries)
    )

    dataloaderToFlatbin(loader, entries, output, patch_info, overrides)


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Convert WebDataset .tar → flat .bin with simplified keys"
    )
    p.add_argument("dataset", nargs="+",
                   help="One or more .tar archives to read")
    p.add_argument("--entries", nargs="+", required=True,
                   help="Which keys to extract, e.g. 0.png 1.png cls metadata.txt")
    p.add_argument("--output", required=True,
                   help="Output .bin filename")
    p.add_argument("--shuffle", type=int, default=20000,
                   help="WebDataset shuffle buffer (0 to disable)")
    p.add_argument("--shardshuffle", type=int, default=100,
                   help="WebDataset shard-shuffle buffer (parsed but not applied)")
    p.add_argument("--handler_overrides", nargs="*", default=[],
                   help="Pairs of ext type to override default handlers, e.g. cls stoi")

    args = p.parse_args()

    if len(args.handler_overrides) % 2 != 0:
        p.error("handler_overrides must be even-length: ext type [ext type ...]")

    overrides = {
        args.handler_overrides[i]: args.handler_overrides[i+1]
        for i in range(0, len(args.handler_overrides), 2)
    }

    # right after args = p.parse_args() and building `overrides`:
    valid_shards = [p for p in args.dataset if os.path.getsize(p) > 0]
    if not valid_shards:
        raise RuntimeError("No non-empty tar shards to convert.")
    # replace args.dataset with valid_shards:
    
    convertWebdataset(
        valid_shards,
        args.entries,
        args.output,
        args.shuffle,
        args.shardshuffle,
        overrides
    )
