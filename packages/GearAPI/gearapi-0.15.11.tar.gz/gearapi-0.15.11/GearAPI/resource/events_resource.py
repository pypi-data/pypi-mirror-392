# coding: utf_8
import pandas as pd
from GearAPI.rest_adaptor import RestAdaptor
from GearAPI.utilis.utilis import remove_empty_params
from GearAPI.helpers.helpers import multiple_json_normalize
from typing import Union

"""
TODO: create a method for POST BMS device setpoints
"""


class EventsResource(RestAdaptor):

    """
    Class for event resource.

    args:
        resource - event resource endpoint
    
    """

    def __init__(
            self,
            rest_adaptor: RestAdaptor) -> None:
        
        super().__init__(
            user=rest_adaptor.user,
            password=rest_adaptor.password
        )
        self.resource = '/event/events'



    def get_all_events(self, id:str, date_start:str, date_end:str, **kwargs) -> Union[pd.DataFrame,str]:
        """
        return all Result data available as pandas dataframe.
        args:
            id - device id. see device_list.csv for reference.
            date_start - start date of measurement. format YYYY-MM-DD
            date_end - end date of measurment. format YYYY-MM-DD
            kwargs - (optional params) e.g. type, valueFragmentSeries, valueFragmentType - https://www.cumulocity.com/api/core/#tag/Events
        """
        kwargs = kwargs or {}
        request_params ={
            'dateFrom': date_start,
            'dateTo': date_end,
            'currentPage': 1,
            'pageSize': 2000,
            'source': id,
            'withSourceDevices': 'True',
            **kwargs
        }

        request_params = remove_empty_params(request_params)
        results_df = pd.DataFrame()
        result_messages = []
        while True:
            result = self.get(endpoint = self.resource, ep_params=request_params)
            result_data_events = result.data.get('events',None)
            result_messages.append(result.message)
            if not result_data_events:
                break
            df = multiple_json_normalize(result_data_events)
            results_df = pd.concat([results_df,df],ignore_index=True)
            request_params['currentPage'] +=1

        pages_scraped = len(result_messages)
        ok = result_messages.count('OK')
        message = f"{ok}/{pages_scraped} pages scraped successfully."
        return results_df,message
