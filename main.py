import requests
import time
import json
from tqdm import tqdm
from tqdm import trange


def vk_to_ya(count_photos=5):
    count_photos_sys = count_photos
    user_id = input('Введите id пользователя VK: ')
    while not user_id.isdigit() or int(user_id) <= 0:
        user_id = input('Неверный ввод!\n'
                        'Введите id пользователя VK: ')
    disk_token = input('Введите Ваш токен Яндекс.Диска: ')
    folders_name = input('Введите имя создаваемой папки для фото: ')
    print('Данные получены')

    vk_token = 'TOKEN'
    url_vk = 'https://api.vk.com/method/photos.get'
    authorization_params = {'access_token': vk_token,
                            'v': '5.131'}
    params_get_count_photos = {**authorization_params,
                               'owner_id': user_id,
                               'album_id': 'profile'}
    params_get_photo = {**params_get_count_photos,
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
    params_get_meta = {'path': '/',
                       'fields': '_embedded.items.name',
                       'limit': 999999999999}
    time.sleep(0.34)
    get_meta = requests.get(url_disk + disk_create_folder_method,
                            params=params_get_meta,
                            headers=disk_headers).json()
    files_names = [item['name'] for item in get_meta['_embedded']['items']]
    banned_symbols = ['/']
    while (folders_name in files_names or folders_name.isspace()
           or any([s in folders_name for s in banned_symbols])
           or not folders_name):
        if folders_name in files_names:
            print(f'Папка "{folders_name}" уже есть!')
        else:
            print(f'"{folders_name}" - недопустимое название!')
        folders_name = input('Введите другое название папки: ')
    else:
        print('Ожидайте...')

    path = f'/{folders_name}'
    upload_params = {'url': 'url',
                     'path': path}

    time.sleep(0.34)
    total_photos_in_the_album = requests.get(url_vk,
                                             params=params_get_count_photos
                                             ).json()['response']['count']
    if count_photos > total_photos_in_the_album:
        count_photos = total_photos_in_the_album
        count_photos_sys = total_photos_in_the_album

    time.sleep(0.34)
    requests.put(url_disk + disk_create_folder_method,
                 params={'path': path},
                 headers=disk_headers)

    bar = tqdm(total=count_photos_sys,
               unit='picture',
               colour='cyan',
               ascii=False)

    all_likes = []
    output_info = []

    def _uploading(response):
        for picture in response['response']['items']:
            all_likes.append(picture['likes']['count'])
            picture_name = f"{picture['likes']['count']}.jpg"
            if all_likes.count(picture['likes']['count']) > 1:
                picture_name = (f"{picture['likes']['count']}_"
                                f"{time.ctime(picture['date'])}.jpg"
                                .replace(' ', '_').replace(':', '-'))
            picture_dict = max(picture['sizes'], key=lambda x: x['width'])
            upload_params['url'] = picture_dict['url']
            upload_params['path'] = f'{path}/{picture_name}'
            time.sleep(0.34)
            upload_status = requests.post(url_disk + disk_upload_method,
                                          params=upload_params,
                                          headers=disk_headers).status_code
            while upload_status > 399:
                retry = input(f'\nFile {picture_dict["url"]}\n'
                              f'Not uploaded. Retry? Y/N: ').upper()
                if retry == 'N':
                    break
                else:
                    print('Next try after 303 seconds. Just wait 5 min)')
                    for second in trange(303,
                                         position=0,
                                         desc='seconds',
                                         leave=False,
                                         colour='white'):
                        time.sleep(1)
                    upload_status = requests.post(url_disk + disk_upload_method,
                                                  params=upload_params,
                                                  headers=disk_headers
                                                  ).status_code
            output_info.append({'file_name': picture_name,
                                'size': f"{picture_dict['height']}X"
                                        f"{picture_dict['width']}({picture_dict['type']})",
                                'status': upload_status})
            if upload_status < 400:
                bar.update(1)

    while count_photos != 0:
        if count_photos >= 100:
            params_get_photo['count'] = 100
            time.sleep(0.34)
            _uploading(requests.get(url_vk, params=params_get_photo).json())
            params_get_photo['offset'] += 100
            count_photos -= 100
        else:
            params_get_photo['count'] = count_photos
            time.sleep(0.34)
            _uploading(requests.get(url_vk, params=params_get_photo).json())
            params_get_photo['offset'] += count_photos
            count_photos -= count_photos
    with open('output.json', 'w', encoding='utf-8') as file:
        json.dump(output_info, file)
    print('Готово!')


if __name__ == '__main__':
    vk_to_ya()
