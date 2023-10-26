from pprint import pprint
from inter_vk import VK

if __name__ == '__main__':
    user_vk_id = input("Введите id пользователя: ")
    token = open("token").read()
    vk = VK(token, user_vk_id)
    # В параметрах get_info_user необходимо указывать поле, которое хотим получить city,bdate,sex
    pprint(vk.get_info_user())
    pprint(vk.get_matches())
    pprint(vk.users_list())
