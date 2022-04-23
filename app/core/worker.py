from app import celery
from app.user.user_tasks import user_register, user_restore, user_login, user_logout, user_select