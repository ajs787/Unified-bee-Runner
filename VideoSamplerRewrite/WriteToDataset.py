#! /usr/bin/python3

"""
Convert a webdataset to a flat binary file for more efficient dataloading.
"""

import argparse
import functools
import numpy
import struct
# This is only required to convert the webdataset into a torch dataloader
# because the dataloaderToFlatbin function assumes that there is a batch
# dimension. If there is a reason to run this without torch, it is possible to
# make it happen.
import torch
import webdataset as wds

from flatbin_dataset import dataloaderToFlatbin, getPatchHeaderNames, getPatchDatatypes

def getImageInfo(dataset):
    image_info = getPatchHeaderNames()
    dataset = (
        wds.WebDataset(dataset)
        .to_tuple(*image_info))
    row = next(iter(dataset))

    # Use the data from the first entry to extract the patch information
    patch_info = {}
    patch_datatypes = getPatchDatatypes()
    for idx, datum in enumerate(row):
        # image_scale is a float, the rest are ints
        if patch_datatypes[idx] == float:
            patch_info[image_info[idx]] = float(datum)
        else:
            patch_info[image_info[idx]] = int(datum)
    return patch_info


def convertWebdataset(args_dataset, entries, output, shuffle = 20000, shardshuffle = 100, overrides = {}):
    # We want to save any image data in the header of the flatbin file so that the data is later
    # recreatable. Decode that special data by just fetching a single entry in a dataset.

    # Webdatasets have default decoders for some datatypes, but not all.
    # We actually just want to do nothing with the data so that we can write it
    # directly into the flatbin file.
    def binary_image_decoder(data):
        assert isinstance(data, bytes)
        # Just return the bytes
        return data

    def numpy_decoder(data):
        assert isinstance(data, bytes)
        # Just return the bytes, this is already neatly packed with its own header.
        return data

    def do_nothing(key, data):
        """Just do nothing with the input data, leaving it as a binary string."""
        return data


    # Decode images as raw bytes
    if shuffle > 0:
        dataset = (
            wds.WebDataset(args_dataset, shardshuffle=shardshuffle)
            # TODO This isn't the right way to shuffle. Making shuffling and merging flatbins a separate
            # program.
            .shuffle(shuffle, initial=shuffle)
            .decode(
                do_nothing
                #wds.handle_extension("cls", do_nothing),
                #wds.handle_extension("png", binary_image_decoder),
                #wds.handle_extension("numpy", numpy_decoder)
            )
        ).to_tuple(*entries)
    else:
        dataset = (
            wds.WebDataset(args_dataset)
            .decode(
                wds.handle_extension("cls", do_nothing),
                wds.handle_extension("png", binary_image_decoder),
                wds.handle_extension("numpy", numpy_decoder)
            )
        ).to_tuple(*entries)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=False, drop_last=False)

    # TODO Should we check the webdataset for metadata and store them? Or leave it to the user?
    # Store the patch information in the metadata
    # patch_info = getImageInfo(args_dataset)
    patch_info = {}

    dataloaderToFlatbin(dataloader, entries, output, patch_info, overrides)
    print("Binary file complete.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'dataset',
        type=str,
        help='Path for the WebDataset archive.')
    parser.add_argument(
        '--entries',
        type=str,
        nargs='+',
        required=False,
        default=['1.png'],
        help='Which files to decode from the webdataset.')
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        default=None,
        help='Name of the output file (e.g. data.bin).')
    parser.add_argument(
        '--shuffle',
        type=int,
        required=False,
        default=20000,
        help='Shuffle argument to the webdataset. Try (20000//frames per sample). 0 disables all shuffling.')
    parser.add_argument(
        '--shardshuffle',
        type=int,
        required=False,
        default=100,
        help='Shardshuffle argument to the webdataset. Try the number of shards.')
    parser.add_argument(
        '--handler_overrides',
        type=str,
        nargs='+',
        required=False,
        default=[],
        help='Overrides for default handlers, e.g. "--handler_override cls txt" if cls files should be treated as txt instead of binary numbers.')

    args = parser.parse_args()

    if 0 != len(args.handler_overrides)%2:
        print("Overrides must be provided in pairs of <file extension>, <type>.")
    assert(len(args.handler_overrides) % 2 == 0)
    overrides = {}
    for over_idx in range(0, len(args.handler_overrides), 2):
        overrides[args.handler_overrides[over_idx]] = args.handler_overrides[over_idx+1]

    convertWebdataset(args.dataset, args.entries, args.output, args.shuffle, args.shardshuffle, overrides)

webdataset_to_flatbin (mine):
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

def convertWebdataset(dataset, entries, output, shuffle, shardshuffle, overrides):
    """
    dataset    : list of .tar filenames
    entries    : list of keys, e.g. ['0.png','1.png',…,'cls','metadata.txt']
    output     : path for output .bin
    shuffle    : int shuffle buffer (WebDataset)
    shardshuffle: int shard-shuffle buffer
    overrides  : ext->handler overrides for WebDataset
    """
    # 1) figure out numeric metadata header
    patch_info = {}

    # 2) build the WebDataset loader with short keys
    loader = (
        wds.WebDataset(dataset)
           .shuffle(shuffle, initial=shuffle)
           .decode("torchrgb")
           .map(strip_prefix)
           .to_tuple(*entries)
    )

    # 3) write out the flat bin
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