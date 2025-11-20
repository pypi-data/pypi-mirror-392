# coding: utf_8

import logging.config
import requests
from requests.auth import HTTPBasicAuth
from json import JSONDecodeError
from GearAPI.models.rest_adaptor_models import Result
from GearAPI.utilis.utilis import retry
from GearAPI.exceptions import RequestError
import configparser
from typing import Dict
import os
import logging
from GearAPI.helpers.helpers import validate_date
import base64

# Configure logging at the module level
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='API.log',  # Log output file
    filemode='w'  # Write mode (overwrite)
)

logger = logging.getLogger(__name__)


class RestAdaptor:
    """
    A Generic Rest Adaptor with credential.

    args:
        _credentials = a stored credential from config.ini. Use for API authentication.
        _ssl_verify = a generic ssl verification. (Not required for things Cloud API call.)
    """

        
    def __init__(self, user:str, password:str):
        self.user = user
        self.password = password
        self.base_url = 'https://thegear.jp.cumulocity.com'
        self.websocket_url = 'wss://thegear.jp.cumulocity.com'
        self.tenant_id = 't21092648'
        self.authorisation_header = self._set_authorisation_header()
    
    @retry(attempts=3, delay=2, backoff=2)
    def _do(self, http_method: str,endpoint: str, ep_params: Dict = None, data: Dict = None, stream=None, headers=None, timeout=None) -> Result:
        """
        A generic rest API call method
        args:
            http_method = http method. e.g get, post, del
            endpoint = endpoint of the request url.
            ep_params = endpoint params for the request url.
            data = data to perform POST method.
            stream = stream the response.
            headers = headers for the request.

        output:
            Result = An API data wrapped in a object class with additional meta information of the API request. 
            (With stream enabled) - return raw response
        """
        full_url = self.base_url + endpoint

        if ep_params:
            validate_date(ep_params.get('dateTo'))
            validate_date(ep_params.get('dateFrom'))
        
        #logger.debug(ep_params)
        try:
            if headers:
                response = requests.request(method=http_method, url=full_url, params=ep_params, json=data, stream=stream, headers=headers, timeout=timeout) #long-polling connection method
            else:
                response = requests.request(method=http_method, url=full_url, auth=HTTPBasicAuth(self.user, self.password), params=ep_params, json=data)
                
        except requests.exceptions.RequestException as e:
            raise RequestError("Request failed") from e
        try:
            if stream:
                if 299 >= response.status_code >= 200:
                    return response
            
            data_out = response.json()

        except (ValueError, JSONDecodeError) as e:
            raise RequestError("Bad JSON in response") from e
        if 299 >= response.status_code >= 200:     # 200 to 299 is OK
            return Result(response.status_code, message=response.reason, data=data_out)

        raise RequestError(f"{response.status_code}: {response.reason}")

    def get(self, endpoint: str, ep_params: Dict = None, stream:bool = False, headers=None, timeout:int = None) -> Result:
        """
        Generic REST GET method.
        args:
            endpoint - endpoint of the request url.
            ep_params - endpoint params for the request url.
            stream - stream the response.

        return:
            Result = An API data wrapped in a object class with additional meta information of the API request. 
        """
        return self._do(http_method='GET', endpoint=endpoint, ep_params=ep_params, stream=stream, headers=headers, timeout = timeout)

    def post(self, endpoint: str, ep_params: Dict = None, data: Dict = None,  headers=None) -> Result:
        """
        Generic REST POST method.
        args:
            endpoint - endpoint of the request url.
            ep_params - endpoint params for the request url.
            data - data to perform POST method.
        return:
            Result = An API data wrapped in a object class with additional meta information of the API request. 
        """
        return self._do(http_method='POST', endpoint=endpoint, ep_params=ep_params, data=data, headers=headers)

    def delete(self, endpoint: str, ep_params: Dict = None, data: Dict = None) -> Result:
        """
        Generic REST DELETE method.
        args:
            endpoint - endpoint of the request url.
            ep_params - endpoint params for the request url.
            data - data to perform DELETE method.
        return:
            Result = An API data wrapped in a object class with additional meta information of the API request. 
        """
        return self._do(http_method='DELETE', endpoint=endpoint, ep_params=ep_params, data=data)
    
    def _set_authorisation_header(self):
        credentials = f"{self.tenant_id}/{self.user}:{self.password}"

        return base64.b64encode(credentials.encode()).decode()



