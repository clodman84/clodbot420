from utils import get
from html import unescape


async def get_image(link):
    # add json to the link
    link = 'https:/' + '/'.join(link.split('/')[1:8]) + '.json'

    # now do get request and slurp

    json = await get(link)
    json = json.json()
    if not json[0]['data']['children'][0]['data']['is_video']:
        json = json[0]['data']['children'][0]['data']
        if not json['is_gallery']:
            return {'url': json['url'], 'title': json['title'], 'subreddit': json['subreddit_name_prefixed'],
                    'ratio': json['upvote_ratio'] * 100, 'upvotes': json['ups'],
                    'permalink': 'https://www.reddit.com' + json['permalink']}
        else:
            pic = [*json['media_metadata'].values()][0]['p'][-1]['u']
            pic = unescape(pic)
            return {'url': pic, 'title': json['title'], 'subreddit': json['subreddit_name_prefixed'],
                    'ratio': json['upvote_ratio'] * 100, 'upvotes': json['ups'],
                    'permalink': 'https://www.reddit.com' + json['permalink']}

    return None
