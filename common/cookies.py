from aiohttp import CookieJar
from yarl import URL
import rookiepy

def load_edge_cookies() -> CookieJar:
    """
    Load Edge cookies via rookiepy and return an aiohttp.CookieJar.
    """
    jar = CookieJar()
    for c in rookiepy.edge():
        jar.update_cookies(
            {c['name']: c['value']},
            response_url=URL.build(scheme='https', host=c['domain'].lstrip('.'))
        )
    return jar
