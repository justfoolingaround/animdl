import shutil
from warnings import warn

from ...config import PLAYERS
from .players import player_mapping


def iter_available_players():
    for player, player_info in PLAYERS.items():

        executable = player_info.get("executable")

        if executable is None or shutil.which(executable) is None:
            continue

        yield player, player_info


def get_player(default_player, user_selected_player=None):

    players = tuple(iter_available_players())

    if not players:
        raise RuntimeError(
            "No players found on the system. "
            "Make sure the player is installed and in PATH or in the current directory or has a configured executable."
        )

    if user_selected_player is None:
        user_selected_player = default_player

    for player, player_info in players:
        if player == user_selected_player:
            return player, player_info

    fallback_player, _ = players[0]

    warn(
        f"Could not find {user_selected_player!r} in the system. "
        f"Falling back to the first available player {fallback_player!r}."
    )

    return fallback_player, _


def handle_player(default_player: str, player_opts: tuple, user_selected_player=None):
    if default_player is None:
        raise RuntimeError("No default player set in the configuration.")

    player, player_info = get_player(default_player, user_selected_player)

    cls = player_mapping[player]

    return cls(
        executable=player_info["executable"],
        args=tuple(player_info.get("opts", ())) + player_opts,
    )
