import logging

import httpx

from animdl import utils

from .exit_codes import INTERNET_ISSUE

http_logger = logging.getLogger("http-client")

client = httpx.Client(
    headers={"user-agent": utils.http_client.get_user_agent()},
    timeout=30,
    follow_redirects=True,
)

utils.http_client.integrate_ddg_bypassing(
    client,
    ".marin.moe",
)

utils.http_client.setup_global_http_exception_hook(
    exit_code=INTERNET_ISSUE,
    http_error_baseclass=httpx.HTTPError,
    logger=http_logger,
)

setattr(client, "cf_request", utils.http_client.cors_proxify)
