from dateqa import db

#db.drop_all()
#db.create_all()
#db.session.commit()


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

r = requests.get('http://localhost:5000/user/1')
print(r.text)


body = {'name': 'gemma',
        'username': 'chem',
        'password': '1234',
        'gender': 'female',
        'age': '34',
        'surname': 'aragones'}

body_json = encoder.encode(body)
r = requests.post('http://localhost:5000/user', data=body_json, headers={'content-type': 'application/json'})

#r = requests.delete('http://localhost:5000/user/2')

r = requests.put('http://localhost:5000/user/1', data=body_json, headers={'content-type': 'application/json'})
print(r.text)

interest_body = {'sports': True, 'games': False, 'dancing': False, 'travel': True, 'cinema': True, 'music': True}
body_json = encoder.encode(interest_body)

r = requests.put('http://localhost:5000/user/1/interests', data=body_json, headers={'content-type': 'application/json'})
print(r.text)

r = requests.get('http://localhost:5000/user/1/interests')
print(r.text)