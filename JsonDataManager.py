import json
import os

class DataManager:
    def __init__(self, basePath="data"):
        self.basePath = basePath

    def Getpath(self, fileName):
        return os.path.join(self.basePath, fileName)
    
    def load(self, fileName, default=None):
        path = self.Getpath(fileName)
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return default
        
    def save(self, fileName, data):
        path = self.Getpath(fileName)
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
