def geobypass_response(session, url):
    session.cookies.update({'session_id': session.get('https://raw.githubusercontent.com/justfoolingaround/animdl-provider-benchmarks/master/api/raw').text})
    return session.get(url)
