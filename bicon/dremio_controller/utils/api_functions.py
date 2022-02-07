import requests
import json
import pandas as pd
from datetime import datetime as dt

from django.conf import settings
base_url = settings.DREMIO_BASE_URL
# base_url = 'http://dremio.bi.stuffio.com'
dremio_user = settings.DREMIO_USER
dremio_pw = settings.DREMIO_PW
data_dir = settings.DATA_DIR
credentials_file = data_dir + 'credentials.json'
url_login = base_url + '/apiv2/login'
url_sql = base_url + '/api/v3/sql'
url_job = base_url + '/api/v3/job/'
url_ref = base_url + '/api/v3/reflection/'
url_catalog = base_url + '/api/v3/catalog/'
# url_user = base_url + '/api/v3/user/by-name/'


def loginDremio():
    body = '{"userName": "' + dremio_user + '","password": "' + dremio_pw + '"}'
    headers = json.loads('{"Content-Type":"application/json"}')
    response_login = requests.request("POST",
                                      url=url_login,
                                      data=body,
                                      headers=headers)
    print('Login Info: ', response_login, url_login, headers, body)
    new_credentials = {'base_url': base_url,
                       'token': response_login.json()['token'],
                       'headers': {
                           "Authorization": "_dremio" + response_login.json()['token'],
                           "Content-Type": "application/json",
                           "cache-control": "no-cache",
                           "Postman-Token": "token"
                       }}
    with open(credentials_file, 'w') as outfile:
        json.dump(new_credentials, outfile)
    outfile.close()
    file = open(credentials_file, 'r')
    cre = json.loads(file.read())
    file.close()
    print('token: ', cre['token'])
    return cre


def getHeaders():
    try:
        file = open(credentials_file, 'r')
        cre = json.loads(file.read())
        file.close()
        _headers = cre['headers']
        response = requests.request("GET", url_catalog, headers=_headers)
        if response.status_code != 200:
            print('Getting new credentials due to outdated credentials')
            cre = loginDremio()
            _headers = cre['headers']
            response = requests.request("GET", url_catalog, headers=_headers)
    except (ImportError, FileNotFoundError):
        print('Getting new credentials due to no credentials')
        cre = loginDremio()
        _headers = cre['headers']
        # response = requests.request("GET", url_catalog, headers=_headers)
    return _headers


def refreshReflection(reflection_id):
    url = url_ref + reflection_id
    _headers = getHeaders()
    response_ref = requests.request("GET", url, headers=_headers)
    response_json = response_ref.json()
    response_json['enabled'] = False
    response_ref = requests.request("PUT", url, headers=_headers, data=json.dumps(response_json))  # disable
    response_json = response_ref.json()
    response_json['enabled'] = True
    response_ref = requests.request("PUT", url, headers=_headers, data=json.dumps(response_json))  # re-enable
    return response_ref.json()


# def viewUser(user_name):
#     url = url_user + user_name
#     response_user = requests.request("GET", url=url, headers=getHeaders())
#     return response_user.json()


# def viewJobState(job_id):
#     url = url_job + job_id
#     response_job = requests.request("GET", url=url, headers=getHeaders())
#     job_state = response_job.json()['jobState']
#     return str(job_state)
#
# def viewReflectionStatus(ref_id):
#     url = url_ref + ref_id
#     response_ref = requests.request("GET", url=url, headers=getHeaders())
#     job_state = response_ref.json()['status']['refresh']
#     return str(job_state)

def getReflection(reflection_id):
    url = url_ref + reflection_id
    response = requests.request("GET", url, headers=getHeaders())
    # reflection = pd.json_normalize(response.json(), max_level=0)
    return response.json()


def getDataset(dataset_id):
    url = url_catalog + dataset_id
    response = requests.request("GET", url, headers=getHeaders())
    dataset = pd.json_normalize(response.json()).drop('entityType', axis=1)
    return dataset


def processCreatedAt(x):
    if x == x:  # when createdAt value not nan
        x = dt.strftime(pd.to_datetime(x), "%Y-%m-%d %H:%M:%S")
    else:
        x = None
    return x


def processPath(x):
    x = x.replace("[", "").replace("]", "").replace(", ", ".").replace("\'", "\"")
    return x
