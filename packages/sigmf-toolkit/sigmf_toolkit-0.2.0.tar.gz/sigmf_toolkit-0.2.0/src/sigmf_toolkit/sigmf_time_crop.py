import argparse
import copy
import pathlib

import numpy as np
import sigmf
from sigmf.sigmffile import SigMFFile, get_sigmf_filenames

from sigmf_toolkit.time import parse_datetime


def parse_args(args):
    parser = argparse.ArgumentParser()
    start = parser.add_mutually_exclusive_group()
    start.add_argument(
        "--start-datetime",
        type=parse_datetime,
        help="Start datetime (either ISO 8601 or UNIX timestamp)",
    )
    start.add_argument(
        "--start-offset",
        type=float,
        help="Start offset (s from file beginning)",
    )
    end = parser.add_mutually_exclusive_group()
    end.add_argument(
        "--end-datetime",
        type=parse_datetime,
        help="End datetime (either ISO 8601 or UNIX timestamp)",
    )
    end.add_argument(
        "--end-offset",
        type=float,
        help="End offset (s from file beginning)",
    )
    parser.add_argument(
        "input_file",
        type=pathlib.Path,
        help="Input SigMF file (either .sigmf-data or .sigmf-meta)",
    )
    parser.add_argument(
        "output_file",
        type=pathlib.Path,
        help="Output SigMF file (either .sigmf-data or .sigmf-meta)",
    )
    return parser.parse_args(args)


def main(args=None):
    args = parse_args(args)

    input_data = sigmf.sigmffile.fromfile(args.input_file)
    samp_rate = input_data.get_global_field(SigMFFile.SAMPLE_RATE_KEY)
    captures = input_data.get_captures()
    if len(captures) != 1:
        raise ValueError("only one capture is supported")
    capture = captures[0]
    assert capture[SigMFFile.START_INDEX_KEY] == 0
    dt = capture[SigMFFile.DATETIME_KEY]
    if dt[-1] == "Z":
        dt = dt[:-1]
    input_start = np.datetime64(dt, "ns")

    if args.start_datetime is not None:
        start_dt = args.start_datetime
        assert start_dt[-1] == "Z"
        start_dt = start_dt[:-1]
        skip_seconds = (np.datetime64(start_dt) - input_start) / np.timedelta64(1, "s")
        first_sample = round(skip_seconds * samp_rate)
    elif args.start_offset is not None:
        first_sample = round(args.start_offset * samp_rate)
    else:
        first_sample = 0

    if args.end_datetime is not None:
        end_dt = args.end_datetime
        assert end_dt[-1] == "Z"
        end_dt = end_dt[:-1]
        skip_seconds = (np.datetime64(end_dt) - input_start) / np.timedelta64(1, "s")
        last_sample = round(skip_seconds * samp_rate)
    elif args.start_offset is not None:
        last_sample = round(args.end_offset * samp_rate)
    else:
        last_sample = None

    in_data_file = get_sigmf_filenames(args.input_file)["data_fn"]
    out_data_file = get_sigmf_filenames(args.output_file)["data_fn"]

    chunk_size = 32 * 2**20  # copy in 32 MiB chunks
    sample_size = input_data.get_sample_size()
    bytes_to_copy = (
        (last_sample - first_sample) * sample_size if last_sample is not None else None
    )
    with open(in_data_file, "rb") as f_in, open(out_data_file, "wb") as f_out:
        f_in.seek(first_sample * sample_size)
        while True:
            if bytes_to_copy is not None and bytes_to_copy == 0:
                break
            buf = f_in.read(chunk_size)
            if len(buf) == 0:
                break
            if bytes_to_copy is not None:
                buf = buf[:bytes_to_copy]
            f_out.write(buf)
            if bytes_to_copy is not None:
                bytes_to_copy -= len(buf)

    global_info = copy.deepcopy(input_data.get_global_info())
    # these are recalculated for the output file
    del global_info[SigMFFile.HASH_KEY]
    del global_info[SigMFFile.VERSION_KEY]
    meta_out = sigmf.SigMFFile(
        data_file=out_data_file,
        global_info=global_info,
    )

    capture_out = copy.deepcopy(capture)
    if first_sample != 0:
        dt = input_start + np.timedelta64(round(first_sample / samp_rate * 1e9), "ns")
        capture_out[SigMFFile.DATETIME_KEY] = f"{dt}Z"
    meta_out.add_capture(0, capture_out)

    for annotation in input_data.get_annotations():
        annotation = copy.deepcopy(annotation)
        start_index = annotation[SigMFFile.START_INDEX_KEY] - first_sample
        if start_index < 0:
            continue
        meta_out.add_annotation(start_index, metadata=annotation)

    meta_out.tofile(args.output_file)
