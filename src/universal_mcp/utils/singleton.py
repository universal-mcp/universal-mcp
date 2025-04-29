class Singleton(type):
    """Metaclass that ensures only one instance of a class exists.

    This metaclass implements the singleton pattern by maintaining a dictionary
    of instances for each class that uses it. When a class with this metaclass
    is instantiated, it checks if an instance already exists and returns that
    instance instead of creating a new one.

    Example:
        class MyClass(metaclass=Singleton):
            pass

        a = MyClass()
        b = MyClass()
        assert a is b  # True
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
