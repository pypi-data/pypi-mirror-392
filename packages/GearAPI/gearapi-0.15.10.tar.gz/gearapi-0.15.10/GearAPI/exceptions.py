

class ResourceError(Exception):
    def __init__(self, message=f"Resource not recognised. Check the resource used."):
        self.message = message
        super().__init__(self.message)

class DeviceFilePathError(Exception):
    def __init__(self, message=f"No data found. check your device_list path and device_list csv"):
        self.message = message
        super().__init__(self.message)

class DeviceListFilteringError(Exception):
    def __init__(self, message=f"No data found. Please check the filtering criteria is correct"):
        self.message = message
        super().__init__(self.message)

class DeviceTypeError(Exception):
    def __init__(self, message=f"No data found. Please check Device Type is correct"):
        self.message = message
        super().__init__(self.message)

class RequestError(Exception):
    """Exception raised for errors during an HTTP request.

    Attributes:
        message -- explanation of the error
        status_code -- HTTP status code related to the error, if available
        original_exception -- original exception raised during the request, if available
    """

    def __init__(self, message="Request failed", status_code=None, original_exception=None):
        self.message = message
        self.status_code = status_code
        self.original_exception = original_exception
        super().__init__(self.message)

    def __str__(self):
        error_message = self.message
        if self.status_code:
            error_message += f" (Status Code: {self.status_code})"
        if self.original_exception:
            error_message += f" - {str(self.original_exception)}"
        return error_message