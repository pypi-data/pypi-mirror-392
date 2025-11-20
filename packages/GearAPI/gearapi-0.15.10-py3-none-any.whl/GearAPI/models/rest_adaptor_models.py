from typing import List, Dict

class Result:
    def __init__(self, status_code: int, message: str = '', data: List[Dict] = None):
        """
        Result returned from low-level BaseResource
        
        param:
            status_code: Standard HTTP Status code
            message: Human readable result
            data: Python List of Dictionaries (or maybe just a single Dictionary on error)
        """
        self.status_code = int(status_code)
        self.message = str(message)
        self.data = data if data else []

    def __str__(self):
        return f"Result(status_code={self.status_code}, message='{self.message}', data={self.data})"

    def __repr__(self):
        return self.__str__()
    
    def __iter__(self):
        """
        Make the Result class iterable over its 'data' attribute.
        """
        return iter(self.data)
    
    def add_data(self, new_data: Dict):
        """
        Add a dictionary to the data list.
        """
        self.data.append(new_data)