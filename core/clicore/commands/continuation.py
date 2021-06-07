import click

from ..helpers import sfhandler, to_stdout
from .constants import SESSION_FILE
from .download import animdl_download
from .stream import animdl_stream

def session_prompt(session_list):
    ts = lambda x: to_stdout(x, "animdl-session-search")
    ts("Found %d sessions(s)" % len(session_list))
    for n, anime in enumerate(session_list, 1):
        ts("[#%02d] %s" % (n, sfhandler.describe_session_dict(anime.get('stream_url'))))
    
    index = click.prompt("Select by the index (defaults to 1)", default=1, type=int, show_default=False) - 1
    
    if (index + 1) > len(session_list):
        ts("Applying modulus to get a valid index from incorrect index: #%02d -> #%02d" % (index + 1, index % len(session_list) + 1))
        index %= len(session_list)
    
    return session_list[index]

@click.command(name='continue', help="Continue your downloads or stream from where t'was left.")
@click.option('-n', '--name', help="Name of the session to be continued from.", required=False, default='', show_default=False)
@click.option('-v', is_flag=True, default=False, help="View the sessions that can be continued from.")
@click.pass_context
def animdl_continue(ctx: click.Context, name, v):
    """
    Just continue the stuff from where you left it (so that you won't have to type the same things all over again).
    
    By default, the most recent stream/download will be handed.
    """
    if v:
        sessions = sfhandler.load_sessions(SESSION_FILE)
        for i, session in enumerate(sessions, 1):
            to_stdout("[#%02d] %s" % (i, sfhandler.describe_session_dict(session)), 'animdl-continuation')
        if not sessions:
            to_stdout('No active sessions found in the working directory.', 'animdl-continuation')
        return
    
    if name:
        ses = [*sfhandler.search_identifiers(SESSION_FILE, name)]
        
        if not len(ses):
            return to_stdout("No sessions of that identifier found.", 'animdl-continuation')
        
        session = session_prompt(ses)if len(ses) > 1 else ses.pop()
    else:
        session = sfhandler.get_most_recent_session(SESSION_FILE)
        if not session:
            return to_stdout("No recent session found in the working directory.", 'animdl-continuation')
    
    if session.get('type') == 'stream':
        u, s, i, au, ao, af, ac, am = sfhandler.generate_stream_arguments(session)
        return ctx.invoke(animdl_stream, query=u, start=s, title=i, filler_list=au, offset=ao, filler=af, mixed=ac, canon=am)
    
    if session.get('type') == 'download':
        u, s, e, i, au, ao, af, ac, am = sfhandler.generate_download_arguments(session)
        return ctx.invoke(animdl_download, query=u, start=s, end=e, title=i, filler_list=au, offset=ao, filler=af, mixed=ac, canon=am)