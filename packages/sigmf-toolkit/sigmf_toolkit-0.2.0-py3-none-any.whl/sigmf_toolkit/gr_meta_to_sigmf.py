import argparse
import datetime
import pathlib

from gnuradio.blocks import parse_file_metadata
import pmt
from sigmf.sigmffile import SigMFFile


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--frequency", type=float, help="RF frequency (Hz)")
    parser.add_argument("input_file", type=pathlib.Path, help="Input file")
    return parser.parse_args(args)


def main(args=None):
    args = parse_args(args)

    header = args.input_file.with_suffix(".hdr")
    with open(header, "rb") as f:
        hdr = f.read(parse_file_metadata.HEADER_LENGTH)
        hdr = pmt.deserialize_str(hdr)
        info = parse_file_metadata.parse_header(hdr)
        if info["extra_len"]:
            extra = pmt.deserialize_str(f.read(info["extra_len"]))
            info = parse_file_metadata.parse_extra_dict(extra, info)

    dt = datetime.datetime.fromtimestamp(info["rx_time_secs"], tz=datetime.UTC)
    dt = dt.strftime("%Y-%m-%dT%H:%M:%S")
    dt = f"{dt}.{str(info['rx_time_fracs']).split('.')[-1]}Z"

    if info["type"] == "float" and info["cplx"]:
        datatype = "cf32_le"
    else:
        raise ValueError("unsupported datatype")

    data_file = args.input_file.with_suffix(".sigmf-data")
    args.input_file.rename(data_file)

    meta = SigMFFile(
        data_file=data_file,
        global_info={
            SigMFFile.DATATYPE_KEY: datatype,
            SigMFFile.SAMPLE_RATE_KEY: info["rx_rate"],
        },
    )
    metadata = {
        SigMFFile.DATETIME_KEY: dt,
    }
    if args.frequency is not None:
        metadata[SigMFFile.FREQUENCY_KEY] = args.frequency
    meta.add_capture(0, metadata=metadata)
    meta.tofile(args.input_file)
