"""
@author: Kartik Saini

"""

class DataObject:
    file_id = None
    object_id = None
    object_index = None
    
    data = None
    
    def __init__(self, file_id, object_id, object_index):
        self.file_id = file_id
        self.object_id = object_id
        self.object_index = object_index
        
    def write_data(self, data):
        self.data = data
        

class PlacementGroup:
    pg_id = None
    num_of_object = 0
    
    object_list = []
    
    def __init__(self, pg_id):
        self.pg_id = pg_id
        
    def add_object(self, obj):
        self.object_list.append(obj)
        self.num_of_object += 1
        
    def remove_object(self, object_id):
        pass
