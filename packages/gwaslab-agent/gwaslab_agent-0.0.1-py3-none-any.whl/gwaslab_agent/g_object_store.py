
class ObjectStore:
    def __init__(self):
        self.objects = {}

    def put(self, obj):
        obj_id = f"subset_{len(self.objects)}"
        self.objects[obj_id] = obj
        return obj_id

    def get(self, obj_id):
        return self.objects[obj_id]