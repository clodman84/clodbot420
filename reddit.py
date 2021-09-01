from utils import get

async def get_image(link):
    # add json to the link
    link = 'https:/' + '/'.join(link.split('/')[1:8]) + '.json'

    # now do get request and slurp

    json = await get(link)
    json = json.json()
    if not json[0]['data']['children'][0]['data']['is_video']:
        json = json[0]['data']['children'][0]['data']
        return {'url':json['url'], 'title':json['title'], 'subreddit':json['subreddit_name_prefixed'], 'ratio':json['upvote_ratio']*100, 'upvotes':json['ups'], 'permalink':'https://www.reddit.com'+json['permalink']}

    return None
