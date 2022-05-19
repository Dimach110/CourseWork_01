import datetime
from pprint import pprint
import requests
import json


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