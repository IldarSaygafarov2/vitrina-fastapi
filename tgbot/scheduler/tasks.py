from datetime import datetime


async def send_new_advertisement(advertisement_id: int, time_to_send: datetime):
    print(f'{advertisement_id=}, time_to_send={time_to_send.now()}')