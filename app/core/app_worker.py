from app import celery
from app.user.user_tasks import user_register, user_restore, user_signin, user_signout, user_select, user_update, user_remove, image_upload