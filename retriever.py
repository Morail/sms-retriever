#!/usr/bin/env python

##########################################################################
#                                                                        #
#  This program is free software; you can redistribute it and/or modify  #
#  it under the terms of the GNU General Public License as published by  #
#  the Free Software Foundation; version 2 of the License.               #
#                                                                        #
#  This program is distributed in the hope that it will be useful,       #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#  GNU General Public License for more details.                          #
#                                                                        #
##########################################################################


import sys
import urllib2 as ul
import re
import htmlentitydefs

from datetime import datetime
from BeautifulSoup import BeautifulSoup
from twiggy import log
from twiggy_setup import twiggy_setup


class Retriever(object):
    
    def __init__(self, url, mpp=1, df='%y/%m/%d', regex='.'):
        self.top = mpp
        self.date_format = df
        self.counter, self.page_start = 0, 0
        self.base_url = url
        self.messages = {}
        self.re = regex
        self._log = log.name('process')


    def process(self):
    
        while True:
            url = "%s?top=%d&pagestart=%d" % (self.base_url, self.top,
                                              self.page_start)

            self._log.info('reading from url {url}', url=url)
            html = BeautifulSoup(ul.urlopen(url))
    
            ## break while loop
            if not html:
                self._log.fields(Messages=self.counter).debug('Nothing returned from the given url, stopping this process')
                break
    
            list_ = html.findAll('div', id=re.compile(self.re))
    
            if not len(list_):
                self._log.fields(Messages=self.counter).debug('Nothing returned from the given url, stopping this process')
                break
    
            for d in list_:
                id = d['id'].split('_')[-1]

                if not id or id in self.messages:
                    continue

                date_ = datetime.strptime(d.strong.string, self.date_format)
                text= unescape(d.div.contents[-1])
    
                self.messages[id] = (text, date_)

                ## updating message counter
                self.counter += 1
    
            ## incrementing pagestart
            self.page_start += self.top
    
        self._log.info('Messages found: {}', self.counter)



## Thanks to: http://effbot.org/zone/re-sub.htm#unescape-html
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)


def main():

    ## Twiggy logger setup
    twiggy_setup()
    log.name('main').info('-------------------- START --------------------')

    url = 'http://www.rtl.it/ajaxreturn/sms_list.php'
    df = '%d.%m.%Y %H:%M:%S'
    regex = 'sms_\d+'
    
    r = Retriever(url=url, mpp=15, regex=regex, df=df)
    r.process()
    log.name('main').info('-------------------- STOP --------------------')

if __name__ == "__main__":
    main()

