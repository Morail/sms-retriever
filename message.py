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

    def __init__(self, m_id, text, date_):
        self.id = m_id
        self.text = text
        self.date = date_

    def __repr__(self):
        return "<Message(%s - [%s] %s)>" % (
            self.id,
            self.date.strftime('%Y-%m-%d %H:%M:%s'),
            self.clean_text
        )
        
    @property
    def clean_text(self):
        try:
            return self.text.encode('utf-8')
        except UnicodeDecodeError:
            return self.text
    
    @clean_text.setter
    def clean_text(self, value):
        self.clean_text = value.encode('utf-8')

