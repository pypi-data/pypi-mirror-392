"""Helper script to download all pull requests from bitbucket.
uses environment variable IMAS_DD_BITBUCKET_TOKEN to authenticate
agains the bitbucket server and saves a record of all pull requests
on the DD repository to pull_requests.json
"""

import requests
import ssl
import urllib3
import json
import os


for name in ["IMAS_DD_BITBUCKET_TOKEN", "bamboo_IMAS_DD_BITBUCKET_TOKEN"]:
    if name in os.environ:
        token = os.environ[name]
        break
else:
    raise RuntimeError("Token not found. Missing env var: $IMAS_DD_BITBUCKET_TOKEN.")


# https://stackoverflow.com/questions/71603314/ssl-error-unsafe-legacy-renegotiation-disabled
class CustomHttpAdapter(requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self.ssl_context,
        )


def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount("https://", CustomHttpAdapter(ctx))
    return session


def get_pull_requests(start: int = 0):
    url = "https://git.iter.org/rest/api/latest/projects/IMAS/repos/data-dictionary/pull-requests"

    d = get_legacy_session().get(
        url,
        headers={"Accept": "application/json", "Authorization": f"Bearer {token}"},
        params={"state": "MERGED", "start": start, "limit": 100},
    )

    return d.json()


if __name__ == "__main__":
    start = 0
    prs = []
    while True:
        data = get_pull_requests(start)
        prs.extend(data["values"])
        if data["isLastPage"]:
            break
        start = data["nextPageStart"]

    with open("pull_requests.json", "w") as f:
        json.dump(prs, f)
