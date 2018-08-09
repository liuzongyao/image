class MyBaseError(BaseException):
    pass


class FileFormatError(MyBaseError):
    pass


class FileNotExist(MyBaseError):
    pass


class NotFoundError(MyBaseError):
    pass


class ResponseError(MyBaseError):
    pass


class ParseResponseError(MyBaseError):
    pass
