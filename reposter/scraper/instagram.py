import aiohttp
import re
from patches import media

class Instagram:
    async def post(self, url: str) -> media.InstagramPost:
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-FB-Friendly-Name': 'PolarisPostActionLoadPostQueryQuery',
            'X-CSRFToken': 'F2o8ZcoKHRWTpAIFM7uQ0H',
            'X-IG-App-ID': '936619743392459',
            'X-FB-LSD': 'AVro3PzlCNo',
            'X-ASBD-ID': '129477',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }
        return await self.request(url, headers)
        
    async def request(self, url: str, headers: dict[str, str]) -> media.InstagramPost:
        async with aiohttp.ClientSession() as session:
            async with session.post('https://www.instagram.com/api/graphql', headers=headers, data=self.get_post_request(url)) as resp:
                if resp.status!= 200: return None
                post = await resp.json(content_type='text/javascript')
                return media.InstagramPost.from_dict(post['data']['xdt_shortcode_media'], url=url)
            
    def get_post_request(self, post_url: str) -> str:
        post = r'^https:\/\/(?:www\.)?instagram\.com\/(?:[a-zA-Z0-9_]+\/)?(?:p|reels?)\/([a-zA-Z0-9_-]+)\/?'
        match = re.match(post, post_url)
        if not match: raise ValueError('No post URL provided.')
        return f"av=0&__d=www&__user=0&__a=1&__req=3&__hs=19776.HYP%3Ainstagram_web_pkg.2.1..0.0&dpr=1&__ccg=UNKNOWN&__rev=1011606959&__s=j4b2ot%3Awtycf8%3Af8q90j&__hsi=7338804015128324278&__dyn=7xeUjG1mxu1syUbFp40NonwgU29zEdEc8co2qwJw5ux609vCwjE1xoswaq0yE7i0n24oaEd86a3a1YwBgao6C0Mo2iyovw8O4U2zxe2GewGwso88cobEaU2eUlwhEe87q7U1bobpEbUGdwtU662O0Lo6-3u2WE5B0bK1Iwqo5q1IQp1yUoxe4Xxui2qi&__csr=l1GIRW9tJFbl4HGZuiLGSqQ8G-p4iWDDCBy8BebHKAaooyVVLgkBjyt2Ai4LjjABHUiyvHj-haamUSn8FQmiiKUx4BCgB0xxevACG4Uoglwu801i_Wx11fw2WO0f103Eo0twPix90wwTwXwpBw16O0s_e04l87u0lqOU02fCw&__comet_req=7&lsd=AVro3PzlCNo&jazoest=2993&__spin_r=1011606959&__spin_b=trunk&__spin_t=1708698462&fb_api_caller_class=RelayModern&fb_api_req_friendly_name=PolarisPostActionLoadPostQueryQuery&variables=%7B%22shortcode%22%3A%22{match.group(1)}%22%2C%22fetch_comment_count%22%3A40%2C%22fetch_related_profile_media_count%22%3A3%2C%22parent_comment_count%22%3A24%2C%22child_comment_count%22%3A3%2C%22fetch_like_count%22%3A10%2C%22fetch_tagged_user_count%22%3Anull%2C%22fetch_preview_comment_count%22%3A2%2C%22has_threaded_comments%22%3Atrue%2C%22hoisted_comment_id%22%3Anull%2C%22hoisted_reply_id%22%3Anull%7D&server_timestamps=true&doc_id=10015901848480474"