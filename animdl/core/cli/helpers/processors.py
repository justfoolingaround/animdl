from click import prompt

from ...codebase.providers import get_provider
from ...config import DEFAULT_PROVIDER
from .searcher import get_searcher


def prompt_user(logger, anime_list_genexp, provider):
    expansion = [*anime_list_genexp]

    if not expansion:
        return logger.critical(
            "Failed to find anything of that query on {!r}. Try searching on other providers.".format(
                provider
            )
        ) or ({}, None)

    for n, anime in enumerate(expansion, 1):
        logger.info(
            "{0:02d}: {1[name]} \x1b[33m{1[anime_url]}\x1b[39m".format(n, anime)
        )

    if len(expansion) == 1:
        logger.debug(
            "Only a single search result found, automatically resorting to it."
        )
        return expansion[0], provider

    index = (
        prompt(
            "Select by the index (defaults to 1)",
            default=1,
            type=int,
            show_default=False,
        )
        - 1
    )
    if (index + 1) > len(expansion):
        logger.debug(
            "Applying modulus to get a valid index from incorrect index: #%02d -> #%02d"
            % (index + 1, index % len(expansion) + 1)
        )
        index %= len(expansion)

    return expansion[index], provider


def process_query(
    session, query: str, logger, *, provider=DEFAULT_PROVIDER, auto=False, auto_index=1
):

    _, module, provider_name = get_provider(query, raise_on_failure=False)

    if module:
        return {"anime_url": query}, provider_name

    *provider_name, custom_query = query.split(":", 1)

    searcher = get_searcher(":".join(provider_name))

    if not searcher:
        searcher, custom_query = get_searcher(provider), query

    genexp = searcher(session, custom_query)

    if not auto:
        return prompt_user(logger, genexp, searcher.provider)
    return [*genexp][auto_index - 1], searcher.provider
