from App.model import UserAgents


async def agent_save(request, user):
    ua = request.headers['User-Agent']
    now = datetime.datetime.now()
    uas = [await i for i in user.ips]

    if ua in [i.content for i in contents]:
        ua_in = [i for i in uas if i.content == content][0]
        ua_in.utime = now
        ua_in.count += 1
        await ip_in.save()

    else:
        await UserAgents.insert_many([{
            "content": ua,
            'ctime': now,
            'utime': now,
            'user': user
        }])
