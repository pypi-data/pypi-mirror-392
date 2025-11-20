"""
    client for GearAPI
"""
import pandas as pd
from GearAPI.exceptions import DeviceListFilteringError
from typing import Union,List,Optional
from GearAPI.resource import events_resource, inventory_resource, measurements_resource,realtime_notification,alarms_resource
from GearAPI.rest_adaptor import RestAdaptor
import os

class Client:
    """Client for Gear resource"""

    def __init__(
            self,
            user:str,
            password:str,
            device_list_path:str = 'device_list.csv',
    ) -> None:
        self.rest_adaptor = RestAdaptor(user=user,password=password)
        self.events = events_resource.EventsResource(self.rest_adaptor)
        self.measurements = measurements_resource.MeasurementsResource(self.rest_adaptor)
        self.alarms = alarms_resource.AlarmsResource(self.rest_adaptor)
        self.inventory = inventory_resource.InventoryResource(self.rest_adaptor)
        self.realtime_notification = realtime_notification.RealtimeNotificationResource(self.rest_adaptor)


        if os.path.exists(device_list_path):
            self.devices_list = pd.read_csv(device_list_path) 
        else:
            self.devices_list = self.inventory.get_devices_list()
    
    
    def download(
            self, 
            date_start:str, 
            date_end:str,
            device_params:dict, 
            output_file_path = None, 
            alarms:bool = False,
            alarm_count_only:bool = False,
            aggregate_period = None,
            **request_params,
            ) -> pd.DataFrame:

        """
        downloads all the data from the gear api to a csv file.
        args:
            output_file_path - the path to the output file.
            date_start - the start date of the data to download. format YYYY-MM-DD
            date_end - the end date of the data to download. format YYYY-MM-DD
            device_params - a key-value filtering criteria for the devices. Uses the device_list columns as filtering criteria. 
            alarms - if True, will download all the alarms.
            aggregate_period - the aggregation period for the measurements.
            request_params - an additional key-value filtering criteria to the request_params. See the resource class for more information.
        return:
            (Optional) pd.DataFrame - the dataframe of the downloaded data. Only when **output_file_path** is not specified.

        """
        total_devices,ids,resource_endpoint = self._filtered_devices_ids(
            device_params = device_params)
        endpoints_ids = zip(ids,resource_endpoint)
        total_df = pd.DataFrame()

        for idx, (ids,resource_endpoint) in enumerate(endpoints_ids):
            if alarms:
                resource_endpoint == 'alarm/alarms'

                df,message = self.alarms.get_all_alarms(
                        id = ids, 
                        date_start= date_start, 
                        date_end= date_end,
                        alarm_count_only = alarm_count_only,
                        **request_params
                        )
            
            else:
                if resource_endpoint == 'event/events' and aggregate_period:
                    raise DeviceListFilteringError(f'ids {ids} is a event type data and does not provide aggregation. See device list for more information')

                if resource_endpoint == 'event/events':
                    df,message = self.events.get_all_events(
                        id = ids, 
                        date_start= date_start, 
                        date_end= date_end,
                        **request_params
                        )
                elif resource_endpoint == 'measurement/measurements':
                    if aggregate_period:

                        df,message = self.measurements.get_all_aggregated_measurements(
                            aggregate_period = aggregate_period,
                            id = ids, 
                            date_start= date_start, 
                            date_end= date_end,
                            **request_params
                        )
                    else:
                        df,message = self.measurements.get_all_measurements(
                            id = ids, 
                            date_start= date_start, 
                            date_end= date_end,
                            **request_params
                        )
            try:
                total_df = pd.concat([total_df, df], axis=0)
            except UnboundLocalError:
                pass

            print(f"{idx + 1}/{total_devices} completed. {message}")
        
        if not output_file_path:
            return total_df
        total_df.to_csv(output_file_path, index=False)

        return total_df

    def post_setpoints(self, opc_code:str,value:float) -> None:
        """
        Change setpoints & control of the BMS devices via opc code.
        args:
            opc_code - the opc code of the device.
            value - the value to set the setpoint/control to.

        """
        self.measurements.post_setpoints(opc_code,value)

    def _filtered_devices_ids(
            self, 
            device_params:dict, 
            #OR_filtering:bool = 1,
            ) -> Union[int,List[str],List[int]]:
        """
        To filter devices dataframe based on device_list_filter_params parameter and return back the ids. Case-insensitive
        note: supported_fragment filtering for multiple values uses OR method. (all the values mentioned will be included in the filtering)
        args:
            device_params - a key-value filtering criteria for the devices
        return:
            a list of device ids that met the filtering criteria
        """

        df = self.devices_list
        df.columns = df.columns.str.lower()
        df = df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
        device_params = {k.lower(): v.lower() if isinstance(v, str) else v for k, v in device_params.items()}
        
        for key,val in device_params.items():

            if val in (None,[]):
                continue
            elif isinstance(val, list): 

                if key == 'supported_fragment': #to handle dicts-like values for supported_fragment column.
                    filtered_df = pd.DataFrame()
                    for x in val:
                        x = str(x)
                        temp = df.loc[df[key].str.contains(x, na=False)]
                        filtered_df = pd.concat([filtered_df, temp], axis=0)

                    df = filtered_df
                    if len(df) == 0:
                        return DeviceListFilteringError()
                else:
                    df = df.loc[df[key].isin(val)]

                if len(df) == 0:
                    raise DeviceListFilteringError()

                continue
            elif isinstance(val, (str,int)):
                if key == 'supported_fragment': #to handle dicts-like values for supported_fragment column.
                    df = df.loc[df[key].str.contains(val)]

                    if len(df) == 0:
                        raise DeviceListFilteringError()
                    continue
                
                df = df.loc[df[key] == val]
                
                if len(df) == 0:
                        raise DeviceListFilteringError()
            else:
                raise DeviceListFilteringError()

        check = df.loc[df['resource_endpoint'].isnull(),'id'].count()
        if check > 0:
            raise DeviceListFilteringError("Filtering criteria does not have a valid endpoint. Please check your criteria again")

        ids = df['id'].tolist()
        resource_endpoint = df['resource_endpoint'].tolist()

        total_devices = len(ids)

        if not ids:
            raise DeviceListFilteringError()
        
        return total_devices,ids,resource_endpoint
    
    def get_device_list_with_fragments(self) -> None:
        self.inventory.get_devices_list(with_fragment= True)

    def stream_data(self, resource:str, device_params:dict = None)->list:

        resources = ['measurements','events','alarms']
        if resource not in resources:
            raise ValueError('type must be one of the following: measurements, events, alarms')
        
        rn = self.realtime_notification

        if device_params is None:
            rn.initiate(resource=resource)

        else:
            total_devices,ids,_ = self._filtered_devices_ids(
                device_params = device_params)
            
            print(f'There are total of {total_devices} devices for streaming')
            filtered_df = self.devices_list.__deepcopy__()

            filtered_df = filtered_df.loc[filtered_df['id'].isin(ids)]

            for id in ids:
                if id not in filtered_df['id'].values:
                    raise ValueError('Device is not a measurement device')
            
            if resource != 'alarms':
                if resource == 'measurements':
                    check = 'events'
                else:
                    check = 'measurements'

                check_df = filtered_df[filtered_df['resource_endpoint'].str.contains(check)]
                if len(check_df) != 0:
                    raise ValueError(f'filters contain {check} device')
            rn.initiate(ids=ids, resource=resource)
        
        while True:
            current_data = rn.get_data()
            if current_data:
                print(f"Current {resource}: {current_data}")
                return current_data









