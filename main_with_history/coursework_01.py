import datetime
from pprint import pprint
import requests
import time
import json
from tqdm import tqdm

class VkClass:
    url = 'https://api.vk.com/method'

    def __init__(self, token, version='5.131'):
        self.params = {
            'access_token': token,
            'v': version
        }

    def user_info(self, user_id):
        info_params = {
            'user_ids': user_id,
            'fields': 'sex, universities, photo_max_orig'
        }
        response = requests.get(f'{self.url}/users.get', params={**self.params, **info_params}).json()
        return response

    def user_search(self, q, sex, count=50, sort=0, ):
        search_params = {
            'q': q,
            'fields': ' photo_id, verified, sex, bdate, city, country, home_town, has_photo, photo_50,'
                      ' photo_100, photo_200_orig, photo_200, photo_400_orig, photo_max, photo_max_orig,'
                      ' online, lists, domain, has_mobile, contacts, site, education, universities, schools,'
                      ' status, last_seen, followers_count, common_count, occupation, nickname, relatives,'
                      ' relation, personal, connections, exports, wall_comments, activities, interests, music,'
                      ' movies, tv, books, games, about, quotes, can_post, can_see_all_posts, can_see_audio,'
                      ' can_write_private_message, can_send_friend_request, is_favorite, is_hidden_from_feed,'
                      ' timezone, screen_name, maiden_name, crop_photo, is_friend, friend_status, career,'
                      ' military, blacklisted, blacklisted_by_me',
            'sex': sex
        }
        response = requests.get(f'{self.url}/users.search', params={**self.params, **search_params})
        return response.json()

    def search_group(self, q, sorting=0):
        sg_params = {
            'q': q,
            'sort': sorting,
            'count': 30
        }
        response = requests.get(f'{self.url}/groups.search', params={**self.params, **sg_params})
        return response.json()

    def photo_get(self, user_id, count):
        info_params = {
            'owner_id': user_id,
            'album_id': 'wall',
            'rev': '0',
            'extended': '1',
            'photo_sizes': '0',
            'count': count
        }
        response = requests.get(f'{self.url}/photos.get', params={**self.params, **info_params})
        return response.json()

class YaDisk:
    host = 'https://cloud-api.yandex.net'

    def __init__(self, token):
        self.token = token

    def get_header(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def get_files_list(self):
        url = f'{self.host}/v1/disk/resources/files/'
        headers = self.get_header()
        response = requests.get(url, headers=headers)
        return response.json()

    def _get_upload_link(self, path):  # Получаем ссылку для загрузки файла
        url = f'{self.host}/v1/disk/resources/upload'
        headers = self.get_header()
        params = {'path': path, 'overwrite': True}
        response = requests.get(url, headers=headers, params=params)
        pprint(response.json())
        return response.json().get('href')

    def upload_file(self, path, file_name):  # Не используемая функция в курсовой работе, но удалять не стал
        upload_link = self._get_upload_link(path)
        headers = self.get_header()
        response = requests.put(upload_link, data=open(file_name, 'rb'), headers=headers)
        response.raise_for_status()  # Запрашиваем статус
        if response.status_code == 201:
            print("The file upload was successful")

    def new_folder(self, folder_name):  # Функция для создания папки
        url = f'{self.host}/v1/disk/resources/'
        headers = self.get_header()
        params = {'path': folder_name}
        response = requests.put(url=url, params=params, headers=headers)

    def upload_file_url(self, folder_name, file_name, url_file, size, id):
        upload_link = f'/{folder_name}/{file_name}.jpg'
        url = f'{self.host}/v1/disk/resources/upload/'
        headers = self.get_header()
        params = {'path': upload_link, 'url': url_file}
        response = requests.post(url=url, params=params, headers=headers)
        response.raise_for_status()  # Запрашиваем статус
        if response.status_code == 202:  # При успешном результате заносим в лог файл через функцию логирования
            self.logs_upload_txt(file_name, folder_name, id)
            self.logs_upload_json(file_name, size)

    def logs_upload_txt(self, file_name, folder_name, id):  # Функция для логирования действий в файл logs_file.txt
        try:  # Использовал как проверку создан ли такой файл (возможно есть более простой вариант)
            with open('logs_file.txt', 'r') as logs_f:
                print(" ")
        except FileNotFoundError:  # если файл отсутствует, то идёт запись первой строки
            with open('logs_file.txt', 'w', encoding='utf-8') as logs_f:
                #   Хотел, что бы сверху файла была такая надпись, без неё всё было бы проще
                logs_f.write('Регистрации выполняемых действий по копированию фотографий:' + '\n')
        # Дальше уже только добавляем в созданный файл
        with open('logs_file.txt', 'a', encoding='utf-8') as logs_f:
            logs_f.write(f'{id} {datetime.datetime.now()}: Загрузка файла {file_name}.jpg в папку {folder_name} прошла успешно'
                         + '\n')
            print(f'{datetime.datetime.now()}: Загрузка файла {file_name}.jpg в папку {folder_name} прошла успешно')

    def logs_upload_json(self, file_name, size):
        try:
            with open('logs_file.json', encoding='utf-8') as f_json:
                data_json = json.load(f_json)
                data_json += [{'file_name': f'{file_name}.jpg', 'size': size}]
            with open('logs_file.json', 'w') as f_json:
                json.dump(data_json, f_json, ensure_ascii=False, indent=2)
        except FileNotFoundError:
            with open('logs_file.json', 'w') as f_json:
                data_json = [{'file_name': f'{file_name}.jpg', 'size': size}]
                json.dump(data_json, f_json, ensure_ascii=False, indent=2)
        return data_json

if __name__ == '__main__':
    # Создаём объект vk_user в класcе VkClass с нужным токеном
    vk_user = VkClass('5b854648c30a6e6ccf8387c2203d290458563166cea035749c1479dc8b8568282c5918f9b7c2a4e1b9734')
    # Создаём объект ya_disk_user в классе YaDisk с нужным токеном
    ya_disk_user = YaDisk('AQAAAABAsTdkAADLW2HDHm7tHkqVnrowtMgORCU')
    # Указываем необходимые для копирования данные:
    user_id = '926808'  # Указываем ID пользователя, чьи фото хотим скачать
    count_photo = '50'  # Указываем кол-во фотографий, сколько мы хотим сохранить
    directory = 'Photos_new' # Указываем название папки на Я.Диск куда мы сохраняем фотографии

    # Создаём пустой словарь для записи туда названия фотографии и его url на VK
    photo_list = {}
    # И запускаем цикл по всем полученным фотографиям, что бы получить Url фото в лучшем разрешении
    # При этом используем функцию класса VK с методом photos.get
    for photo in tqdm(vk_user.photo_get(user_id, int(count_photo))['response']['items']):
        time.sleep(0.1)
        name_file = str(photo['likes']['count'])
        photo_data_unix = int(photo['date'])
        photo_data = time.strftime("_%d_%m_%Y", time.gmtime(photo_data_unix))  # получаем даты для каждой фото
        if name_file not in photo_list.keys():  # Добавляем проверку на повтор значения лайков
            height = max(photo['sizes'], key=lambda s: s['height'] * s['width'])['height']
            width = max(photo['sizes'], key=lambda s: s['height'] * s['width'])['width']
            photo_list[name_file] = [max(photo['sizes'], key=lambda s: s['height'] * s['width'])['url'],
                                     f'{height}x{width}']
        else:  # Если лайки повторяются, то добавляем в название дату
            photo_list[name_file + photo_data] = [max(photo['sizes'], key=lambda s: s['height'] * s['width'])['url'],
                                                  f'{height}x{width}']
        # print(f'Найдена и скачена фотография с датой публикации '
        #       f'{time.strftime("%d_%m_%Y", time.gmtime(photo_data_unix))}')
    #
    # Получаем словарь, где ключ - имя файла (кол-во лайков + (возможно) даты), а значение - Url фото в макс. качестве
    # и размер изображения

    # Определяем название директории и создаём новую папку
    ya_disk_user.new_folder(directory)
    # Далее запускаем цикл по полученному словарю с функцией класса YaDisk
    # для записи фото в новую папку directory из списка (полученных ранее url)
    for i, (file_name, url_size_photo) in enumerate(tqdm(photo_list.items()), start=1):
        ya_disk_user.upload_file_url(directory, file_name, url_size_photo[0], url_size_photo[1], i)
    # Фотографии скопированы, лог файл заполнен.
