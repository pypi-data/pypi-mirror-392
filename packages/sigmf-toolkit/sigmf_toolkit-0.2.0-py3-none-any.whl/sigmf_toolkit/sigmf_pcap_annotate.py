import argparse
import datetime

# This import is needed for PcapReader to parse packets correctly
import scapy.all  # noqa: F401
from scapy.utils import PcapReader, hexdump
from scapy.packet import Raw
import sigmf
from sigmf.sigmffile import SigMFFile


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pcap-file", required=True, help="PCAP file")
    parser.add_argument("--sigmf-file", required=True, help="SigMF file to annotate")
    parser.add_argument("--bps", type=float, help="Bits per second over the air")
    parser.add_argument(
        "--pcap-overhead",
        default=0,
        type=int,
        help=("Overhead not transmitted over the air (bytes) [default=%(default)r]"),
    )
    parser.add_argument(
        "--air-overhead",
        default=0,
        type=int,
        help=(
            "Overhead transmitted over the air (for instance FEC) bits"
            "[default=%(default)r]"
        ),
    )
    parser.add_argument("--frequency", type=float, help="RF frequency for annotations")
    parser.add_argument("--bandwidth", type=float, help="Bandwidth for annotations")
    return parser.parse_args()


def main():
    args = parse_args()

    sigmf_file = sigmf.sigmffile.fromfile(args.sigmf_file)
    t0 = sigmf_file.get_capture_info(0)[SigMFFile.DATETIME_KEY]
    samp_rate = sigmf_file.get_global_field(SigMFFile.SAMPLE_RATE_KEY)
    t0_int = datetime.datetime.fromisoformat(f"{t0.split('.')[0]}Z")
    t0_frac = float(f"0.{t0.split('.')[1].rstrip('Z')}")

    # remove annotations added by this generator
    generator = "sigmf_pcap_annotate"
    annotations = [
        a
        for a in sigmf_file.get_annotations()
        if a[SigMFFile.GENERATOR_KEY] != generator
    ]
    sigmf_file._metadata[SigMFFile.ANNOTATION_KEY] = annotations

    for j, packet in enumerate(PcapReader(args.pcap_file)):
        num_bits = 8 * max(len(packet) - args.pcap_overhead, 0) + args.air_overhead
        air_time = num_bits / args.bps if args.bps is not None else 0
        t_int = datetime.datetime.fromtimestamp(int(packet.time), tz=datetime.UTC)
        t_frac = float(packet.time - int(packet.time))
        delta_t = (t_int - t0_int).total_seconds() + t_frac - t0_frac
        offset = round(delta_t * samp_rate)
        length = round(air_time * samp_rate)
        comment = (
            hexdump(packet, dump=True)
            if isinstance(packet, Raw)
            else packet.show(dump=True)
        )
        metadata = {
            SigMFFile.GENERATOR_KEY: generator,
            SigMFFile.LABEL_KEY: f"{j + 1}",
            SigMFFile.COMMENT_KEY: comment,
        }
        if args.frequency is not None and args.bandwidth is not None:
            metadata[SigMFFile.FLO_KEY] = args.frequency - 0.5 * args.bandwidth
            metadata[SigMFFile.FHI_KEY] = args.frequency + 0.5 * args.bandwidth
        sigmf_file.add_annotation(offset, length, metadata)

    # save generated annotations
    sigmf_file.tofile(args.sigmf_file)
