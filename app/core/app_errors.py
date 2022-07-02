def create_errors():
    class AppError:
        INVALID_VALUE = 'Invalid value.'
        EMPTY_VALUE = 'Empty value.'
        VALUE_NOT_FOUND = 'Value not found.'
        ALREADY_EXISTS = 'Already exists.'
        ATTEMPTS_ARE_OVER = 'Attempts are over.'
        PERMISSION_DENIED = 'Permission denied.'
        PERMISSION_SUSPENDED = 'Permission suspended.'
        PERMISSION_EXPIRED = 'Permission expired.'
        FILE_ERROR = 'File error.'

        SERVER_ERROR = 'Internal server error.'
        SERVICE_UNAVAILABLE = 'Service unavailable.'

        NOT_FOUND = '__not found'
        NOT_LEFT = '__not left'
        NOT_ALLOWED = '__not allowed'
        IS_EMPTY = '__is empty'
        IS_EXIST = '__is exist'
        IS_INCORRECT = '__is incorrect'
        IS_OCCUPIED = '__is occupied'
        IS_EXPIRED = '__is expired'
        IS_SUSPENDED = '__is suspended'

    return AppError()
