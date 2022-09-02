import requests
import time
import json
from tqdm import tqdm


def vk_to_ya_uploading(count_photos=5):
    user_id = input('Введите id пользователя VK: ')
    while not user_id.isdigit() or int(user_id) <= 0:
        user_id = input('Неверный ввод!\n'
                        'Введите id пользователя VK: ')
    count_photos = count_photos
    count_photos_sys = count_photos
    disk_token = input('Введите Ваш токен Яндекс.Диска: ')
    print('Данные получены, ожидайте...')

    vk_token = '!!!'
    url_vk = 'https://api.vk.com/method/photos.get'
    authorization_params = {'access_token': vk_token,
                            'v': '5.131'}
    params_get_photo = {**authorization_params,
                        'owner_id': user_id,
                        'album_id': 'profile',
                        'rev': 1,
                        'extended': 1,
                        'photo_sizes': 1,
                        'count': 100,
                        'offset': 0}

    disk_headers = {'Content-Type': 'application/json',
                    'Authorization': f'OAuth {disk_token}'}
    url_disk = 'https://cloud-api.yandex.net'
    disk_create_folder_method = '/v1/disk/resources'
    disk_upload_method = '/v1/disk/resources/upload'
    upload_params = {'url': 'url',
                     'path': '/VK_avatars'}

    time.sleep(0.34)
    requests.put(url_disk + disk_create_folder_method,
                 params={'path': '/VK_avatars'},
                 headers=disk_headers)

    bar = tqdm(total=count_photos_sys,
               unit='picture',
               colour='cyan',
               ascii=False)

    all_likes = []
    output_info = []

    def from_vk_to_ya(response):
        for picture in response['response']['items']:
            all_likes.append(picture['likes']['count'])
            picture_name = f"{picture['likes']['count']}.jpg"
            if all_likes.count(picture['likes']['count']) > 1:
                picture_name = (f"{picture['likes']['count']}_"
                                f"{time.ctime(picture['date'])}.jpg"
                                .replace(' ', '_').replace(':', '-'))
            picture_dict = max(picture['sizes'], key=lambda x: x['width'])
            upload_params['url'] = picture_dict['url']
            upload_params['path'] = f'/VK_avatars/{picture_name}'
            time.sleep(0.34)
            upload_status = requests.post(url_disk + disk_upload_method,
                                          params=upload_params,
                                          headers=disk_headers).status_code
            while upload_status > 399:
                bar.write(f'File {picture_dict["url"]}\n'
                          f'Not uploaded. Retrying...Please, wait!', end="\r")
                time.sleep(333)
                upload_status = requests.post(url_disk + disk_upload_method,
                                              params=upload_params,
                                              headers=disk_headers).status_code
                bar.write('', end="\r")
            output_info.append({'file_name': picture_name,
                                'size': f"{picture_dict['height']}X"
                                        f"{picture_dict['width']}({picture_dict['type']})",
                                'status': upload_status})
            bar.update(1)

    while count_photos != 0:
        if count_photos >= 100:
            params_get_photo['count'] = 100
            time.sleep(0.34)
            from_vk_to_ya(requests.get(url_vk, params=params_get_photo).json())
            params_get_photo['offset'] += 100
            count_photos -= 100
        else:
            params_get_photo['count'] = count_photos
            time.sleep(0.34)
            from_vk_to_ya(requests.get(url_vk, params=params_get_photo).json())
            params_get_photo['offset'] += count_photos
            count_photos -= count_photos
    with open('output.json', 'w', encoding='utf-8') as file:
        json.dump(output_info, file)
    print('Готово!')


if __name__ == '__main__':
    vk_to_ya_uploading()
