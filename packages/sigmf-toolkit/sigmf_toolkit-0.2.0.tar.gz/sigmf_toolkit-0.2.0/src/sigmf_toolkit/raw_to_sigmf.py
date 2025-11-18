import argparse
import pathlib

from sigmf.sigmffile import SigMFFile

from sigmf_toolkit.time import parse_datetime


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--datatype", type=str, required=True, help="SigMF datatype")
    parser.add_argument(
        "--samp-rate", type=float, required=True, help="Sample rate (sps)"
    )
    parser.add_argument("--frequency", type=float, help="RF frequency (Hz)")
    parser.add_argument(
        "--datetime",
        type=parse_datetime,
        help="Datetime (either ISO 8601 or UNIX timestamp)",
    )
    parser.add_argument("--author", type=str, help="Author")
    parser.add_argument("--description", type=str, help="Description")
    parser.add_argument("--hw", type=str, help="Hardware")
    parser.add_argument("--license", type=str, help="License")
    parser.add_argument("--recorder", type=str, help="Recorder")
    parser.add_argument("input_file", type=pathlib.Path, help="Input file")
    return parser.parse_args(args)


def main(args=None):
    args = parse_args(args)

    data_file = args.input_file.with_suffix(".sigmf-data")
    args.input_file.rename(data_file)

    global_info = {
        SigMFFile.DATATYPE_KEY: args.datatype,
        SigMFFile.SAMPLE_RATE_KEY: args.samp_rate,
    }
    if args.author is not None:
        global_info[SigMFFile.AUTHOR_KEY] = args.author
    if args.description is not None:
        global_info[SigMFFile.DESCRIPTION_KEY] = args.description
    if args.hw is not None:
        global_info[SigMFFile.HW_KEY] = args.hw
    if args.license is not None:
        global_info[SigMFFile.LICENSE_KEY] = args.license
    if args.recorder is not None:
        global_info[SigMFFile.RECORDER_KEY] = args.recorder
    meta = SigMFFile(
        data_file=data_file,
        global_info=global_info,
    )
    metadata = {}
    if args.datetime is not None:
        metadata[SigMFFile.DATETIME_KEY] = args.datetime
    if args.frequency is not None:
        metadata[SigMFFile.FREQUENCY_KEY] = args.frequency
    meta.add_capture(0, metadata=metadata)
    meta.tofile(args.input_file)
