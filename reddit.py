from utils import get

async def get_image(link):
    # add json to the link
    link = 'https:/' + '/'.join(link.split('/')[1:8]) + '.json'

    # now do get request and slurp

    json = await get(link)
    json = json.json()
    if json[0]['data']['children'][0]['data']['post_hint'] == 'image':
        return json[0]['data']['children'][0]['data']['url']

    return None

