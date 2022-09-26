"""
Script to read api and save data into the S3 bucket
"""

import pandas as pd
import requests
import toml
import os
import boto3
import time
from dotenv import load_dotenv
import numpy as np

columns = ['company_name', 'location', 'job_name', 'job_type', 'publication_date']
today = time.strftime("%Y-%m-%d")


def read_config():
    app_config = toml.load('configuration.toml')
    return app_config


# function to read api data and convert into json
def read_api(url_config):
    response = requests.get(url_config['api']['url'])
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("URL is unreachable: {}: STATUS CODE-{}".format(url_config['api']['url'], response.status_code))


# function to process json data according to business requirements
"""
Here we are processing 5 fields from Response body
    1. company name
    2. locations --> further divided into City and Country
    3. job name
    4. job type
    4.publication date
"""


def process_json_dataframe(data):
    publication_dates = [data['results'][i]['publication_date'] for i in range(len(data['results']))]
    job_names = [data['results'][i]['name'] for i in range(len(data['results']))]
    job_types = [data['results'][i]['type'] for i in range(len(data['results']))]
    locations = [data['results'][i]['locations'][0]['name'] for i in range(len(data['results']))]
    company_names = [data['results'][i]['company']['name'] for i in range(len(data['results']))]

    # converting data into dataframe
    df = pd.DataFrame(list(zip(company_names, locations, job_names, job_types, publication_dates)),
                      columns=columns)

    # separating location into city and country
    new_df = df['location'].str.split(",", n=1, expand=True)
    df['city'] = new_df[0]
    df['country'] = new_df[0]
    df['country'] = df['country'].fillna(value=df['city'])

    # reducing datetime to date
    df_date = pd.to_datetime(df['publication_date']).dt.date
    df['publication_date'] = df_date

    df.drop(columns=["location"], inplace=True)
    return df



"""
function to get aws session from ~/.aws/credentials file. To setup credentials file you need to
run below command
-----------------------------------------
aws configure
AWS Access Key ID [None]: accesskey
AWS Secret Access Key [None]: secretkey
Default region name [None]: us-west-2
Default output format [None]:
-----------------------------------------
"""


def aws_session():
    load_dotenv()
    access_key = os.getenv('ACCESS_KEY')
    secret_key = os.getenv('SECRET_KEY')
    session = boto3.Session(profile_name='default')
    # credentials = session.get_credentials()
    # s3 = session.resource("s3")
    # print("AWS_ACCESS_KEY_ID = {}".format(credentials.access_key))
    # print("AWS_SECRET_ACCESS_KEY = {}".format(credentials.secret_key))
    # print("AWS_SESSION_TOKEN = {}".format(credentials.token))
    return access_key+","+secret_key


# function to write data into S3 bucket
def save_data_to_s3(file_path, bucket_config):
    access_key,secret_key = aws_session().split(",")

    s3_client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    print(bucket_config['s3']['bucket'])
    try:
        s3_client.upload_file(os.path.abspath(file_path), bucket_config['s3']['bucket'], f'{today}.csv')
    except Exception as e:
        return False
    return True


# function to save data into a file and return absolute path
def save_dataframe_to_file(data_frame):
    data_frame.to_csv(f"{today}.csv", index=False)
    return os.path.abspath(f'{today}.csv')


def run():
    config = read_config()
    data = read_api(config)
    data_frame = process_json_dataframe(data)
    file_path = save_dataframe_to_file(data_frame)
    save_data_to_s3(file_path, config)


if __name__ == "__main__":
    run()
