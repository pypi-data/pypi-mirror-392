import os
import argparse
from typing import List
from importlib.metadata import version

from treerequests import args_section

__version__ = version(__package__ or __name__)


def valid_directory(directory: str) -> str:
    if not os.path.isdir(directory):
        raise argparse.ArgumentTypeError(
            'couldn\'t change directory to "{}"'.format(directory)
        )
    return directory


def valid_resource(res: str) -> str:
    res = res.lower()
    if res in ["institutions", "datasets", "resources"]:
        return res

    def err():
        raise argparse.ArgumentTypeError('incorrect resource type "{}"'.format(res))

    left, dot, right = res.partition(".")
    if len(dot) == 0 or len(right) == 0:
        err()
    if left not in ["institution", "dataset", "resource"]:
        err()
    if not right.isdigit():
        err()
    return res


def valid_format(format: str) -> List[str] | None:
    format = format.lower()
    if format == "":
        return None

    format = format.split(",")
    if "all" in format:
        return []
    for i in format:
        if i not in ["csv", "jsonld", "xlsx"]:
            raise argparse.ArgumentTypeError('incorrect format type "{}"'.format(i))
    return format


def argparser():
    parser = argparse.ArgumentParser(
        description="Tool for getting data from dane.gov.pl",
        add_help=False,
    )

    parser.add_argument(
        "resources",
        metavar="RESOURCE",
        type=valid_resource,
        nargs="*",
        help="starting point for getting resources i.e. institutions, institution.{ID}, datasets, dataset.{ID}, resources, resource.{ID}",
    )

    general = parser.add_argument_group("General")
    general.add_argument(
        "-h",
        "--help",
        action="help",
        help="Show this help message and exit",
    )
    general.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
        help="Print program version and exit",
    )

    files = parser.add_argument_group("Files")
    files.add_argument(
        "-d",
        "--directory",
        metavar="DIR",
        type=valid_directory,
        default=".",
        help="Change directory to DIR",
    )

    settings = parser.add_argument_group("Settings")
    settings.add_argument(
        "-t",
        "--threads",
        metavar="NUM",
        type=int,
        help="use NUM of threads",
        default=1,
    )
    settings.add_argument(
        "-l",
        "--lvl",
        type=int,
        default=-1,
        help="Get resources metadata up to level",
    )
    settings.add_argument(
        "-f",
        "--format",
        type=valid_format,
        default="",
        help="Download files in specified format preference i.e. all; jsonld; csv; xlsx, csv,jsonld,xls (if not set, files are not downloaded)",
    )
    settings.add_argument(
        "-c",
        "--compress",
        type=valid_format,
        default="",
        help="Compress csv and jsonld files with zstd",
    )

    args_section(parser)

    return parser
