
#
# Written by
#
#     ___   _____ __         _
#    /   | / ___// /_  _____(_)___ ___  ____
#   / /| | \__ \/ __ \/ ___/ / __ `__ \/ __ \
#  / ___ |___/ / / / / /  / / / / / / / /_/ /
# /_/  |_/____/_/ /_/_/  /_/_/ /_/ /_/ .___/
#                                   /_/
#
# Special thanks to
#
#     ____                   ________
#    / __ \_________  ____  / ____/ /
#   / / / / ___/ __ \/ __ \/ /_  / /
#  / /_/ / /  / /_/ / /_/ / __/ / /___
# /_____/_/   \____/ .___/_/   /_____/
#                 /_/
#
# and
#
#     ____
#    / __ )____ _____  ____  ____
#   / __  / __ `/ __ \/ __ \/ __ \
#  / /_/ / /_/ / /_/ / /_/ / / / /
# /_____/\__, /\____/\____/_/ /_/
#       /____/
#

import datetime
import hashlib
import json
import os
import requests
import shutil
import sys

from settings import loadSettings, getSettingsMap

AUTH_HOST = 'https://oauth.secure.pixiv.net'
SEARCH_HOST = 'https://app-api.pixiv.net'

if not os.path.isdir('images'):
    os.mkdir('images')

loadSuccess = loadSettings('settings.json')

if not loadSuccess:
    try:
        input('press ENTER to close')
    except:
        pass
    sys.exit(0)

settings = getSettingsMap()

local_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')

try:
    with open('refresh_token.txt', encoding='utf-8') as refresh_token_file:
        refresh_token = refresh_token_file.read().strip()
except:
    refresh_token = None

if refresh_token is None:
    result = requests.post('{}/auth/token'.format(AUTH_HOST), {
        'get_secure_url': 1,
        'client_id': 'MOBrBDS8blbauoSck0ZfDbtuzpyT',
        'client_secret': 'lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj',
        'grant_type': 'password',
        'username': settings['username'],
        'password': settings['password']
    }, headers={
        'User-Agent': 'PixivAndroidApp/5.0.64 (Android 6.0)',
        'X-Client-Time': local_time,
        'X-Client-Hash': hashlib.md5((local_time + '28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c').encode('utf-8')).hexdigest(),
    })
else:
    result = requests.post('{}/auth/token'.format(AUTH_HOST), {
        'get_secure_url': 1,
        'client_id': 'MOBrBDS8blbauoSck0ZfDbtuzpyT',
        'client_secret': 'lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj',
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }, headers={
        'User-Agent': 'PixivAndroidApp/5.0.64 (Android 6.0)',
        'X-Client-Time': local_time,
        'X-Client-Hash': hashlib.md5((local_time + '28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c').encode('utf-8')).hexdigest(),
    })

if result.status_code not in [200, 301, 302]:
    try:
        if os.path.isdir('refresh_token.txt'):
            os.unlink('refresh_token.txt')
    except:
        pass

    print('authentication failed :(')
    print('please contact to led789zxpp@naver.com')
    try:
        input('press ENTER to close')
    except:
        pass
    sys.exit(1)

token = json.loads(result.text)
access_token = token['response']['access_token']
refresh_token = token['response']['refresh_token']
user_id = token['response']['user']['id']
user_name = token['response']['user']['name']

print('login success :)')
print('access_token:', access_token)
print('refresh_token:', refresh_token)
print('user_id:', user_id)
print('user_name:', user_name)

try:
    print('saving refresh token for later use')

    with open('refresh_token.txt', 'w', encoding='utf-8') as refresh_token_file:
        refresh_token_file.write(refresh_token)
except:
    pass

while True:
    print()
    result = input(
        'do you want to sort artworks in chronological descending(latest-first) order? [Y/n]: ').strip()

    if result == '' or result == 'y' or result == 'Y':
        sort = 'date_desc'
        break
    elif result == 'n' or result == 'N':
        sort = 'date_asc'
        break

    print('please enter correct answer')

while True:
    print()
    result = input(
        'enter anchor artwork id (less than 1 will disable it): ').strip()

    try:
        limit_id = int(result)

        if limit_id < 1:
            limit_id = None

        break

    except:
        pass

    print('please enter correct number')

halt = False
search_url = None

while True:
    if search_url is None:
        print('searching for tags:', settings['tags'])

        search_result = requests.get('{}/v1/search/illust'.format(SEARCH_HOST), {
            'word': settings['tags'],
            'search_target': 'partial_match_for_tags',
            'sort': sort,
        }, headers={
            'App-OS': 'ios',
            'App-OS-Version': '12.2',
            'App-Version': '7.6.2',
            'User-Agent': 'PixivIOSApp/7.6.2 (iOS 12.2; iPhone9,1)',
            'Authorization': 'Bearer {}'.format(access_token)
        })
    else:
        search_result = requests.get(search_url, headers={
            'App-OS': 'ios',
            'App-OS-Version': '12.2',
            'App-Version': '7.6.2',
            'User-Agent': 'PixivIOSApp/7.6.2 (iOS 12.2; iPhone9,1)',
            'Authorization': 'Bearer {}'.format(access_token)
        })

    search_result.encoding = 'utf-8'

    if search_result.status_code != 200:
        print('search failed :(')
        print('please contact to led789zxpp@naver.com')
        try:
            input('press ENTER to close')
        except:
            pass
        sys.exit(1)

    images = json.loads(search_result.text)

    for image in images['illusts']:
        if halt:
            break

        print('downloading:', image['title'])

        if 'meta_pages' in image and len(image['meta_pages']) != 0:
            length = len(image['meta_pages'])

            if length == 1:
                print('1 image found')
            else:
                print('{} images found'.format(length))

            if limit_id is not None:
                try:
                    image_id = int(image['id'])

                    if sort == 'date_desc':
                        if image_id < limit_id:
                            print(
                                'the id of this artwork({}) is lower than limit id({}).'.format(image_id, limit_id))
                            print('halting')
                            halt = True
                            continue
                    else:
                        if image_id > limit_id:
                            print(
                                'the id of this artwork({}) is higher than limit id({}).'.format(image_id, limit_id))
                            print('halting')
                            halt = True
                            continue

                except:
                    pass

            if 1 <= settings['max-page-image-count']:
                if settings['max-page-image-count'] < length:
                    print('the number of these images exceeds {}(from max-page-image-count in the settings.json file).'.format(
                        settings['max-page-image-count']))
                    print('skipping')
                    continue

            for index in range(0, length):
                print('{} / {}'.format(index + 1, length))

                if 'original' in image['meta_pages'][index]['image_urls']:
                    url = image['meta_pages'][index]['image_urls']['original']
                    print('original image found:', url)
                elif 'large' in image['meta_pages'][index]['image_urls']:
                    url = image['meta_pages'][index]['image_urls']['large']
                    print('large image found:', url)
                elif 'medium' in image['meta_pages'][index]['image_urls']:
                    url = image['meta_pages'][index]['image_urls']['medium']
                    print('medium image found:', url)
                elif 'square_medium' in image['meta_pages'][index]['image_urls']:
                    url = image['meta_pages'][index]['image_urls']['square_medium']
                    print('square_medium image found:', url)
                else:
                    print('no image found :(')
                    print('skipping')
                    continue

                ext = url.split('.')[-1]
                filename = '{} - {} {}.{}'.format(
                    image['id'],
                    image['title']
                    .replace('/', '_')
                    .replace('\\', '_')
                    .replace(':', '_')
                    .replace('*', '_')
                    .replace('?', '_')
                    .replace('"', '_')
                    .replace('<', '_')
                    .replace('>', '_')
                    .replace('|', '_'), index + 1, ext)

                if os.path.isfile(os.path.join('images', filename)):
                    print('duplicated filename detected')
                    print('skipping')
                    continue

                image_response = requests.get(url, headers={
                    'Referer': 'https://app-api.pixiv.net/',
                }, stream=True)

                with open(os.path.join('images', filename), 'wb') as image_file:
                    shutil.copyfileobj(image_response.raw, image_file)

        else:
            if 'meta_single_page' in image:
                if 'original_image_url' in image['meta_single_page']:
                    url = image['meta_single_page']['original_image_url']
                    print('original image found:', url)
                elif 'large_image_url' in image['meta_single_page']:
                    url = image['meta_single_page']['large_image_url']
                    print('large image found:', url)
                elif 'medium_image_url' in image['meta_single_page']:
                    url = image['meta_single_page']['medium_image_url']
                    print('medium image found:', url)
                elif 'square_medium_image_url' in image['meta_single_page']:
                    url = image['meta_single_page']['square_medium_image_url']
                    print('square_medium image found:', url)
                else:
                    print('no image found :(')
                    print('skipping')
                    continue
            else:
                if 'large' in image['image_urls']:
                    url = image['image_urls']['large']
                    print('large image found:', url)
                elif 'medium' in image['image_urls']:
                    url = image['image_urls']['medium']
                    print('medium image found:', url)
                elif 'square_medium' in image['image_urls']:
                    url = image['image_urls']['square_medium']
                    print('square_medium image found:', url)
                else:
                    print('no image found :(')
                    print('skipping')
                    continue

            ext = url.split('.')[-1]
            filename = '{} - {}.{}'.format(
                image['id'],
                image['title']
                .replace('/', '_')
                .replace('\\', '_')
                .replace(':', '_')
                .replace('*', '_')
                .replace('?', '_')
                .replace('"', '_')
                .replace('<', '_')
                .replace('>', '_')
                .replace('|', '_'), ext)

            if os.path.isfile(os.path.join('images', filename)):
                print('duplicated filename detected')
                print('skipping')
                continue

            image_response = requests.get(url, headers={
                'Referer': 'https://app-api.pixiv.net/',
            }, stream=True)

            with open(os.path.join('images', filename), 'wb') as image_file:
                shutil.copyfileobj(image_response.raw, image_file)

    if halt:
        break

    if 'next_url' not in images or images['next_url'] is None:
        print('no further image found!')
        break
    else:
        print('next page found, keep downloading it')
        search_url = images['next_url']

try:
    input('press ENTER to close')
except:
    pass
