'''
Провести анализ репозитория, используя REST API Github.
Результат анализа выводятся в stdout.
Необходимо вывести такие результаты:

  * Самые активные участники. Таблица из 2 столбцов: login автора, количество его коммитов.
    Таблица отсортирована по количеству коммитов по убыванию. Не более 30 строк.

  * Количество открытых и закрытых pull requests.

  * Количество "старых" pull requests. Pull requests считается старым, 
    если он не закрывается в течении 30 дней.

  * Количество открытых и закрытых issues.

  * Количество "старых" issues. Issue считается старым, 
    если он не закрывается в течении 14 дней.
'''

import urllib.request
import json
import re
from argparse import ArgumentParser, ArgumentTypeError
from datetime import datetime


def main(url, branch, startdate, enddate):
    '''
    '''
    repository = '/'.join([n for n in url.split('/') if n not in ['', 'https:', 'github.com']])
    print(get_top_contributors(repository))


def get_top_contributors(repository):
    API_URL = 'https://api.github.com/repos/{0}/stats/contributors'.format(repository)
    response_json = get_resource(API_URL)
    contributors = []
    for response_element in response_json:
        contributors.append((response_element['author']['login'], response_element['total']))
    contributors.sort(key=lambda el: el[1], reverse=True)
    return contributors[:30]


def get_resource(url):
    request = urllib.request.Request(url=url, method='GET')
    request.add_header('Accept', 'application/vnd.github.v3+json')
    with urllib.request.urlopen(request) as res:
        response = res.read().decode('utf-8')
    return json.loads(response)


def valid_url(url):
    if re.match('^(https://)?github.com/[a-z0-9-]+/[a-z0-9-]+/?$', url):
        return url
    else:
        msg = "Not a valid github URL: '{0}'.".format(url)
        raise ArgumentTypeError(msg)


def valid_date(date):
    try:
        return datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(date)
        raise ArgumentTypeError(msg)


if __name__ == "__main__":
    parser = ArgumentParser(description='Анализ репозитория github.')
    # URL публичного репозитория на github.com
    parser.add_argument('url', type=valid_url,
        help='The URL of the public repository on github.com')
    # Дата начала анализа. Если пустая, то неограничено.
    parser.add_argument('-s', '--startdate', type=valid_date,
        help='Дата начала анализа в формате YYYY-MM-DD')
    # Дата окончания анализа. Если пустая, то неограничено.
    parser.add_argument('-e', '--enddate', type=valid_date,
        help='Дата окончания анализа в формате YYYY-MM-DD')
    # Ветка репозитория. По умолчанию - master.
    parser.add_argument('-b', '--branch', type=str, default = 'master',
        help='Ветка репозитория. По умолчанию - master')

    main(**(vars(parser.parse_args())))