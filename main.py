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
from urllib.error import HTTPError
import json
import re
import logging
from argparse import ArgumentParser, ArgumentTypeError
from datetime import datetime


def func_run_logging(func):
    def func_log(*args, **kwargs):
        args_string = ', '.join(list(args) + ['='.join((key, str(kwargs[key]))) for key in kwargs])
        logging.info("Run function: {0}({1})".format(func.__name__, args_string))
        return func(*args, **kwargs)
    return func_log


@func_run_logging
def main(url, branch, startdate, enddate):
    '''
    '''
    repository = '/'.join([n for n in url.split('/') if n not in ['', 'https:', 'github.com']])
    #print(get_top_contributors(repository))
    #print(get_open_and_closed_pull_requests(repository))


@func_run_logging
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


@func_run_logging
def get_open_and_closed_pull_requests(repository):
    '''Количество открытых и закрытых pull requests.'''
    API_URL = 'https://api.github.com/repos/{0}/pulls?state=all'.format(repository)
    open_pull_requests = 0
    closed_pull_requests = 0
    logging.info("Counting open and closed pull requests...")
    for response_json in get_resource(API_URL):
        for response_element in response_json:
            if response_element['state']=='open':
                open_pull_requests += 1
            else:
                closed_pull_requests += 1
        logging.info("Open: {0}, closed: {1} pull requests...",format(open_pull_requests, closed_pull_request))
    return open_pull_requests, closed_pull_requests


@func_run_logging
def parse_headers_link(headers_link):
    ''' 
    >>> parse_headers_link(
    ... '<https://api.github.com/repositories/1579990/pulls?page=2>; rel="next", ' +
    ... '<https://api.github.com/repositories/1579990/pulls?page=4>; rel="last"')
    {'next': {'page': 2}, 'last': {'page': 4}}
    >>> parse_headers_link(
    ... '<https://api.github.com/repositories/1579990/pulls?state=all&page=2>; rel="next", ' +
    ... '<https://api.github.com/repositories/1579990/pulls?state=all&page=116>; rel="last"')
    {'next': {'state': 'all', 'page': 2}, 'last': {'state': 'all', 'page': 116}}
    '''
    logging.debug(headers_link)
    rels = dict()
    for i in headers_link.split(','):
        uri, rel = i.split(';')
        rel_value = (re.sub('"', '', rel).split('='))[1]
        key_values = dict()
        for key_value in re.sub('>$', '', re.sub('^<[\S]+\?','', uri.strip())).split('&'):
            key, value = key_value.split('=')
            try:
                key_values[key] = int(value)
            except ValueError:
                key_values[key] = value
        rels[rel_value] = key_values
    logging.debug(rels)
    return rels


@func_run_logging
def get_resource(url):
    request = urllib.request.Request(url=(url), method='GET')
    request.add_header('Accept', 'application/vnd.github.v3+json')
    with urllib.request.urlopen(request) as res:
        response = res.read().decode('utf-8')
        rel = parse_headers_link(res.headers['Link'])
    if rel['next'] == None:
        logging.debug("some")
        return json.loads(response)
    else:
        logging.debug("some")
        yield json.loads(response)
    for i in range(rel['next']['page'],rel['last']['page']+1):
        request = urllib.request.Request(url=(url + '?page=' + str(i)), method='GET')
        request.add_header('Accept', 'application/vnd.github.v3+json')
        with urllib.request.urlopen(request) as res:
            response = res.read().decode('utf-8')
        logging.debug("some")
        yield json.loads(response)


@func_run_logging
def valid_url(url):
    if re.match('^(https://)?github.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-]+/?$', url):
        return url
    else:
        msg = "Not a valid github URL: '{0}'.".format(url)
        raise ArgumentTypeError(msg)


@func_run_logging
def valid_date(date):
    try:
        return datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(date)
        raise ArgumentTypeError(msg)


if __name__ == "__main__":
    FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
    FILENAME = 'X:\OwnWork\PlayRix\example.log'
    logging.basicConfig(filename=FILENAME, format=FORMAT, level=logging.DEBUG)
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