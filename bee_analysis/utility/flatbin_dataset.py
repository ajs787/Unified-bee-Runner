#! /usr/bin/python3

"""
Dataset that loads flatbinary files.
"""

import io
import functools
import numpy
import os
import random
import struct
import torch

from PIL import Image

def getPatchHeaderNames():
    """A convenience function that other utilities can use to keep code married."""
    return ['image_scale', 'original_width', 'original_height',
            'crop_x_offset', 'crop_y_offset', 'patch_width', 'patch_height',
            'camera_roll', 'camera_pitch', 'camera_yaw',
            'camera_x_offset', 'camera_y_offset', 'camera_z_offset',
            'camera_focal_length', 'camera_pixel_size', 'camera_sensor_pixels_h', 'camera_sensor_pixels_v']

def getPatchDatatypes():
    """A convenience function with the data types of the patch header."""
    return [float, int, int,
            int, int, int, int,
            float, float, float,
            float, float, float,
            float, float, int, int]

################################################
# The read and write handling functions.
# These are used when decoding or writing a flat binary file.

def img_handler(binfile, img_format=None):
    img_len = int.from_bytes(binfile.read(4), byteorder='big')
    bin_data = binfile.read(img_len)
    with io.BytesIO(bin_data) as img_stream:
        img = Image.open(img_stream)
        img.load()
        # Decode the image according to the requested format or return the format as written
        # NOTE Only handling RGB and grayscale (L) images currently.
        if (img_format is None and img.mode == "RGB") or img_format == "RGB":
            img_data = numpy.array(img.convert("RGB")).astype(numpy.float32) / 255.0
        elif (img_format is None and img.mode == "L") or img_format == "L":
            img_data = numpy.array(img.convert("L")).astype(numpy.float32) / 255.0
        else:
            if img_format is None:
                raise RuntimeError("Unhandled image format: {}".format(img.mode))
            else:
                raise RuntimeError("Unhandled image format: {}".format(img_format))
    # The image is in height x width x channels, which we don't want.
    # We also always want to return data with a channel, even with grayscale images
    if 3 == img_data.ndim:
        return img_data.transpose((2, 0, 1))
    elif 2 == img_data.ndim:
        return numpy.expand_dims(img_data, 0)
    else:
        # If there is only a single channel then numpy drops the dimension.
        return img_data

# Raw bytes of a compressed png image
def writeImgData(binfile, data):
    # Write the size and the image bytes
    # The data could already be a PIL image bytes, or it could be a tensor that we must converted to a PIL Image and then saved as a png.
    if not isinstance(data, bytes):
        # We need to get to a numpy array, so check if this is a tensor
        if isinstance(data, torch.Tensor):
            # Only supporting gray and RGB images
            if data.ndim == 3 and data.size(0) == 1:
                # Remove the channel dimension for grayscale images
                np_data = data[0].numpy()
                mode="L"
            elif data.ndim == 3:
                # Permute the CxHxW data of RGB images to HxWxC
                np_data = data.permute((1, 2, 0)).numpy()
                mode="RGB"
            else: # Fallback for other tensor shapes
                np_data = data.numpy()
                mode = None # Let PIL infer mode
            # Rescale if float tensor is in 0-1 range
            if np_data.dtype == numpy.float32 or np_data.dtype == numpy.float64:
                np_data = (np_data * 255).astype(numpy.uint8)

            data_img = Image.fromarray(np_data, mode=mode)
        else: # Assumes it's a numpy array
            data_img = Image.fromarray(data)

        buf = io.BytesIO()
        data_img.save(fp=buf, format="png")
        data = buf.getvalue()
    binfile.write(len(data).to_bytes(length=4, byteorder='big', signed=False))
    binfile.write(data)

def numpy_handler(binfile):
    """Handle a numpy array with a variable per sample length."""
    data_len = int.from_bytes(binfile.read(4), byteorder='big')
    bin_data = binfile.read(data_len)
    with io.BytesIO(bin_data) as data_stream:
        return numpy.lib.format.read_array(data_stream, allow_pickle=False)

# Raw bytes of a numpy array (such as from undecoded data from a webdataset)
def writeNumpyWithHeader(binfile, data):
    # Write the size and the data bytes
    if not isinstance(data, bytes):
        # Convert the numpy array to bytes if necessary
        data = data.tobytes()
    binfile.write(len(data).to_bytes(length=4, byteorder='big', signed=False))
    binfile.write(data)

def array_handler_type(typechar, nmemb, binfile):
    """Handle an array of nmemb elements the type represented by typechar from binfile."""
    match typechar:
        case 'f' | 'i':
            size = 4
        case 'c':
            size = 1
        case _:
            raise ValueError(f"Unsupported typechar: {typechar}")
    # Don't return single values as arrays
    if nmemb > 1:
        return struct.unpack(f'>{nmemb}{typechar}', binfile.read(size*nmemb))
    else:
        return struct.unpack(f'>{nmemb}{typechar}', binfile.read(size*nmemb))[0]

def array_handler_int(nmemb, binfile):
    """Handle an array of nmemb 32 bit ints from binfile."""
    return array_handler_type('i', nmemb, binfile)

def array_handler_float(data_length, binfile):
    """Handle an array of nmemb 32 bit floats from binfile."""
    return array_handler_type('f', data_length, binfile)

def writePrimitiveData(typechar, binfile, data):
    """Write the given primitive value or list into binfile packed with big endian."""
    if isinstance(data, list):
        binfile.write(struct.pack(f">{len(data)}{typechar}", *data))
    else:
        binfile.write(struct.pack(f">{typechar}", data))

def writeFloatData(binfile, data):
    # Pack with big endian float
    writePrimitiveData('f', binfile, data)

def writeIntData(binfile, data):
    # Pack with big endian int
    writePrimitiveData('i', binfile, data)

def writeStoIData(binfile, data):
    # handle both bytes and ints
    if isinstance(data, (bytes, bytearray)):
        value = int(data.decode("utf-8"))
    else:
        value = int(data)
    # This is a single integer, so it should be packed as such
    binfile.write(struct.pack('>i', value))

def convertThenWriteIntData(binfile, data):
    # Convert with frombytes, then write as big endian int.
    # *** BUG FIX 1: Added byteorder='big' ***
    writeIntData(binfile, int.from_bytes(data, byteorder='big'))

def writeBinaryData(binfile, data):
    # Binary data that goes directly to disk
    binfile.write(data)

def tensor_handler(data_length, binfile):
    """Handle a fixed-length tensor."""
    return numpy.frombuffer(binfile.read(data_length*4), dtype=numpy.float32)

def skip_image(binfile):
    """Skip the data section of an image or other variable-length block."""
    try:
        data_len = int.from_bytes(binfile.read(4), byteorder='big')
        binfile.seek(data_len, os.SEEK_CUR)
    except (struct.error, IOError):
        # Handle case where we might be at the end of the file
        pass

def skip_tensor(data_length, binfile):
    """Skip a section of a fixed-size block of data."""
    try:
        binfile.seek(data_length*4, os.SEEK_CUR)
    except (struct.error, IOError):
        # Handle case where we might be at the end of the file
        pass

################################################
# The header reading and writing functions.

def write_header(binfile, metadata):
    """Write the metadata into the binfile."""
    # Create an in-memory buffer to build the header first
    header_buf = io.BytesIO()
    for name, value in metadata.items():
        name_bytes = name.encode('utf-8')
        header_buf.write(len(name_bytes).to_bytes(length=4, byteorder='big', signed=False))
        header_buf.write(name_bytes)
        if isinstance(value, float):
            header_buf.write(struct.pack(">?", True))
            # *** BUG FIX 2: Was 'info', now 'value' ***
            header_buf.write(struct.pack(">f", value))
        else:
            header_buf.write(struct.pack(">?", False))
            header_buf.write(struct.pack(">i", value))

    # Get the complete header content
    header_content = header_buf.getvalue()
    # Write the total length of the header section, then the header itself
    binfile.write(len(header_content).to_bytes(length=4, byteorder='big', signed=False))
    binfile.write(header_content)

def read_header(binfile):
    """Read a header, as written by the write_header function."""
    try:
        bytes_left = int.from_bytes(binfile.read(4), byteorder='big')
    except (struct.error, IOError):
        return {} # Return empty metadata if file is too short
    
    metadata = {}
    header_start = binfile.tell()
    # Protect against reading past the end of the file or a corrupted header
    while binfile.tell() < header_start + bytes_left:
        try:
            name_len = int.from_bytes(binfile.read(4), byteorder='big')
            if name_len > 1024: # Sanity check
                break
            name = binfile.read(name_len).decode('utf-8')
            is_float = struct.unpack('>?', binfile.read(1))[0]
            if is_float:
                value = struct.unpack('>f', binfile.read(4))[0]
            else:
                value = struct.unpack('>i', binfile.read(4))[0]
            metadata[name] = value
        except (struct.error, IOError):
            break # Stop reading if file ends unexpectedly
    return metadata

def dataloaderToFlatbin(dataloader, entries, output, metadata={}, handlers={}):
    """
    Arguments:
        dataloader: An iterable dataloader
        entries ([str]): Names (and implied types) of the data from the dataloader. Required.
        output (str): Name of the output flatbin file.
        metadata ({str:(float|int)}): Metadata information about the dataset.
        handlers ({str:str}): Handle a filetype, e.g. {'cls': 'int'}
    """
    if not entries:
        raise ValueError("'entries' list cannot be empty.")

    binfile = open(output, "wb")
    # Leave a placeholder for the sample count and number of entries
    binfile.write((0).to_bytes(length=4, byteorder='big', signed=False))
    binfile.write(len(entries).to_bytes(length=4, byteorder='big', signed=False))

    # --- Write the data format section of the header ---
    datawriters = []
    for name in entries:
        # Write name
        name_bytes = name.encode('utf-8')
        binfile.write(len(name_bytes).to_bytes(length=4, byteorder='big', signed=False))
        binfile.write(name_bytes)

        # Determine the correct writer function
        handle_str = handlers.get(name.split('.')[-1])

        is_variable_size = False
        if name.endswith(".png") or handle_str == "png":
            datawriters.append(functools.partial(writeImgData, binfile))
            is_variable_size = True
        elif name.endswith(".numpy") or handle_str == "numpy":
            datawriters.append(functools.partial(writeNumpyWithHeader, binfile))
            is_variable_size = True
        elif name.endswith(".int") or handle_str == "int":
            datawriters.append(functools.partial(writeIntData, binfile))
            binfile.write((1).to_bytes(length=4, byteorder='big', signed=False)) # Size = 1 element
        elif name.endswith(".float") or handle_str == "float":
            datawriters.append(functools.partial(writeFloatData, binfile))
            binfile.write((1).to_bytes(length=4, byteorder='big', signed=False)) # Size = 1 element
        elif handle_str == "stoi":
            datawriters.append(functools.partial(writeStoIData, binfile))
            binfile.write((1).to_bytes(length=4, byteorder='big', signed=False)) # Size = 1 element
        else:
            raise ValueError(f"Unsupported entry type for '{name}'. Please specify a handler.")
        
        if is_variable_size:
            # For variable size data, write 0 as size placeholder. Not strictly needed for reading
            # but good for consistency.
            binfile.write((0).to_bytes(length=4, byteorder='big', signed=False))
    
    write_header(binfile, metadata)

    # --- Write the data samples ---
    sample_count = 0
    for batch in dataloader:
        # Determine batch size. Assumes all items in batch are lists or tensors of same length.
        if isinstance(batch[0], (torch.Tensor, list, tuple)):
            batch_size = len(batch[0])
        else: # Should not happen with a standard DataLoader
             batch_size = 1
             batch = [[item] for item in batch] # Wrap items to make it iterable

        # Unzip the batch into per-sample lists
        for i in range(batch_size):
            sample = [item[i] for item in batch]
            sample_count += 1

            # Write the actual sample data using the prepared writers
            for idx, datum in enumerate(sample):
                datawriters[idx](datum)

    # Go back to the beginning to write the final sample count
    binfile.seek(0)
    binfile.write(sample_count.to_bytes(length=4, byteorder='big', signed=False))
    binfile.close()
    print(f"Wrote {sample_count} samples to {output}")
    
class InterleavedFlatbinDatasets(torch.utils.data.IterableDataset):
    def __init__(self, binpath, desired_data, img_format=None):
        if not isinstance(binpath, list):
            binpath = [binpath]
        self.datasets = [FlatbinDataset(path, desired_data, img_format) for path in binpath]
        
        # Create a read order for the different datasets, interleaving them
        if not self.datasets or all(len(ds) == 0 for ds in self.datasets):
            self.interleave_order = []
            return

        # Filter out empty datasets before calculating sizes
        valid_datasets = [ds for ds in self.datasets if len(ds) > 0]
        if not valid_datasets:
            self.interleave_order = []
            return

        least_dataset_size = min(len(ds) for ds in valid_datasets)
        # Heuristic to avoid overdoing the interleave order
        interleave_block_size = max(100, least_dataset_size)

        self.interleave_order = []
        for d_idx, dataset in enumerate(self.datasets):
            if len(dataset) > 0:
                # Calculate how many blocks of size 'interleave_block_size' this dataset contributes
                num_blocks = max(1, len(dataset) // interleave_block_size)
                self.interleave_order.extend([d_idx] * num_blocks)
        
        # If the number of items is too small we lose out on some randomness. Enforce a minimum size.
        if self.interleave_order and 10 > len(self.interleave_order):
            self.interleave_order = self.interleave_order * (10 // len(self.interleave_order) + 1)

        random.shuffle(self.interleave_order)

    def getPatchInfo(self):
        return self.datasets[0].patch_info if self.datasets else None

    def getDataSize(self, out_index):
        """Get the size of the data at the given index. Does not work for images."""
        if not self.datasets: return None
        try:
            in_index = self.datasets[0].data_indices.index(out_index)
            return self.datasets[0].data_sizes[in_index]
        except (ValueError, IndexError):
            return None

    def __len__(self):
        return sum(len(dataset) for dataset in self.datasets)

    def __iter__(self):
        if not self.interleave_order: return
        
        iters = [iter(ds) for ds in self.datasets]
        finished = [False] * len(self.datasets)
        
        while not all(finished):
            interleave_cycle_finished = True
            for source_idx in self.interleave_order:
                if not finished[source_idx]:
                    try:
                        yield next(iters[source_idx])
                        interleave_cycle_finished = False
                    except StopIteration:
                        finished[source_idx] = True
            
            # If an entire pass through the interleave order yielded nothing, we are done
            if interleave_cycle_finished:
                break


class FlatbinDataset(torch.utils.data.IterableDataset):
    def __init__(self, binpath, desired_data, img_format=None):
        if isinstance(binpath, list):
            # If a list is provided, just use the first one.
            self.binpath = binpath[0]
        else:
            self.binpath = binpath
        self.img_format = img_format
        
        with open(self.binpath, "rb") as binfile:
            # Read total samples, and if zero, initialize as an empty dataset
            try:
                self.total_samples = int.from_bytes(binfile.read(4), byteorder='big')
            except (IOError, struct.error):
                self.total_samples = 0
            
            if self.total_samples == 0:
                self.entries_per_sample = 0
                self.header_names, self.data_handlers, self.data_indices, self.data_sizes = [], [], [], []
                self.skip_fns, self.patch_info, self.data_offset = [], {}, 0
                return

            self.entries_per_sample = int.from_bytes(binfile.read(4), byteorder='big')
            self.desired_data = desired_data
            self.header_names, self.data_handlers, self.data_indices, self.data_sizes = [], [], [], []
            
            # Read the data format section of the header
            for _ in range(self.entries_per_sample):
                name_len = int.from_bytes(binfile.read(4), byteorder='big')
                assert name_len <= 1024, "Header name length seems unreasonably large."
                name = binfile.read(name_len).decode('utf-8')
                self.header_names.append(name)

                # All non-image/numpy types have a fixed data length written in the header
                is_variable_size = name.endswith((".png", ".numpy"))
                data_length = int.from_bytes(binfile.read(4), byteorder='big') if not is_variable_size else None
                
                if name not in self.desired_data:
                    self.data_indices.append(None)
                    # For data we don't want, the handler IS the skip function
                    if is_variable_size:
                        self.data_handlers.append(skip_image)
                    else:
                        self.data_handlers.append(functools.partial(skip_tensor, data_length))
                else:
                    idx = self.desired_data.index(name)
                    self.data_indices.append(idx)
                    
                    if name.endswith(".png"):
                        self.data_handlers.append(functools.partial(img_handler, img_format=self.img_format))
                    elif name.endswith(".numpy"):
                        self.data_handlers.append(numpy_handler)
                    elif name.endswith(".float"):
                        self.data_handlers.append(functools.partial(array_handler_float, data_length))
                    elif name.endswith(".int") or name.endswith("cls"):
                        self.data_handlers.append(functools.partial(array_handler_int, data_length))
                    else: # Fallback for other fixed-size tensor-like data
                        self.data_handlers.append(functools.partial(tensor_handler, data_length))
                
                self.data_sizes.append(data_length)

            # Build functions to skip an entire sample efficiently
            # This is separate from handlers because a worker might need to skip data that it *would* normally read
            skip_fns_list = []
            for name, size in zip(self.header_names, self.data_sizes):
                 if name.endswith((".png", ".numpy")):
                     skip_fns_list.append(skip_image)
                 else:
                     skip_fns_list.append(functools.partial(skip_tensor, size))
            self.skip_fns = skip_fns_list


            self.patch_info = read_header(binfile)
            self.data_offset = binfile.tell()

    def getPatchInfo(self):
        return self.patch_info

    def getDataSize(self, out_index):
        """Get the size of the data at the given index. Does not work for images."""
        try:
            in_index = self.data_indices.index(out_index)
            return self.data_sizes[in_index]
        except (ValueError, IndexError):
            return None

    def __len__(self):
        return self.total_samples

    def __iter__(self):
        if self.total_samples == 0:
            return
        with open(self.binpath, "rb") as binfile:
            binfile.seek(self.data_offset, os.SEEK_SET)
            worker_info = torch.utils.data.get_worker_info()
            # Determine interval and offset for multi-worker loading
            if worker_info and worker_info.num_workers > 1:
                read_interval = worker_info.num_workers
                read_offset = worker_info.id
            else:
                read_interval = 1
                read_offset = 0
            # *** LOGIC FIX 3: Combined into a single if/else structure for worker logic ***
            for i in range(self.total_samples):
                current_offset = i % read_interval
                # This sample is for this worker to READ
                if current_offset == read_offset:
                    # Pre-allocate list with None
                    return_data = [None] * len(self.desired_data)
                    for handler_idx, handler in enumerate(self.data_handlers):
                        # The index in the output list where data should be placed
                        output_idx = self.data_indices[handler_idx] 
                        # Read the data if it is desired, otherwise the handler itself is a skip function
                        data_or_none = handler(binfile)
                        if output_idx is not None:
                            # Place the read data in the correct output slot
                            return_data[output_idx] = data_or_none
                    yield return_data
                # This sample is for another worker, so this worker must SKIP
                else:
                    for skip_fn in self.skip_fns:
                        skip_fn(binfile)
                        
#def __next__(self):
    #    if self.completed == self.total_samples:
    #        raise StopIteration

    #    # Trying to prevent python memory overuse in multithreaded dataloading
    #    for idx in range(len(self.return_data)):
    #        if self.return_data[idx] is not None:
    #            old = self.return_data[idx]
    #            self.return_data[idx] = None
    #            del old

    #    for idx, handler in enumerate(self.data_handlers):
    #        if self.data_indices[idx] is not None:
    #            #np_data = handler(self.binfile)
    #            #data[self.data_indices[idx]] = torch.tensor(np_data)
    #            #del np_data
    #            self.return_data[self.data_indices[idx]] = torch.tensor(handler(self.binfile))
    #        else:
    #            # This will be a handler to skip the data
    #            handler(self.binfile)

    #    self.completed += 1
    #    return self.return_data