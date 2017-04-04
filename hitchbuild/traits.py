def needs(**dependencies):
    def decorator(cls):
        cls._needs = dependencies
        return cls
    return decorator


def built_if_exists(cls):
    cls._built_if_exists = True
    return cls
