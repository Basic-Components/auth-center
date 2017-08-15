import asyncio
import aiohttp
import datetime
from auth_center.model import IP

async def ip_save(request,user):
    ip = request.ip[0]
    async with aiohttp.ClientSession() as session:
        async with session.get(request.app.config["GEO_URL"],
            params={"ip":ip}) as resp:
            if resp.status == 200:
                try:
                    json_data = await resp.json()
                except:
                    return False
                if json_data['code'] == 0:
                    country = json_data['data'][u'country']
                    city = json_data['data'][u'city']
                    ips = [await i  for i in user.ips]
                    now = datetime.datetime.now()
                    print(city)
                    if ip in [i.ip for i in ips]:
                        ip_in = [i for i in ips if i.ip==ip][0]
                        ip_in.utime = now
                        ip_in.count += 1
                        await ip_in.save()
                    else:
                        await IP.insert_many([{
                        "ip":ip,
                        "country":country,
                        'city':city,
                        'ctime':now,
                        'utime':now,
                        'user':user
                        }])

                else:
                    return False
            else:
                return False
