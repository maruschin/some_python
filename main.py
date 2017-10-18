import argparse
import urllib.request
import json
import re
from datetime import datetime


URL = 'https://api.github.com'

HEADER = (('Accept', 'application/vnd.github.v3+json'),)

request = urllib.request.Request(url=URL, data=None, method='GET')

# Добавляем заголовки в запрос
for head in HEADER:
    request.add_header(*head)


with urllib.request.urlopen(request) as f:
    #print(f)
    #print(dir(f))
    for a in f:
        foo = a.decode('utf-8')


buzz = json.loads(foo)

#print(buzz)

for b in buzz:
    pass
    #print(b, buzz[b])



def main(url, repository, startdate, enddate):
    print(url)
    print(repository)
    print(startdate)
    print(enddate)

def valid_url(url):
    if re.match('https://github.com/[a-z0-9-]+/[a-z0-9-]+/?$', url):
        return url
    else:
        msg = "Not a valid github URL: '{0}'.".format(url)
        raise argparse.ArgumentTypeError(msg)

def valid_date(date):
    try:
        return datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(date)
        raise argparse.ArgumentTypeError(msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Анализ репозитория github.')
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
    parser.add_argument('-r', '--repository', type=str, default = 'master',
        help='Ветка репозитория. По умолчанию - master')

    main(**(vars(parser.parse_args())))