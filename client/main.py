from tgbot.utils import google_sheet as gsh
import asyncio
from datetime import datetime

from httpx import AsyncClient




async def _make_request(url: str, params: dict):
    async with AsyncClient() as client:
        response = await client.get(url, params=params)
        return response.json()


URL = 'http://0.0.0.0:3000/api/v1/dev/advertisements/'

async def make_request(operation_type: str):
    params = {
        'operation_type': operation_type,
        'page_size': 100
    }
    _response = await _make_request(URL, params)
    pages = _response['pages']
    for page in range(1, pages+1):
        params['page'] = page
        _page_response = await _make_request(URL, params)
        _advertisements = _page_response['advertisements']
        for _advertisement in _advertisements:
            dt = datetime.fromisoformat(_advertisement.get('created_at').replace("Z", "+00:00"))


        print('='*60)





async def main():
    await make_request('BUY')


asyncio.run(main())


