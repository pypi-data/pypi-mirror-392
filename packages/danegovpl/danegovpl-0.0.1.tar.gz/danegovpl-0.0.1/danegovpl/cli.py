#!/usr/bin/env python
# by Dominik Stanisław Suchora <hexderm@gmail.com>
# License: GNU GPLv3

import os
import sys
from pathlib import Path
import itertools
from concurrent.futures.thread import ThreadPoolExecutor
import json
from functools import partial
from math import ceil

import treerequests
import zstandard

from .args import argparser
from .exceptions import Error, ArgError, RequestError
from .api import Api, RequestError


def fexists(filename, size=0):
    return os.path.exists(filename) and os.path.getsize(filename) >= size


def run(func, niter, threads=1, batch_size=2000):
    if threads < 2:
        for i in niter:
            func(i)
    else:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            for i in itertools.batched(niter, batch_size):
                for j in executor.map(func, i):
                    pass


def json_load(file):
    with open(file, "r") as f:
        return json.load(f)


def json_dump(data, file):
    with open(file, "w") as f:
        return json.dump(data, f)


def json_get(func, path):
    if fexists(path, 2):
        return json_load(path)
    r = func()
    json_dump(r, path)
    return r


def pageiter_get(func, path, per_page=100):
    page = 1
    maxpages = 1
    while page <= maxpages:
        try:
            r = json_get(
                lambda: next(func(page=page, per_page=per_page)),
                path / "{}.json".format(page),
            )
        except RequestError as e:
            print("Error - " + repr(e))
            continue

        yield r

        if page == 1:
            maxpages = ceil(r["meta"]["count"] / per_page)
        page += 1


def pageiter_ids(func, source_func, path, res_type, threads):
    run(
        func,
        (
            j["id"]
            for i in pageiter_get(source_func, path)
            for j in i["data"]
            if j["type"] == res_type
        ),
        threads=threads,
    )


def download_res_id(func_index, func, source_func, path, i_id, res_type, threads):
    npath = path / str(i_id)
    os.makedirs(npath, exist_ok=True)

    try:
        json_get(lambda: func_index(i_id), npath / "info.json")
    except RequestError as e:
        print("Error - " + repr(e))
        return
    pageiter_ids(
        partial(func, npath), partial(source_func, i_id), npath, res_type, threads
    )


def nop(*args, **kwargs):
    pass


class Dane:
    def __init__(self, dane, path, lvl, format):
        self.dane = dane
        self.path = path
        self.lvl = lvl
        self.format = format

    def lvl_exceeded(self, lvl):
        return self.lvl >= 0 and lvl > self.lvl

    def download_institution(self, path, i_id, threads=1, lvl=1):
        return download_res_id(
            self.dane.institution,
            (
                nop
                if self.lvl_exceeded(lvl)
                else partial(self.download_dataset, lvl=lvl + 1)
            ),
            self.dane.institution_datasets,
            path,
            i_id,
            "dataset",
            threads,
        )

    def download_dataset(self, path, i_id, threads=1, lvl=1):
        return download_res_id(
            self.dane.dataset,
            (
                nop
                if self.lvl_exceeded(lvl)
                else partial(self.download_resource, lvl=lvl + 1)
            ),
            self.dane.dataset_resources,
            path,
            i_id,
            "resource",
            threads,
        )

    def download_file(self, url, filename, size=0, openfunc=open):
        if fexists(filename, size):
            return
        try:
            r = self.dane.ses.get(url, allow_redirects=True, stream=True)
            with openfunc(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=4 * 2**20):
                    f.write(chunk)
        except Exception as e:
            print(str(filename) + " " + repr(e))

    def download_file_compress(self, url, filename, size=0):
        return self.download_file(url, filename, size=size, openfunc=zstandard.open)

    def download_resource(self, path, i_id, threads=1, lvl=1):
        npath = path / str(i_id)
        os.makedirs(npath, exist_ok=True)

        try:
            r = json_get(lambda: self.dane.resource(i_id), npath / "info.json")
        except RequestError as e:
            print("Error - " + repr(e))
            return

        if self.format is None:
            return

        def file_urls():
            for i in r["data"]["attributes"]["files"]:
                if len(i["download_url"]) > 0:
                    yield i["download_url"], i["format"]

        files = {i[1]: i[0] for i in file_urls()}

        def get_file(url, format):
            filepath = npath / ("file." + format)
            if format == "xlsx":
                self.download_file(url, filepath, size=1)
            else:
                self.download_file_compress(url, filepath, size=1)

        if len(self.format) == 0:
            for i in files:
                get_file(files[i], i)
        else:
            for i in self.format:
                if files.get(i) is not None:
                    get_file(files[i], i)

    def download_datasets(self, path, threads=1, lvl=1):
        npath = path / "datasets"
        os.makedirs(npath, exist_ok=True)
        pageiter_ids(
            lambda x: self.download_dataset(npath, x, lvl=lvl + 1),
            self.dane.datasets,
            npath,
            "dataset",
            threads,
        )

    def download_institutions(self, path, threads=1, lvl=1):
        npath = path / "institutions"
        os.makedirs(npath, exist_ok=True)
        pageiter_ids(
            lambda x: self.download_institution(npath, x, lvl=lvl + 1),
            self.dane.institutions,
            npath,
            "institution",
            threads,
        )

    def download_resources(self, path, threads=1, lvl=1):
        npath = path / "resources"
        os.makedirs(npath, exist_ok=True)
        pageiter_ids(
            lambda x: self.download_resource(npath, x, lvl=lvl + 1),
            self.dane.resources,
            npath,
            "resource",
            threads,
        )

    def resource_run(self, res, threads=1):
        resources_map = {
            "institutions": self.download_institutions,
            "datasets": self.download_datasets,
            "resources": self.download_resources,
        }
        if (x := resources_map.get(res)) is not None:
            x(self.path, threads, 1)
            return

        left, dot, right = res.partition(".")

        resources_map2 = {
            "institution": self.download_institution,
            "dataset": self.download_dataset,
            "resource": self.download_resources,
        }

        if (x := resources_map2.get(res)) is not None:
            x(self.path, right, threads, 1)
        else:
            assert False


def cli(argv):
    args = argparser().parse_args(argv)
    path = Path(args.directory)
    threads = args.threads

    dane = Api(logger=treerequests.simple_logger(sys.stdout))

    dd = Dane(dane, path, args.lvl, args.format)

    for i in args.resources:
        dd.resource_run(i, threads)
