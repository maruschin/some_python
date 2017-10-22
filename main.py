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
import functools
import base64
from argparse import ArgumentParser, ArgumentTypeError
from datetime import datetime, timedelta


def func_run_logging(func):
    @functools.wraps(func)
    def func_log(*args, **kwargs):
        args_string = ', '.join([str(arg) for arg in args] + ['='.join((key, str(kwargs[key]))) for key in kwargs])
        logging.info("Run function: {0}({1})".format(func.__name__, args_string))
        return func(*args, **kwargs)
    return func_log


@func_run_logging
def main(url, branch, startdate, enddate):
    '''
    '''
    repository = '/'.join([n for n in url.split('/') if n not in ['', 'https:', 'github.com']])

    print(get_rate_limit())
    #print(get_top_contributors(repository, branch, startdate, enddate))
    #print(get_open_and_closed_pull_requests(repository, branch, startdate, enddate))
    #print(get_old_pull_requests(repository, branch, startdate, enddate))
    #print(get_open_and_closed_issues(repository, branch, startdate, enddate))
    print(get_old_issues(repository, branch, startdate, enddate))


@func_run_logging
def get_top_contributors(repository, branch, since, until):
    '''
    Самые активные участники. Таблица из 2 столбцов: login автора, количество его коммитов.
    Таблица отсортирована по количеству коммитов по убыванию. Не более 30 строк.
    '''
    API_URL = 'https://api.github.com/repos/{0}/commits'.format(repository)
    
    key_values = ['sha={0}'.format(branch), 'per_page=100']
    if since != None:
        key_values.append('='.join(['since', since.isoformat()]))
    if until != None:
        key_values.append('='.join(['until', until.isoformat()]))
    API_URL = '?'.join([API_URL, '&'.join(key_values)])

    contributors = dict()
    for response_json in get_resource(API_URL):
        for response_element in response_json:
            try:
                contributors[response_element['author']['login']] += 1
            except KeyError:
                contributors[response_element['author']['login']] = 1
            except TypeError:
                # Коммиты у кторых нет логина - не считаем
                pass
    contributors = sorted(contributors.items(), key=lambda it: it[1], reverse=True)
    return contributors[:30]


@func_run_logging
def get_open_and_closed_pull_requests(repository, branch, since, until):
    '''Количество открытых и закрытых pull requests.'''
    API_URL = 'https://api.github.com/repos/{0}/pulls'.format(repository)
    
    key_values = ['base={0}'.format(branch), 'per_page=100', 'state=all']
    API_URL = '?'.join([API_URL, '&'.join(key_values)])

    open_pull_requests, closed_pull_requests = 0, 0
    logging.info("Counting open and closed pull requests...")
    if until == None: until = datetime.now()
    if since == None: since = datetime.datetime(1900, 1, 1)
    for response_json in get_resource(API_URL):
        for response_element in response_json:
            created = datetime.strptime(response_element['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            if (since <= created and created <= until):
                if response_element['state']=='open':
                   open_pull_requests += 1
                else:
                  closed_pull_requests += 1
        logging.info("Open: {0}, closed: {1} pull requests...".format(str(open_pull_requests), str(closed_pull_requests)))
    return open_pull_requests, closed_pull_requests


@func_run_logging
def get_old_pull_requests(repository, branch, since, until):
    '''
    Количество "старых" pull requests. Pull requests считается старым, 
    если он не закрывается в течении 30 дней.
    '''
    API_URL = 'https://api.github.com/repos/{0}/pulls'.format(repository)
    
    key_values = ['base={0}'.format(branch), 'per_page=100', 'state=open']
    API_URL = '?'.join([API_URL, '&'.join(key_values)])

    old_pull_requests = 0
    old_date = datetime.now() - timedelta(days = 30)
    if until == None: until = datetime.now()
    if since == None: since = datetime(1900, 1, 1)
    for response_json in get_resource(API_URL):
        for response_element in response_json:
            created = datetime.strptime(response_element['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            if (since <= created and created <= until and created <= old_date):
                old_pull_requests += 1
        logging.info("Old: {0} pull requests...".format(str(old_pull_requests)))
    return old_pull_requests


@func_run_logging
def get_open_and_closed_issues(repository, branch, since, until):
    '''
    Количество открытых и закрытых issues.
    '''
    API_URL = 'https://api.github.com/repos/{0}/issues'.format(repository)
    
    key_values = ['base={0}'.format(branch), 'per_page=100', 'state=all']
    if since != None:
        key_values.append('='.join(['since', since.isoformat()]))
    API_URL = '?'.join([API_URL, '&'.join(key_values)])

    open_issues, closed_issues = 0, 0
    if until == None: until = datetime.now()
    for response_json in get_resource(API_URL):
        for response_element in response_json:
            created = datetime.strptime(response_element['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            if (created <= until):
                if response_element['state']=='open':
                    open_issues += 1
                if response_element['state']=='closed':
                    closed_issues +=1
        logging.info("Open issues: {0}; closed issues: {1}...".format(str(open_issues), str(closed_issues)))
    return open_issues, closed_issues


@func_run_logging
def get_old_issues(repository, branch, since, until):
    '''
    Количество "старых" issues. Issue считается старым, 
    если он не закрывается в течении 14 дней.
    '''
    API_URL = 'https://api.github.com/repos/{0}/issues'.format(repository)
    
    key_values = ['base={0}'.format(branch), 'per_page=100', 'state=open']
    if since != None:
        key_values.append('='.join(['since', since.isoformat()]))
    API_URL = '?'.join([API_URL, '&'.join(key_values)])

    old_issues = 0
    old_date = datetime.now() - timedelta(days = 14)
    if until == None: until = datetime.now()
    for response_json in get_resource(API_URL):
        for response_element in response_json:
            created = datetime.strptime(response_element['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            if (created <= until and created <= old_date):
                old_issues += 1
        logging.info("Old issues: {0}...".format(str(old_issues)))
    return  old_issues


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
def get_basic_auth(cache=[]):
    '''
    Get username and login from user and memorize it in cache attribute.
    It's black magic, but it works.
    '''
    if not cache:
        print('Enter login to access Github API:', end=' ')
        username = str(input())
        print('Enter password for {0}:'.format(username), end=' ')
        password = str(input())
    
        string = '%s:%s' % (username, password)
        basic_token = base64.b64encode(string.encode()).decode('utf-8')
        cache.append(basic_token)
    else:
        basic_token = cache[0]
    return ('Authorization', 'Basic %s' % basic_token)


@func_run_logging
def get_request(url, method):
    ''' Get request entity with basic auth '''
    request = urllib.request.Request(url=url, method=method)
    request.add_header('Accept', 'application/vnd.github.v3+json')
    request.add_header(*get_basic_auth())

    return request


@func_run_logging
def get_rate_limit():
    ''' Get rate limit '''
    url = 'https://api.github.com/rate_limit'
    request = get_request(url, 'GET')
    
    with urllib.request.urlopen(request) as res:
        response = res.read().decode('utf-8')
        logging.debug(res.headers)
        rate_limit = int(res.headers['X-RateLimit-Limit'])
        rate_remaining = int(res.headers['X-RateLimit-Remaining'])
        rate_reset = datetime.fromtimestamp(int(res.headers['X-RateLimit-Reset']))
    
    logging.info('Rate limit: {0}, remaining: {1}, reset: {2}'.format(str(rate_limit), str(rate_remaining), str(rate_reset)))
    return {'rate_limit': rate_limit, 'rate_remaining': rate_remaining, 'rate_reset': rate_reset}


@func_run_logging
def get_resource(url):
    ''' Get resources '''
    request = get_request(url, 'GET')

    with urllib.request.urlopen(request) as res:
        response = res.read().decode('utf-8')
        logging.debug(res.headers)
        rel = parse_headers_link(res.headers['Link']) if res.headers['Link'] != None else {'next': None}
    if rel['next'] == None:
        yield json.loads(response)
    else:
        yield json.loads(response)
        for i in range(rel['next']['page'],rel['last']['page']+1):
            REQUEST_URL = url + '&page=' + str(i)
            logging.debug(REQUEST_URL)
            request.full_url = REQUEST_URL
            with urllib.request.urlopen(request) as res:
                response = res.read().decode('utf-8')
            yield json.loads(response)


@func_run_logging
def valid_url(url):
    if re.match('^(https://)?github.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-]+/?$', url):
        return url
    else:
        msg = "Not a valid github URL: '{0}'".format(url)
        logging.error(msg)
        raise ArgumentTypeError(msg)


@func_run_logging
def valid_date(date):
    try:
        return datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        msg = "Not a valid date: '{0}'".format(date)
        logging.error(msg)
        raise ArgumentTypeError(msg)


if __name__ == "__main__":
    FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
    FILENAME = 'X:\OwnWork\PlayRix\example.log'
    logging.basicConfig(filename=FILENAME, format=FORMAT, level=logging.DEBUG)
    parser = ArgumentParser(description='Анализ репозитория github.')
    # URL публичного репозитория на github.com
    parser.add_argument('url', type = valid_url,
        help='The URL of the public repository on github.com')
    # Дата начала анализа. Если пустая, то неограничено.
    parser.add_argument('-s', '--startdate', type=valid_date, default=None,
        help='Дата начала анализа в формате YYYY-MM-DD')
    # Дата окончания анализа. Если пустая, то неограничено.
    parser.add_argument('-e', '--enddate', type=valid_date, default=None,
        help='Дата окончания анализа в формате YYYY-MM-DD')
    # Ветка репозитория. По умолчанию - master.
    parser.add_argument('-b', '--branch', type=str, default='master',
        help='Ветка репозитория. По умолчанию - master')
    #import doctest
    #doctest.testmod()
    main(**(vars(parser.parse_args())))
