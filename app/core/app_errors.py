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

    return AppError()
