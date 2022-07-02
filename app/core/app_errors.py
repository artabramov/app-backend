def create_errors():
    class AppError:
        INVALID_VALUE = 'Invalid value.'
        VALUE_NOT_FOUND = 'Value not found.'
        ALREADY_EXISTS = 'Already exists.'
        PERMISSION_DENIED = 'Permission denied.'
        ATTEMPTS_ARE_OVER = 'Attempts are over.'

        NOT_FOUND = '!not found'
        NOT_LEFT = '!not left'
        NOT_ALLOWED = '!not allowed'

        IS_EMPTY = '!is empty'
        IS_EXIST = '!is exist'
        IS_INCORRECT = '!is incorrect'
        IS_OCCUPIED = '!is occupied'
        IS_EXPIRED = '!is expired'
        IS_SUSPENDED = '!is suspended'

        SERVER_ERROR = '!internal server error'
        SERVICE_UNAVAILABLE = '!service unavailable'
        FILE_ERROR = '!file error'

    return AppError()
