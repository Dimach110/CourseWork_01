from pprint import pprint
import time
from tqdm import tqdm
from VK import VkClass
from YaDisk import YaDisk
import configparser


def find_photo(user_id, type_photo, count_photo):
    # Создаём пустой словарь для записи туда названия фотографии и его url на VK
    photo_list = {}
    # И запускаем цикл по всем фотографиям пользователя ID, что бы получить Url фото в лучшем разрешении
    # При этом используем функцию класса VK с методом photos.get
    for photo in tqdm(vk_user.photo_get(user_id, type_photo, count_photo)['response']['items']):
        time.sleep(0.1)
        name_file = str(photo['likes']['count'])
        photo_data_unix = int(photo['date'])
        photo_data = time.strftime("_%d_%m_%Y", time.gmtime(photo_data_unix))  # получаем даты для каждой фото
        height = max(photo['sizes'], key=lambda s: s['height'] * s['width'])['height']
        width = max(photo['sizes'], key=lambda s: s['height'] * s['width'])['width']
        if name_file not in photo_list.keys():  # Добавляем проверку на повтор значения лайков
            photo_list[name_file] = [max(photo['sizes'], key=lambda s: s['height'] * s['width'])['url'],
                                     f'{height}x{width}']
        else:  # Если лайки повторяются, то добавляем в название дату
            photo_list[name_file + photo_data] = [max(photo['sizes'], key=lambda s: s['height'] * s['width'])['url'],
                                                  f'{height}x{width}']
    return photo_list

def input_param():
    '''Запрашиваем у пользователя параметры

    :return: [Id пользователя, тип фото (wall или profile), количество фото, директория]
    '''
    # Запрашиваем данные у пользователя (профиль, тип и коли-во фото, директорию куда будем сохранять)
    user = input("Укажите ID пользователя или его имя: ").strip('id')
    print("""Укажите откуда вы ходите загрузить фото:
               'wall' - фотографии со стены
               'profile' - фотографии профиля""")
    type_photo = input(": ")
    count_photo = input("Укажите количество фотографий для выгрузки: ")
    directory = input("Укажите название папки, куда хотите загрузить фотографии: ")
    return [user, type_photo, count_photo, directory]

def save_photo(photo_list, user_param):
    for i, (file_name, url_size_photo) in enumerate(tqdm(photo_list.items()), start=1):
        ya_disk_user.upload_file_url(user_param[3], file_name, url_size_photo[0], url_size_photo[1], i)

if __name__ == '__main__':
    # Загружаем данные токенов из файла .ini
    config = configparser.ConfigParser()
    config.read('set.ini')
    token_vk = config['VK']['token']
    # print(token_vk.encode())
    # print("f898dfaf60c16a3e81c44426f283cc7f948fe616f6508c64d4743289fbfd9043acbf5ee8333991195c914".encode())
    token_yd = config['Yandex_Disk']['token']
    # Создаём объект vk_user в класcе VkClass с нужным токеном, токен запрашиваем из файла .ini
    vk_user = VkClass(token_vk)
    # Создаём объект ya_disk_user в классе YaDisk с нужным токеном
    ya_disk_user = YaDisk(token_yd)
    # Запрашиваем у пользователя параметры и передаём в виде списка в user_papam
    user_param = input_param()

    # запускаем поиск фото по требуемым параметрам
    photo_list = find_photo(user_param[0], user_param[1], user_param[2])

    # Получаем словарь photo_list, где ключ - имя файла (кол-во лайков + (возможно) даты),
    # а значение - Url фото в макс. качестве и размер изображения
    pprint(photo_list)

    # Cоздаём новую директорию на я.Диск
    ya_disk_user.new_folder(user_param[3])
    # Далее запускаем функцию цикла по полученному словарю с функцией класса YaDisk
    # для записи фото в новую папку directory из списка (полученных ранее url)
    save_photo(photo_list, user_param)

    # # Фотографии скопированы, лог файл заполнен.

# id926808