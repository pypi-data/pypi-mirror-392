from datetime import datetime
import pandas as pd
from pandas import json_normalize
import re

def multiple_json_normalize(data:list , id:int = None, aggregated:bool = False) -> pd.DataFrame:
    """
    To transform json format to pandas DataFrame format for measurement data type and event data type.
    args:
        data - data queried
        id - id of the device. To handle aggregated measurement data.
        aggregated - A flag to indicate if the data is aggregated or not.
    return:
        A pandas DataFrame
    """
    if aggregated: 
        return _custom_aggregated_measurement_normalise_json(data, id)
    try:
        return json_normalize(data)
    except AttributeError:
        return json_normalize(data[0])

def _custom_aggregated_measurement_normalise_json(data:dict, id) -> pd.DataFrame:
    """
    A custom function to normalize aggregated measurement data.
    args:
        data - data queried
        id - id of the device. To handle aggregated measurement data.
    return:
        A pandas DataFrame

    """

    rows = []
    values = data['values']
    series = data['series']

    if data.get('values') in (None, [],{}):
        return pd.DataFrame()
    
    for datetime, measurements in values.items():

        for idx, measurement in enumerate(measurements):

            if not measurement:
                row = {
                    'datetime': datetime,
                    'min': None,
                    'max': None,
                    'unit': None,
                    'name': None,
                    'type': None,
                    'id': id
                }
            else:
                row = {
                    'datetime': datetime,
                    'min': measurement.get('min'),
                    'max': measurement.get('max'),
                    'unit': series[idx].get('unit'),
                    'name': series[idx].get('name'),
                    'type': series[idx].get('type'),
                    'id': id
                }
            rows.append(row)

    df = pd.DataFrame(rows)

    return df

def validate_date(date_string: str = None) -> str:
    """ Validate date format 
    args:
        date_string - date string in yyyy-mm-dd format

    return:
        date_string - date string in yyyy-mm-dd format

    """
    if not date_string:
        return
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return date_string
    except ValueError:
        raise ValueError("Date must be in yyyy-mm-dd format")

