from pprint import pprint

from inter_vk import VK

if __name__ == '__main__':
    token = 'vk1.a.36ZYPXGJhoI394iWlkUh6SYqBw_XzF0IHYa7Bm_KYg1Rn_Q_WrpaJnrYV-jP6_JAW7XE2N9R4mD3gsB56AYSQmfx-Cm1pQf56T-X1yuif2laJIWKFqxGVosSipf9Fi9szUQ_9T5BOMv5u_m9bA461K0SR1U5cokFa0YM-caux3sJTlwgLNMFV8o8m-Ft0DsfCd-W7m58Ie0LEAkiHCuy0A'
    #
    user_vk_id = input("Введите id пользователя: ")

    vk = VK(token, user_vk_id)

    vk_photos = vk.get_profile_photo()
    # В параметрах get_info_user необходимо указывать поле, которое хотим получить city,bdate,sex
    vk_user = vk.get_info_user('city')
    get_members = vk.get_members('223098125', 'city')

    pprint(vk_user)
    pprint(get_members)


