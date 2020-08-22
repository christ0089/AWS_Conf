import boto3
import os
import logging
import io
import time
import folium
import json
import csv
import boto3
import pandas as pd
import folium as fl
import s3fs

f3 = s3fs.S3FileSystem(anon=False)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def get_dom(dt):
    return dt.day

def get_weekdayNum(dt):
    return dt.weekday()

def get_hour(dt):
    return dt.hour

def get_weekday(dt):
    return dt.day_name()
    

    
def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(os.environ)
 
    bucket = 'ubermap'
    key = 'Travel_Times.csv'

    csvfile = s3.get_object(Bucket=bucket, Key=key)
    

    pd.read_csv('{}/{}'.format(bucket, key))
        
    df['Date/Time'] = pd.to_datetime(df['Date/Time'])

    df['DoM'] = df['Date/Time'].map(get_dom)
    df['WeekdayNum'] = df['Date/Time'].map(get_weekdayNum)
    df['Hour'] = df['Date/Time'].map(get_hour)
    df['Weekday'] = df['Date/Time'].map(get_weekday)
    df2 = df[df['DoM'] == 1].reset_index()
    
    start_location = [40.8145, -73.9444]
    map_list = []
    
    print("--------Folium Process---------")

    # El primer ciclo itera en cada dia por medio del metodo unique, aparte crea su Dataframe y mapa.
    for n in (df['DoM'].unique()):
        mapa2 = fl.Map(location = start_location, zoom_start = 10)
        df3 = df[df['DoM'] == n].reset_index()
        # El segundo ciclo agrega los pick_up´s a los mapas de cada dia y los va agregando a map_list.
        for x in range(len(df3)):
            try:
                fl.Circle(
                    radius=0.2,
                    location=[df3['Lat'][x],df3['Lon'][x]],
                    color='red'
                ).add_to(mapa2)
            except:
                pass
        map_list.append(mapa2)
    
    maps = []
    print("--------Create Maps Process---------")
    for x in range(len(map_list)):
        file_url = "map_{index}.html".format(index=1)
        map_list[x].save('tmp/{}'.format(file_url))
    

    ## Upload generated screenshot files to S3 bucket.
        s3.upload_file('/tmp/{}'.format(file_url), os.environ['BUCKET'], '{}/{}'.format(os.environ['DESTPATH'], file_url))
    
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': os.environ['BUCKET'],
                'Key': '{}/{}'.format(os.environ['DESTPATH'], file_url)
            }
        )
        maps.append(url)
 
    print("--------Response  Process---------")
    transactionResponse = {}
    transactionResponse['map_files'] = maps

    #3. Construct http response object
    responseObject = {}
    responseObject['statusCode'] = 200
    responseObject['headers'] = {}
    responseObject['headers']['Content-Type'] = 'application/json'
    responseObject['body'] = json.dumps(transactionResponse)
    #4. Return the response object
    return responseObject
