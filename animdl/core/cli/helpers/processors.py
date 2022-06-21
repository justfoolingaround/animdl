from ...codebase.providers import get_provider
from .prompts import get_prompt_manager
from .searcher import provider_searcher_mapping


def prompt_user(logger, anime_list_genexp, provider):

    manager = get_prompt_manager()

    return manager(
        logger,
        anime_list_genexp,
        processor=lambda component: (component, provider),
        component_name="search result",
        fallback=({}, None),
        error_message=f"Failed to find anything of that query on {provider!r}. Try searching on other providers.",
        stdout_processor=lambda component: f"{component[0]['name']} / {component[0]['anime_url']}",
    )


def process_query(session, query: str, logger, provider: str, *, auto_index=1):

    match, module, provider_name = get_provider(query, raise_on_failure=False)

    if module:
        return {
            "anime_url": query,
            "name": module.metadata_fetcher(session, query, match).get(
                "titles", [None]
            )[0],
        }, provider_name

    provider_name, *custom_query = query.split(":", 1)

    if provider_name in provider_searcher_mapping:
        provider, query = provider_name, ":".join(custom_query)

    genexp = provider_searcher_mapping[provider](session, query)

    if auto_index is None:
        return prompt_user(logger, genexp, provider)

    expanded = list(genexp)
    return expanded[(auto_index - 1) % len(expanded)], provider
