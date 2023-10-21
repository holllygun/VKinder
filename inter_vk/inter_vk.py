import requests
import json


class VK:
 
   def __init__(self, access_token, user_id, version='5.131'):
       self.token = access_token
       self.id = user_id
       self.version = version
       
   def common_params(self):
       return {
           'access_token': self.token,
           'v': self.version
       }
   def get_profile_photo(self):
       params = self.common_params()
       params.update({"owner_id":self.id, "album_id": "profile","photo_sizes":"0","extended":"1"})
       response =requests.get('https://api.vk.com/method/photos.get', params=params)
       return response.json()
   def get_info_user(self,fields:str):
       params = self.common_params()
       params.update({"user_id":self.id, "fields":fields})
       response =requests.get('https://api.vk.com/method/users.get', params=params)
       return response.json()