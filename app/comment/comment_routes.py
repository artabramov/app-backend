from flask import g, request
from app import app
from app.core.app_response import app_response
from app.core.user_auth import user_auth
from app.core.basic_handlers import insert, update, delete, select, search
from app.post.post import Post
from app.comment.comment import Comment


@app.route('/comment/', methods=['POST'], endpoint='comment_insert')
@app_response
@user_auth
def comment_insert():
    """
    Comment insert
    headers: user_token
    params: post_id, comment_content
    """
    if not g.user.can_edit:
        return {}, {'user_token': ['user have not permissions for edit'], }, 406

    post_id = request.args.get('post_id')
    post = select(Post, id=post_id, deleted=0)
    if not post:
        return {}, {'post_id': ['post not found or deleted'], }, 404

    comment_content = request.args.get('comment_content')
    comment = insert(Comment, user_id=g.user.id, post_id=post.id, comment_content=comment_content)
    return {
        'comment': str(comment)
    }, {}, 201

