from objects import glob, privileges
from quart import jsonify
import json

async def get_users(limit:int=100, search:str=None):
    """Returns the all of a users."""
    query = ['SELECT * FROM users u']
    args = []
    query.append('left join (select userid, ANY_VALUE(ip) as ip, ANY_VALUE(osu_stream) as osu_stream, max(datetime) as last_login from ingame_logins group by userid) as l on u.id = l.userid')

    if search:
        query.append("WHERE `name` LIKE %s")
        args.append(f'{search}%')
        query.append("OR `email` LIKE %s")
        args.append(f'{search}%')

    query.append(f'ORDER BY u.id DESC LIMIT %s')
    args.append(limit)
    
    
    query = ' '.join(query)
    res = await glob.db.fetchall(query, args)
    return res

async def get_user(id:int):
    """Returns the all of a users."""
    query = (f'SELECT * FROM users WHERE id={id}')
    res = await glob.db.fetch(query)
    return res

async def get_user_username(username:str):
    query = (f'SELECT id from users WHERE name="{username}"')
    res = await glob.db.fetch(query)
    return res

async def get_user_email(email:str):
    query = (f'SELECT id from users WHERE email="{email}"')
    res = await glob.db.fetch(query)
    return res

async def get_res_users():
    query = ('select ru.id, ru.country, ru.name,`logs`.msg, `logs`.time  from (SELECT * FROM `users` where NOT users.priv & 1) ru left join `logs` on ru.id=`logs`.to')
    res = await glob.db.fetchall(query)
    return res

async def get_scores(limit:int=25):
    """Returns the all of a scores."""
    query = (
        'SELECT scores_vn.*, maps.artist, maps.title, '
        'maps.set_id, maps.creator, maps.version '
        'FROM scores_vn '
        'JOIN maps ON scores_vn.map_md5 = maps.md5 '
        f'ORDER BY scores_vn.id DESC LIMIT {limit}'
    )
    res = await glob.db.fetchall(query)
    return res

async def get_data(table_name:str, id:str):
    if table_name in ('users'):
        if id.isdigit():
            return await glob.db.fetch('select * from `%s` where id = %s limit 1' % (table_name, id))
        else:
            return (404)
    else:
        return (404)

async def update(table, id, **kargs):
    params = []
    for k, v in kargs.items():
        if v is not None:
            params.append(f"{k}='{v}'")
        else:
            params.append(f"{k}=NULL")
    await glob.db.execute("UPDATE `%s` SET %s WHERE %s = '%s'" % (table, ', '.join(params), *id))
    return 'ok'