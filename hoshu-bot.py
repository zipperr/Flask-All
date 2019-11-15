# -*- coding: utf-8 -*-
from urllib.parse import urlencode
from http.cookiejar import CookieJar
import re
import urllib.request, urllib.error


class Error(Exception):
    pass


class Write2chException(Error):
    pass


UA = 'Monazilla/1.00 hoshu-bot.py/0.01'
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
opener.addheaders = [('User-Agent', UA)]


def getabouturl(url):
    return re.search(r'http://([\w.]+)/test/read[.]cgi/(\w+)/(\d+)/', url).groups()


def write(url, message, name='', mail='sage'):
    host, board_key, thread_key = getabouturl(url)
    postto   = 'http://{host}/test/bbs.cgi'.format(host=host)
    postdata = dict(
        bbs = board_key,
        key = thread_key,
        FROM = name.encode('sjis'),
        mail = mail,
        MESSAGE = message.encode('sjis'),
        submit = u'書き込む'.encode('sjis'),
        time = 1,
        tepo = 'don',
    )
    params = urlencode(postdata)

    request = urllib2.Request(postto, params, {'Referer': url})

    while True:
        reader = opener.open(request)
        cont = unicode(reader.read(), 'sjis')
        if u'書きこみました' in cont or u'2ch_X:true' in cont:
            return
        elif u'2ch_X:false' in cont:
            continue
        elif u'書き込み確認' in cont or u'2ch_X:cookie' in cont:
            continue
        else:
            raise Write2chException(cont)


def main():
    import sys
    import time
    import httplib2

    # url = sys.argv[1]
    url ='http://egg.5ch.net/test/read.cgi/ffo/1500024397/'
    mes = u'ほしゅ'

    host, board_key, thread_key = getabouturl(url)
    daturl = 'http://{host}/{board_key}/dat/{thread_key}.dat'.format(host=host, board_key=board_key, thread_key=thread_key)
    print(daturl)
    lastmod = opener.open(daturl).headers['Last-Modified']
    request = urllib.request.Request(daturl)
    request.add_header('If-Modified-Since', lastmod)

    while True:
        try:
            reader = opener.open(request)
            code = reader.code
            lastmod = reader.headers['Last-Modified']
            request.add_header('If-Modified-Since', lastmod)
        except urllib.error.HTTPError as e:
            code = e.code
        if code == httplib2.OK:
            print('sleeping...')
            time.sleep(60 * 15)
        elif code == httplib2.NOT_MODIFIED:
            write(url, mes)


if __name__ == '__main__':
    main()
