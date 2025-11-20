This is a Python client for the Cumulocity Data API. The GearAPI package is a wrapper to simplify GET requests and JSON response parsing from the Measurement and Event Resources. 

This library abstracts:
1. API endpoint handling
2. pagnation handling
3. API retry
4. file handling
5. Handling API from multiple devices 

## how to use

2. `pip install GearAPI`


```
from GearAPI import Client

client = Client(
    user = <IoT Platform User Name>
    password = <IoT Platform User Password>
)

date_start = "2025-03-01"
date_end = "2025-03-02"
device_params = {
    "devicetype": "iaq"
}
output_file_path = "output.csv"

client.download(
    date_start, 
    date_end, 
    output_file_path = output_file_path, 
    device_params = device_params)

"""
output: all the iaq devices data from 2024-08-01 to 2024-08-02
"""
```

go to https://github.com/kajimadev-KaTRIS/GearAPI/deployments/github-pages and click on the latest weblink for more information


## data in csv
some of the data doesn't open properly in excel .csv (e.g. oura ring heart rate data) due to limited size. 
please use pandas to visualise the data for now.