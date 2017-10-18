'''
Author: Eugene Maruschin (Evgenii Marushchenko | Евгений Марущенко)
Source: https://github.com/maruschin/some_python

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
import logging
from argparse import ArgumentParser, ArgumentTypeError
from datetime import datetime


def main(url, branch, startdate, enddate):
    '''
    '''
    repository = '/'.join([n for n in url.split('/') if n not in ['', 'https:', 'github.com']])
    #print(get_top_contributors(repository))
    print(get_open_and_closed_pull_requests(repository))


def get_top_contributors(repository):
    '''
    Самые активные участники. Таблица из 2 столбцов: login автора, количество его коммитов.
    Таблица отсортирована по количеству коммитов по убыванию. Не более 30 строк.
    '''
    API_URL = 'https://api.github.com/repos/{0}/stats/contributors'.format(repository)
    response_json = get_resource(API_URL)
    contributors = []
    for response_element in response_json:
        contributors.append((response_element['author']['login'], response_element['total']))
    contributors.sort(key=lambda el: el[1], reverse=True)
    return contributors[:30]


def get_open_and_closed_pull_requests(repository):
    '''Количество открытых и закрытых pull requests.'''
    API_URL = 'https://api.github.com/repos/{0}/pulls'.format(repository)
    open_pull_requests = 0
    for response_json in get_resource(API_URL):
        for response_element in response_json:
            open_pull_requests +=1
    return open_pull_requests
    #return open_pull_requests, close_pull_requests


def parse_header_links(header_links):
    ''' 
    >>> parse_header_links(
    ... '<https://api.github.com/repositories/1579990/pulls?page=2>; rel="next", ' +
    ... '<https://api.github.com/repositories/1579990/pulls?page=4>; rel="last"')
    {'next': {'page': 2}, 'last': {'page': 4}}
    '''
    logging.info('Running parse_header_links function')
    logging.debug(header_links)
    rel = dict()
    for i in header_links.split(','):
        foo = i.split(';')
        page = re.sub('>$', '', re.sub('^<[\S]+\?','', foo[0].strip())).split('=')
        rel_value = (re.sub('"', '', foo[1]).split('='))[1]
        rel[rel_value] = {page[0]: int(page[1])}
    logging.debug(rel)
    return rel


def get_resource(url):
    request = urllib.request.Request(url=(url), method='GET')
    request.add_header('Accept', 'application/vnd.github.v3+json')
    with urllib.request.urlopen(request) as res:
        response = res.read().decode('utf-8')
        rel = parse_header_links(res.headers['Link'])
    if rel['next'] == None:
        return json.loads(response)
    else:
        yield json.loads(response)
    for i in range(rel['next']['page'],rel['last']['page']+1):
        request = urllib.request.Request(url=(url + '?page=' + str(i)), method='GET')
        request.add_header('Accept', 'application/vnd.github.v3+json')
        with urllib.request.urlopen(request) as res:
            response = res.read().decode('utf-8')
        yield json.loads(response)


def valid_url(url):
    if re.match('^(https://)?github.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-]+/?$', url):
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
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
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
    #import doctest
    #doctest.testmod()
    main(**(vars(parser.parse_args())))
