from utils import get
from config import WOLFRAM_APP_ID
import urllib.parse


async def WolframSearch(query):
    query = urllib.parse.quote_plus(query)
    query_url = f"http://api.wolframalpha.com/v2/result?" \
                f"appid={WOLFRAM_APP_ID}" \
                f"&input={query}" \
                f"&format=plaintext" \

    result = await get(query_url)
    if result.status_code != 200:
        return 'Could not retrieve information from Wolfram|Alpha.'
    return result.text
