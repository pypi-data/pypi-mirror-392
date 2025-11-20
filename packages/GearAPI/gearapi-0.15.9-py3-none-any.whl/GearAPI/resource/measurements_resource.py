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

"""
TODO: create a method for POST BMS device setpoints
"""


class MeasurementsResource(RestAdaptor):

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
        self.resource = '/measurement/measurements'
        self.realtime_notification = RealtimeNotificationResource(rest_adaptor)




    def get_all_measurements(self, id:str, date_start:str, date_end:str, **kwargs) -> Union[pd.DataFrame,str]:
        """
        return all Result data available as pandas dataframe.
        args:
            id - device id. see device_list.csv for reference.
            date_start - start date of measurement. format YYYY-MM-DD
            date_end - end date of measurment. format YYYY-MM-DD
            kwargs - (optional params) https://www.cumulocity.com/api/core/#operation/getMeasurementCollectionResource
        """
        kwargs = kwargs or {}
        request_params ={
            'dateFrom': date_start,
            'dateTo': date_end,
            'currentPage': 1,
            'pageSize': 2000,
            'valueFragmentType': kwargs.get('valueFragmentType'),
            'valueFragmentSeries': kwargs.get('valueFragmentSeries'),
            'source': id,
            'revert': kwargs.get('revert'),
            **kwargs
        }

        request_params = remove_empty_params(request_params)

        results_df = pd.DataFrame()
        result_messages = []
        while True:
            result = self.get(endpoint = self.resource, ep_params=request_params)
            result_data_measurements = result.data.get('measurements',None)
            result_messages.append(result.message)
            if not result_data_measurements:
                break
            df = multiple_json_normalize(result_data_measurements)
            results_df = pd.concat([results_df,df],ignore_index=True)
            request_params['currentPage'] +=1

        pages_scraped = len(result_messages)
        ok = result_messages.count('OK')
        message = f"{ok}/{pages_scraped} pages scraped successfully."

        return results_df,message

    def get_all_aggregated_measurements(
            self, 
            aggregate_period:str, 
            id:str, 
            date_start:str,
            date_end:str, 
            **kwargs
              ) -> Union[pd.DataFrame,str]:
        """
        return all min max value of the aggregated period data as pandas dataframe. 
        result will provide up to 5000 values. Reduce the date range if required.
        args:
            id - device id. see device_list.csv for reference.
            aggregation_type - aggregation period for the data. Accept "DAILY" "HOURLY" "MINUTELY"
            date_start - start date of measurement
            date_end - end date of measurment.
            kwargs - (optional params) https://www.cumulocity.com/api/core/#operation/getMeasurementSeriesResource
        """

        request_params ={
            'aggregationType': aggregate_period,
            'dateFrom': date_start,
            'dateTo': date_end,
            'type': kwargs.get('type'), #don't use it for source only method
            'series': kwargs.get('valueFragmentSeries'),
            'source': id,
            'revert': kwargs.get('revert'),
            **kwargs

        }

        resource = self.resource + '/series'

        request_params = remove_empty_params(request_params)
        result = self.get(endpoint = resource, ep_params=request_params)
        results_data = result.data

        df = multiple_json_normalize(results_data, id, aggregated=True)

        additional = ''
        if result.data.get('truncated'):
            additional = f'data is trancated. Reduce the date range of the query'

        rows = len(df)
        message = f"{rows} {aggregate_period} aggregated data return successfully.{additional}"
            
        return df, message
    
    def post_setpoints(self, OPC_tag:str, value:Union[str,float], description:str = '') -> str:
        """
        To control the selected BMS devices via the OPC_tag.
        args:  
            OPC_tag - address of the device to be controlled.
            value - value to be set.


        """
        resource = '/devicecontrol/operations'

        body = {
                "deviceId": "78194421", #fixed, BMS VM
                "c8y_ua_command_WriteValue": {
                    "values": {
                        {OPC_tag}: {
                            "value": f"{value}"
                        }
                    }
                },
                "description": {description}
            }

        result = self.post(endpoint = resource, data= body)
        message = result.message
        return message


    # def stream_measurements(self, id:str, stream_method = 'application/json-stream', timeout=10) -> None:
    #     """
    #     WIP
    #     stream measurements from the selected device.
    #     args:
    #         id - device id. see device_list.csv for reference.
    #         stream_method - stream method. default is application/json-stream.
    #     """
    #     url = self.base_url +  f'/notification/realtime'

    #     stream_method_type = ('application/json-stream','text/csv', 'application/vnd.ms-excel', 'application/xlsx')

    #     if stream_method not in stream_method_type:
    #         raise ValueError("Invalid stream_method. Supported methods are: text/csv, application/vnd.ms-excel, application/xlsx")

    #     #text/csv
    #     headers = {
    #         "Accept": stream_method,
    #         'X-Cumulocity-System-Of-Units': 'metric'
    #     }

    #     request_params ={
    #         "channel": f"/measurements/{id}"
    #     }
        

    #     response = self.get(endpoint= '/notification/realtime', ep_params=request_params, stream = True, headers = headers, timeout=timeout)
    #     for line in response.iter_lines(decode_unicode=True):
    #         if line:
    #             print(line)

    # def stream_measurements(self, ids:Union[str,list]) -> None:
    #     rn = self.realtime_notification
    #     ws_thread = threading.Thread(target=rn.run,args=(ids,'measurements'), daemon=True)
    #     ws_thread.start()
    #     print("ready to get data")

    # def get_stream_measurements(self) -> dict:
    #     return self.realtime_notification.get_data()




 