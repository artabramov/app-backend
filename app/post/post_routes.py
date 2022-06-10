from flask import request
from app import app
from app.core.app_response import app_response
from app.user.user_handlers import user_auth
from app.core.primary_handlers import insert, update, delete, select, search
from app.post.post import Post


@app.route('/post/', methods=['POST'], endpoint='post_post')
@app_response
def post_post():
    """ Post insert """
    user_token = request.headers.get('user_token')
    vol_id = request.args.get('vol_id', None)
    post_title = request.args.get('post_title', None)

    this_user = user_auth(user_token)

    if not this_user.can_edit:
        return {}, {'user_token': ['user_token have not permissions for post insert'], }, 406

    post_meta = {
        'key_1': 'value 1!!!',
        'key_2': 'value 2!!!',
        'key_3': 'value 3!!!',
    }

    post = insert(Post, user_id=this_user.id, vol_id=vol_id, post_title=post_title, meta=post_meta)

    return {
        'vol': str(post)
    }, {}, 201

