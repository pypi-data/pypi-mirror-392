#!/usr/bin/env python
# by Dominik Stanisław Suchora <hexderm@gmail.com>
# License: GNU GPLv3

from typing import Iterator
import re
import urllib.parse
from math import ceil

import requests
import treerequests

from .exceptions import Error, ArgError, RequestError


class Api:
    DOMAIN = "https://api.dane.gov.pl"

    def __init__(self, version="1.4", **kwargs):
        if version != "1.4":
            raise ArgError('Unsupported api version - "{}"', format(version))
        self.version = version
        self.ses = treerequests.Session(
            requests,
            requests.Session,
            None,
            requesterror=RequestError,
            **kwargs,
        )
        self.ses.headers.update({"X-API-VERSION": version, "Accept-Language": "en"})

    def call_api_request(self, path, method, params=[], **kwargs):
        query = ""
        if len(params) != 0:
            query = "?" + urllib.parse.urlencode(params)

        url = self.DOMAIN + "/" + self.version + "/" + path + query
        # print(kwargs.get("params"), file=sys.stderr)
        r = self.ses.json(
            url,
            method=method,
            **kwargs,
        )
        return r

    def call_api(self, path, method="get", params=[], **kwargs):
        r = self.call_api_request(path, method, params=params, **kwargs)
        return r

    def go_through_pages(self, path, params=[], page=1, per_page=25, max_per_page=100):
        if per_page > max_per_page:
            raise ArgError(
                'Amount of results returned per page is set too high "{}", where max is "{}"'.format(
                    per_page, max_per_page
                )
            )
        maxpages = page
        while page <= maxpages:
            p = []
            p.extend(params)
            p.append(("page", page))
            p.append(("per_page", per_page))

            r = self.call_api(path, params=p)
            yield r

            if page == 1:
                maxpages = ceil(r["meta"]["count"] / per_page)

            page += 1

    def institutions(self, params=[], page=1, per_page=100) -> Iterator:
        return self.go_through_pages(
            "institutions", params=params, page=page, per_page=per_page
        )

    def institution(self, i_id, params=[]) -> dict:
        return self.call_api("institutions/" + str(i_id), params=params)

    def institution_datasets(self, i_id, params=[], page=1, per_page=100) -> Iterator:
        return self.go_through_pages(
            "institutions/" + str(i_id) + "/datasets",
            params=params,
            page=page,
            per_page=per_page,
        )

    def datasets(self, params=[], page=1, per_page=100) -> Iterator:
        return self.go_through_pages(
            "datasets", params=params, page=page, per_page=per_page
        )

    def dataset(self, i_id, params=[]) -> dict:
        return self.call_api(
            "datasets/" + str(i_id),
            params=params,
        )

    def dataset_resources(self, i_id, params=[], page=1, per_page=100) -> Iterator:
        return self.go_through_pages(
            "datasets/" + str(i_id) + "/resources",
            params=params,
            page=page,
            per_page=per_page,
        )

    def dataset_showcases(self, i_id, params=[], page=1, per_page=100) -> Iterator:
        return self.go_through_pages(
            "datasets/" + str(i_id) + "/showcases",
            params=params,
            page=page,
            per_page=per_page,
        )

    def resources(self, params=[], page=1, per_page=100) -> Iterator:
        return self.go_through_pages(
            "resources", params=params, page=page, per_page=per_page
        )

    def resource(self, i_id, params=[]) -> dict:
        return self.call_api(
            "resources/" + str(i_id),
            params=params,
        )

    def dga_aggregated(self) -> dict:
        return self.call_api("dga-aggregated")

    def resource_data(
        self,
        i_id,
        params=[],
        page=1,
        per_page=100,
    ) -> Iterator:

        return self.go_through_pages(
            "resources/" + str(i_id) + "/data",
            page=page,
            per_page=per_page,
            params=params,
        )

    def resource_data_row(self, i_id, row_id) -> str:
        return self.call_api("resources/" + str(i_id) + "/data/" + str(row_id))

    def search(self, params=[], page=1, per_page=100) -> Iterator:
        return self.go_through_pages(
            "search", params=params, page=page, per_page=per_page
        )

    def showcases(self, params=[], page=1, per_page=100) -> Iterator:
        return self.go_through_pages(
            "showcases", params=params, page=page, per_page=per_page
        )

    def showcase(self, i_id, params=[]) -> dict:
        return self.call_api("showcases/" + str(i_id), params=params)

    def histories(self, params=[], page=1, per_page=100) -> Iterator:
        return self.go_through_pages(
            "histories", params=params, page=page, per_page=per_page
        )

    def history(self, i_id, params=[]) -> dict:
        return self.call_api("histories/" + str(i_id), params=params)
