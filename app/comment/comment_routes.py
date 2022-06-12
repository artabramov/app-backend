from flask import g, request
from app import app
from app.core.app_response import app_response
from app.core.user_auth import user_auth
from app.core.basic_handlers import insert, update, delete, select, summarize, search
from app.post.post import Post
from app.comment.comment import Comment


@app.route('/comment/', methods=['POST'], endpoint='comment_insert')
@app_response
@user_auth
def comment_insert():
    """
    Comment insert
    headers: user_token
    params: post_id, comment_content, comment_sum
    """
    if not g.user.can_edit:
        return {}, {'user_token': ['user have not permissions for edit'], }, 406

    post_id = request.args.get('post_id')
    post = select(Post, id=post_id, deleted=0)
    if not post:
        return {}, {'post_id': ['post not found or deleted'], }, 404

    comment_content = request.args.get('comment_content')
    comment_sum = Comment.trunc_sum(request.args.get('comment_sum'))

    comment = insert(Comment, user_id=g.user.id, post_id=post.id, comment_content=comment_content, comment_sum=comment_sum)
    return {
        'comment': str(comment)
    }, {}, 201


@app.route('/comment/<int:comment_id>', methods=['PUT'], endpoint='comment_update')
@app_response
@user_auth
def comment_update(comment_id):
    """ Comment update """
    if not g.user.can_edit:
        return {}, {'user_token': ['user_token must have edit permissions'], }, 406

    comment = select(Comment, id=comment_id, deleted=0)
    if not comment:
        return {}, {'comment_id': ['comment not found or deleted']}, 404

    comment_content = request.args.get('comment_content')
    comment_sum = Comment.trunc_sum(request.args.get('comment_sum'))

    comment_data = {}
    recount_sum = False
    if comment_content:
        comment_data['comment_content'] = comment_content

    if comment_sum:
        comment_data['comment_sum'] = comment_sum
        if comment.comment_sum != comment_sum:
            recount_sum = True

    comment = update(comment, **comment_data)

    if recount_sum:
        post_sum = summarize(Comment, 'comment_sum', post_id=comment.post_id, deleted=0)
        update(comment.post, post_sum=post_sum)

        vol_sum = summarize(Post, 'post_sum', vol_id=comment.post.vol_id, deleted=0)
        update(comment.post.vol, vol_sum=vol_sum)

    return {}, {}, 200