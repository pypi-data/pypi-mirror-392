class ObjectModelError(Exception):
    pass


class NotFound(ObjectModelError):
    pass


class ConnectionNotInitialized(ObjectModelError):
    pass
