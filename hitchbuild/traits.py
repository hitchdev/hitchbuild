def needs(**dependencies):
    def decorator(cls):
        cls._needs = dependencies
        return cls
    return decorator
