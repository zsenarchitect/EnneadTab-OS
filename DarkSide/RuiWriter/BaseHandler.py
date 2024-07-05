from abc import ABC, abstractmethod



class BaseHandler(ABC):
    # Class-level dictionary to store instances
    _instances = {}

    def __new__(cls, path, *args, **kwargs):
        # Check if the instance belongs to the base class
        if cls is BaseHandler:
            instances = cls._base_instances
        else:
            # If it's a subclass, use the subclass-specific dictionary
            # or create a new one if it doesn't exist yet
            if not hasattr(cls, '_instances'):
                cls._instances = {}
            instances = cls._instances


        
        # Check if an instance with the same path exists in the dictionary
        if path in instances:
            return instances[path]
        else:
            # Create a new instance if it doesn't exist
            instance = super().__new__(cls)
            instances[path] = instance
            # Initialize the instance with additional arguments
            instance.__init__(path, *args, **kwargs)
            return instance

    @abstractmethod
    def as_json(self):
        pass