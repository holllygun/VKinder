from pprint import pprint

from inter_vk.inter_vk import VK

   
if __name__ == '__main__':
    token = open("private/token_vk.txt").read()
    user_vk_id = input("Введите id пользователя: ")
    

    vk = VK(token, user_vk_id)
    vk_photos = vk.get_profile_photo()
    pprint(vk_photos)