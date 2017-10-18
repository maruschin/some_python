import urllib.request
import json


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




if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Анализ репозитория github.')
    # URL публичного репозитория на github.com
    parser.add_argument('URL', metavar='U', type=str, help='URL публичного репозитория на github.com')
    # Дата начала анализа. Если пустая, то неограничено.
    parser.add_argument('--sd', metavar='S', type=str, help='Дата начала анализа. Если пустая, то неограничено')
    # Дата окончания анализа. Если пустая, то неограничено.
    parser.add_argument('--ed', metavar='E', type=str, help='Дата окончания анализа. Если пустая, то неограничено')
    # Ветка репозитория. По умолчанию - master.
    parser.add_argument('--repo', metavar='R', type=str, help='Ветка репозитория. По умолчанию - master')

    args = parser.parse_args()
    print(args)