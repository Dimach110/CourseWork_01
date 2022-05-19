from pprint import pprint
import time
from tqdm import tqdm
from VK import VkClass
from YaDisk import YaDisk

if __name__ == '__main__':
    # Создаём объект vk_user в класcе VkClass с нужным токеном
    vk_user = VkClass('...')
    # Создаём объект ya_disk_user в классе YaDisk с нужным токеном
    ya_disk_user = YaDisk('...')
    # Указываем необходимые для копирования данные:
    user_id = '...'  # Указываем ID пользователя, чьи фото хотим скачать
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
        height = max(photo['sizes'], key=lambda s: s['height'] * s['width'])['height']
        width = max(photo['sizes'], key=lambda s: s['height'] * s['width'])['width']
        if name_file not in photo_list.keys():  # Добавляем проверку на повтор значения лайков
            photo_list[name_file] = [max(photo['sizes'], key=lambda s: s['height'] * s['width'])['url'],
                                     f'{height}x{width}']
        else:  # Если лайки повторяются, то добавляем в название дату
            photo_list[name_file + photo_data] = [max(photo['sizes'], key=lambda s: s['height'] * s['width'])['url'],
                                                  f'{height}x{width}']
        # print(f'Найдена и скачена фотография с датой публикации '
        #       f'{time.strftime("%d_%m_%Y", time.gmtime(photo_data_unix))}')

    # Получаем словарь photo_list, где ключ - имя файла (кол-во лайков + (возможно) даты),
    # а значение - Url фото в макс. качестве и размер изображения

    # Cоздаём новую директорию на я.Диск
    ya_disk_user.new_folder(directory)
    # Далее запускаем цикл по полученному словарю с функцией класса YaDisk
    # для записи фото в новую папку directory из списка (полученных ранее url)
    for i, (file_name, url_size_photo) in enumerate(tqdm(photo_list.items()), start=1):
        ya_disk_user.upload_file_url(directory, file_name, url_size_photo[0], url_size_photo[1], i)
    # Фотографии скопированы, лог файл заполнен.

