from requests.auth import HTTPBasicAuth

from dateqa import db

db.drop_all()
db.create_all()
db.session.commit()


import requests

from json import JSONEncoder
encoder = JSONEncoder()

body = {'name': 'toni',
        'username': 'arobres',
        'password': '1234',
        'gender': 'male',
        'age': '34',
        'surname': 'robres'}

body_json = encoder.encode(body)
r = requests.post('http://localhost:5000/user', data=body_json, headers={'content-type': 'application/json'})

print(r.text)
print(r.headers)

user_url = r.headers['Location']

r = requests.get(user_url, auth=HTTPBasicAuth('arobres', '1234'))
print(r.status_code)
print(r.text)



body = {'name': 'gemma',
        'username': 'chem',
        'password': '5678',
        'gender': 'female',
        'age': '34',
        'surname': 'aragones'}

body_json = encoder.encode(body)
r = requests.post('http://localhost:5000/user', data=body_json, headers={'content-type': 'application/json'})

user_url = r.headers['Location']
print(user_url)
r = requests.delete(user_url)

#
# r = requests.put('http://localhost:5000/user/1', data=body_json, headers={'content-type': 'application/json'})
# print(r.text)
#
# interest_body = {'sports': True, 'games': False, 'dancing': False, 'travel': True, 'cinema': True, 'music': True}
# body_json = encoder.encode(interest_body)
#
# r = requests.put('http://localhost:5000/user/1/interests', data=body_json, headers={'content-type': 'application/json'})
# print(r.text)
#
# r = requests.get('http://localhost:5000/user/1/interests')
# print(r.text)