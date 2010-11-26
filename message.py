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


class Message(object):

    keys_ =  ['id', 'text', 'date', 'year', 'month', 'day', 'hour', 'minute', 'second',
             'number of words', 'number of characters']

    @property
    def keys(self):
        return self.keys_

    def __init__(self, id_, text, date_):
        self.id = id_
        self.text = text
        self.date = date_

    def __repr__(self):
        return "%d - [%s] %s" % (
            self.id,
            self.date.strftime('%Y-%m-%d %H:%M:%s'),
            self.text
        )

    def prepare_data(self):
        return {
           'id': self.id,
            'text': self.text,
            'date': self.date,
            'year': self.date.year,
            'month': self.date.month,
            'day': self.date.day,
            'hour': self.date.hour,
            'minute': self.date.minute,
            'second': self.date.second,
            'number of words': len(self.text.split(' ')),
            'number of characters': len(self.text)
        }
