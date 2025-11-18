'''
Created on 20251112
Update on 20251114
@author: Eduardo Pagotto
'''

class ExceptRPC(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
