"""this class is used to hold any information, it can also dynamically expand new propety to host data"""

class AreaData:
    """the main class for holding area data on each level."""
    data_collection = dict()

    def __init__(self, type_name):
        self.title = type_name

    @classmethod
    def purge_data(cls):
        cls.data_collection.clear()
        
        
    @classmethod
    def get_data(cls, type_name):
        key = type_name
        if key in cls.data_collection:
            return cls.data_collection[key]
        instance = AreaData(type_name)

        cls.data_collection[key] = instance
        return instance

    def update(self, area_name, area):
        if not hasattr(self, area_name):
            setattr(self, area_name, area)
            return

        current_area = getattr(self, area_name)
        setattr(self, area_name, current_area + area)
        
