import sys


def add_lib_to_path(zip):
    if len([x for x in sys.path if x == zip]) == 0:
        sys.path.insert(0, zip)


#from Crypto.Hash import MD5
#md5 = MD5.new(open('seed.txt', 'r').read())
#from Crypto.Cipher import Blowfish
#desobj = Blowfish .new(md5.hexdigest())
#
#
#def ask(data):
#    return desobj.encrypt(data + (8 - (len(data) % 8)) * 'X')
#
#
#def tell(data):
#    def reduce_func(x, y):
#        if y != 'X':
#            return x + y
#        else:
#            return x
#    return reduce(reduce_func, desobj.decrypt(data))
#
#
#def tell(data, len):
#    if data:
#        return desobj.decrypt(data)[0:len]
#    else:
#        return None


class ScrapError(Exception):
    def __init__(self,  msg):
        self.msg = msg
