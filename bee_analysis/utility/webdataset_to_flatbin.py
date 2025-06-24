#!/usr/bin/env python3
"""
Convert one or more WebDataset .tar files into flat .bin files.
This script strips the long "<key>.0.png" names down to "0.png", "1.png", ...
then packages them via dataloaderToFlatbin().
"""

import argparse
import webdataset as wds
import torch
import numpy as np
import struct
from flatbin_dataset import (
    dataloaderToFlatbin,
    getPatchHeaderNames,
    getPatchDatatypes
)

def strip_prefix(sample):
    """
    Rewrite keys of the form "<key>.<suffix>" into just "<suffix>" by dropping
    exactly the "<key>." prefix.  Preserve all "__key__", "__url__", "__local_path__".
    Also strip any leading dot on the left-over names.
    """
    out = {}
    # copy metadata fields untouched
    for meta in ("__key__", "__url__", "__local_path__"):
        if meta in sample:
            out[meta] = sample[meta]

    # our prefix to drop
    key = sample["__key__"]
    if isinstance(key, bytes):
        key = key.decode("utf-8")
    prefix = key + "."

    # rewrite all the other entries
    for full_name, data in sample.items():
        if full_name in out:
            continue

        if full_name.startswith(prefix):
            # drop exactly "<key>."
            suffix = full_name[len(prefix):]
        else:
            # drop any leading dot(s)
            suffix = full_name.lstrip(".")

        out[suffix] = data

    return out



def getImageInfo(tar_list):
    """
    Read one sample from the WebDataset(s) to infer numeric metadata shapes.
    Returns a dict mapping each numeric field name -> its (int or float) example.
    """
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

import torch
import webdataset as wds
from flatbin_dataset import dataloaderToFlatbin

def convertWebdataset(dataset, entries, output, shuffle, shardshuffle, overrides):
    """
    ... (docstring) ...
    """
    patch_info = {}

    # (2) build the raw WebDataset pipeline.
    # *** CHANGE HERE: REMOVE .decode("torchrgb") ***
    # Let the data remain as raw bytes.
    ds = (
        wds.WebDataset(dataset, shardshuffle=shardshuffle)
           .shuffle(shuffle, initial=shuffle)
           .map(strip_prefix)
           .to_tuple(*entries)
    )

    # (3) wrap in a DataLoader
    # The default collate_fn will handle gathering the bytes correctly.
    loader = torch.utils.data.DataLoader(
        ds,
        batch_size=1, # Keep batch size of 1
        shuffle=False,
        drop_last=False,
        num_workers=0
    )

    # (4) now write out the flat binary.
    # dataloaderToFlatbin will now receive raw image bytes for the '.png' entries
    # and its internal writeImgData function will handle them.
    dataloaderToFlatbin(loader, entries, output, patch_info, overrides)


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Convert WebDataset .tar→flat .bin with zero-prefixed keys"
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
                   help="WebDataset shard-shuffle buffer")
    p.add_argument("--handler_overrides", nargs="*", default=[],
                   help="Pairs of ext type to override default handlers")
    args = p.parse_args()

    # handler_overrides must come in pairs
    if len(args.handler_overrides) % 2 != 0:
        p.error("handler_overrides must be even-length: ext type [ext type ...]")
    overrides = {
        args.handler_overrides[i]: args.handler_overrides[i+1]
        for i in range(0, len(args.handler_overrides), 2)
    }

    convertWebdataset(
        args.dataset,
        args.entries,
        args.output,
        args.shuffle,
        args.shardshuffle,
        overrides
    )