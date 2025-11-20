import pandas as pd
from GearAPI.rest_adaptor import RestAdaptor
from GearAPI.utilis.utilis import remove_empty_params
from GearAPI.helpers.helpers import multiple_json_normalize
from GearAPI.resource.realtime_notification import RealtimeNotificationResource

from typing import Union
import websocket
import json
import threading
from time import time



class AlarmsResource(RestAdaptor):

    """
    Class for measurements resource.


    args:
        resource - measurements resource endpoint
    
    """

    def __init__(
            self,
            rest_adaptor: RestAdaptor) -> None:
        
        super().__init__(
            user=rest_adaptor.user,
            password=rest_adaptor.password
        )
        self.resource = '/alarm/alarms'
        self.realtime_notification = RealtimeNotificationResource(rest_adaptor)

    def get_all_alarms(self, id:str, date_start:str, date_end:str, alarm_count_only:bool = False, **kwargs) -> Union[pd.DataFrame,str]:
        """
        return all Result data available as pandas dataframe.
        args:
            id - device id. see device_list.csv for reference.
            date_start - start date of measurement. format YYYY-MM-DD
            date_end - end date of measurment. format YYYY-MM-DD
            alarm_count_only - (optional) if True, return number of alarms occurance
            kwargs - (optional params) https://www.cumulocity.com/api/core/#operation/getMeasurementCollectionResource
        """
        kwargs = kwargs or {}
        request_params ={
            'dateFrom': date_start,
            'dateTo': date_end,
            'currentPage': 1,
            'pageSize': 2000,
            'resolved': kwargs.get('resolved') or True, #get all active or acknowledged alarms
            'severity': kwargs.get('severity') or 'MAJOR',
            'withSourceDevices': kwargs.get('withSourceDevices') or True,
            'withSourceAssets': kwargs.get('withSourceAssets') or True,
            'source': id,
            'type': kwargs.get('type') or 'c8y_UnavailabilityAlarm',
            **kwargs
        }

        request_params = remove_empty_params(request_params)

        if alarm_count_only:
            resource = self.resource + '/count'
            return self._download_alarm_count(resource,request_params)

        results_df = pd.DataFrame()
        result_messages = []
        while True:
            result = self.get(endpoint = self.resource, ep_params=request_params)
            result_data_alarms = result.data.get('alarms',None)
            result_messages.append(result.message)
            if not result_data_alarms:
                break
            df = multiple_json_normalize(result_data_alarms)
            results_df = pd.concat([results_df,df],ignore_index=True)
            request_params['currentPage'] +=1

        pages_scraped = len(result_messages)
        ok = result_messages.count('OK')
        message = f"{ok}/{pages_scraped} pages scraped successfully."

        return results_df,message
    
    def _download_alarm_count(self,resource,request_params):
        
        result = self.get(endpoint = resource, ep_params=request_params)
        print(result)
        result_data_alarms = result.data
        if result_data_alarms == []:
            result_data_alarms = 0
        message = f"alarm count page scraped successfully."
        id = request_params.get('source')

        results_df = pd.DataFrame({'id': [id], 'count': [result_data_alarms]})
        print(results_df)

        return results_df,message

    def stream_alarms(self, ids:Union[str,list]) -> None:
        rn = self.realtime_notification
        ws_thread = threading.Thread(target=rn.run,args=(ids,'alarms'), daemon=True)
        ws_thread.start()
        print("ready to get data")

    def get_stream_alarms(self) -> dict:
        return self.realtime_notification.get_data()