#!/usr/bin/python

from urllib2 import urlopen, URLError
from BeautifulSoup import BeautifulSoup as BS
import os
from ConfigParser import ConfigParser
from thread_utils import thread_out_work

import logging as log
log.basicConfig(level=log.DEBUG,format="%(levelname)s: %(message)s")

channel_url = 'http://boards.4chan.org/%s/%s'
image_url = 'images.4chan.org/%s'

MULTI_THREAD = True
PAGES = 15

def get_channel_links(channel):
    log.debug('processing channel: %s' % channel)
    channel_links = set()
    for i in xrange(PAGES):
        log.debug('processing page: %s' % i)
        if i == 0: i = ''
        url = channel_url % (channel,i)
        try:
            html = urlopen(url).read()
        except Exception, ex:
            log.error('failed to download page %s %s :: %s',channel,i,ex)
            continue
        soup = BS(html)
        links = soup.findAll('a')
        for link in links:
            href = link.get('href')
            if href and image_url % channel in href:
                channel_links.add((channel,i,href))

    return list(channel_links)

def download_image(url,out_path,urls=None):
    if not os.path.exists(os.path.dirname(out_path)):
        os.mkdir(out_path)
    #name = url.rsplit('/',1)[-1]
    #local_path = os.path.abspath(os.path.join(out_path,name))
    local_path = out_path
    if os.path.exists(local_path):
        log.debug('skipping: %s',local_path)
        return (url,False)
    try:
        with file(local_path,'wb') as fh:
            log.debug('writing: %s',local_path)
            data = urlopen(url).read()
            if len(data) == 0:
                log.error('no data!')
            fh.write(data)
    except Exception, ex:
        log.error('failed to download: %s',ex)
        log.debug('deleting failed image: %s',local_path)
        os.path.unlink(local_path)
        if urls:
            urls.add(url)
        else:
            raise
        return (url,False)

    return (url,True)


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    log.debug('here: %s',here)
    config = ConfigParser()
    config.read(os.path.join(here,'to_pull.conf'))
    image_output_path = config.get('paths','images')
    log.debug('output_path: %s',image_output_path)

    threadout_args = []

    for section in [x for x in config.sections() if x.endswith('_channels')]:
        for channel, active in config.items(section):
            if eval(active):
                threadout_args.append((channel,))

    results = thread_out_work(threadout_args,get_channel_links,fake_it=not MULTI_THREAD, thread_percentage=1)

    threadout_args = []
    for channel_data in results:
        if not channel_data: continue
        for channel, page, link in channel_data:
            image_name = link.rsplit('/',1)[-1]
            out_path = os.path.join(image_output_path,channel,image_name)
            threadout_args.append((link,out_path))

    results = thread_out_work(threadout_args,
                              download_image,
                              fake_it=not MULTI_THREAD,
#                              fake_it=True,
                              thread_percentage=.05)

