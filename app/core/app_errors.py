def create_errors():
    class AppError:
        NOT_FOUND = 'not found' # 400
        NOT_LEFT = 'not left' # 400
        NOT_ALLOWED = 'not allowed' # 400 

        IS_EMPTY = 'is empty' # 400
        IS_EXIST = 'is exist' # 400
        IS_INCORRECT = 'is incorrect' # 400
        IS_OCCUPIED = 'is occupied' # 400
        IS_EXPIRED = 'is expired' # 400
        IS_SUSPENDED = 'is suspended' # 400

        SERVER_ERROR = 'internal server error' # 500
        SERVICE_UNAVAILABLE = 'service unavailable' # 503
        FILE_ERROR = 'file error'

    return AppError()
