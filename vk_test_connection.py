import requests
import yaml

class VK:

   def __init__(self, access_token, user_id, version='5.131'):
       self.token = access_token
       self.id = user_id
       self.version = version
       self.params = {'access_token': self.token, 'v': self.version}

   def users_info(self):
       url = 'https://api.vk.com/method/users.get'
       params = {'user_ids': self.id}
       response = requests.get(url, params={**self.params, **params})
       return response.json()

with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

access_token = config.get('ACCESS_TOKEN', '')
user_id = '7811995'
vk = VK(access_token, user_id)
print(vk.users_info())
