# coding: utf_8
import pandas as pd
from GearAPI.rest_adaptor import RestAdaptor
from datetime import datetime


class InventoryResource(RestAdaptor):

    def __init__(
            self,
            rest_adaptor: RestAdaptor) -> None:
        
        super().__init__(
            user=rest_adaptor.user,
            password=rest_adaptor.password
        )    
        """
        This class is used to get device information from Cumulocity IoT.

        args:
            device_list - path to device_list.csv file. 
            resource - inventory resource endpoint

        """
        self.resource = '/inventory/managedObjects'
        self.device_list = None

    def get_device_count(self, query=None):
        """get the total number of devices

        Args:
            base_uri(string): Base URI of the connection destination
            user(string): Username for authentication
            password(string): Password for authentication
            query(string): Query for filtering(optional)

        Returns:
            integer: number of devices

        """

        params = {
            'pageSize': 1,
            'withTotalPages': 'true'
        }
        if query is not None:
            params['query'] = query
        res = self.get(endpoint = self.resource, ep_params=params)
        device_count = res.data['statistics']['totalPages']
        return device_count

    def get_devices_info(self, query:str =None) -> pd.DataFrame:
        """get information of all devices
        
        Args:
            query - Query using cumulocity query language for filtering(optional)

        Returns:
            dataframe: Pandas DataFrame containing device information

        """
        total_pages = self.get_device_count()
        params = {
            'pageSize': 2000,
            'query': query 
        }
        if query is not None:
            params['query'] = query
        results = []
        for current_page in range(1,total_pages+1):
            params['currentPage'] = current_page
            res = self.get(endpoint = self.resource, ep_params=params)
            data = res.data
            if len(data['managedObjects']) == 0:
                break
            else:
                for managed_object in data['managedObjects']:
                    # temp_dict is just sample.
                    # you can add keys for the desired attribute information to this dictionary.
                    temp_dict = {
                        'id': managed_object.get('id', ''),
                        'name': managed_object.get('name', ''),
                        'deviceType': managed_object.get('deviceType', ''),
                        'subType': managed_object.get('subType', ''),
                        'status': managed_object.get('c8y_Availability', {}).get('status', ''),
                        'lastMessage': managed_object.get('c8y_Availability', {}).get('lastMessage', ''),
                        'zid': managed_object.get('zid', ''),
                        'zoneName': managed_object.get('zoneName', ''),
                        'floor': managed_object.get('floor', ''),
                        'type': managed_object.get('type', ''),
                        'owner': managed_object.get('owner', ''),
                        'creation_time': managed_object.get('create_time','')
                    }
                    results.append(temp_dict)
        df = pd.DataFrame(results)

        #replace column name to python convention
        rename_dict = {
            'deviceType': 'device_type',
            'subType': 'sub_type',
            'lastMessage': 'last_message',
            'zoneName' : 'zone_name',
        }

        df.rename(columns=rename_dict)

        if df['id'].duplicated().any():
            raise ValueError("The 'id' column contains duplicate values, which must be unique.")
        
        return df
    
    def get_supported_fragment_and_series(self,df:pd.DataFrame) -> pd.DataFrame:
        """
        Retrieve all supported measurement fragments and series of a specific managed object by a given ID.
        Useful as reference to work with specific measurement fragment and series.
        args:
            df - df generated from get_device_info
        """
        counter = 1
        total = len(df['id'])

        for id in df['id']:
            current = counter / total
            print(f'{current:.3f}%')
            resource = f'{self.resource}/{id}/supportedSeries'
            result = self.get(endpoint = resource)
            supported_fragment = result.data
            df.loc[id, 'supported_fragment'] = [supported_fragment]
            counter += 1

        return df

    def _get_endpoint(self,df:pd.DataFrame) -> pd.DataFrame:
        """
        Set event resource or measurements resource endpoint for each devices in the df. 
        This will allow GET request to go to the correct resource endpoint.
        args:
            df - df generated from get_device_info
        return:
            df with a new column (resource_endpoint) that has the resource endpoint
        """
        #All Device Type contain either measurement type or event type.
        events_endpoint = ('CCTV','acms','vms','ai-camera','pms','smart_box','Robot','oura')
        measurements_endpoint = ('iaq','Smart_landscaping','smart_landscaping','restroom','solar_panel','BMS','LMS')

        #To handle Device Type collabo which contain measurements and event type.
        collabo_events_endpoint = ('ktg_tabletuser','ktg_fisheye_camera','ktg_dome_camera','ktg_conversation_sensor','ktg_bicycle_load','ktg_tablet_screen')
        collabo_measurements_endpoint = ("ktg_tablet", "ktg_mic_array", "ktg_humidification", "ktg_aq_illuminance", "ktg_diffuseron", "ktg_illuminance_Uv", "ktg_spot_light", "ktg_illuminance_I", "ktg_airflow", "ktg_controller_table", "ktg_camera", "ktg_fan", "ktg_ventilation", "ktg_ziaino", "ktg_aircon", "ktg_pillar_light", "ktg_meeting", "ktg_air_quality_H", "ktg_dehumidification", "ktg_air_quality_T", "ktg_space_player", "ktg_speaker", "ktg_line_light", "ktg_scene", "ktg_actuation_trigger", "ktg_ventilation_fan", "ktg_humidification_fan", "utilization_rate", "fine_mist_machine_(green_aircon)", "uilization_rate")
        
        df.loc[df['deviceType'].isin(events_endpoint), 'resource_endpoint'] = 'event/events'
        df.loc[df['deviceType'].isin(measurements_endpoint), 'resource_endpoint'] = 'measurement/measurements'
        df.loc[df['type'].isin(collabo_events_endpoint), 'resource_endpoint'] = 'event/events'
        df.loc[df['type'].isin(collabo_measurements_endpoint), 'resource_endpoint'] = 'measurement/measurements'

        return df
    
    def get_devices_list(self, with_fragment:bool=False, query:str="has(deviceType)" ) -> pd.DataFrame:
        """
        device info list with fragment series and resource endpoint
        
        args:
            df - df generated from get_device_info
            query - Query using cumulocity query language for filtering. default to remove devices that has no availability tracking. 
        return:
            df with 2 new columns (resource_endpoint and supported_fragment)
        """
        df = self.get_devices_info(query)
        if with_fragment:
            df = self.get_supported_fragment_and_series(df)  #takes too long to load.
        df = self._get_endpoint(df)
        df['lastMessage'] = pd.to_datetime(df['lastMessage'])
        df['device_list_query_date'] = datetime.today()
        df.to_csv('device_list.csv', index=False)
        return df
    
    
