import asyncio
import datetime
from App.model import IP


async def ip_save(request, user):
    ip=request.ip[0]
    now=datetime.datetime.now()
    ips=[await i for i in user.ips]

    if ip in [i.ip for i in ips]:
        ip_in=[i for i in ips if i.ip == ip][0]
        ip_in.utime=now
        ip_in.count += 1
        await ip_in.save()
    else:
        await IP.insert_many([{
            "ip": ip,
            'ctime': now,
            'utime': now,
            'user': user
        }])
