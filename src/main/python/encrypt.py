# -*- coding: utf-8 -*-
import sys
from Crypto.Hash import MD5
from Crypto.Cipher import Blowfish
from binascii import hexlify,unhexlify

desobj = Blowfish.new('0tvl7qZ2cOs7ai4B3tpe')

X='^'

def ask(data):
    return hexlify(desobj.encrypt(data + (8 - (len(data) % 8)) * X))

def tell(data):
    def reduce_func(x, y):
        if y != X:
            return x + y
        else:
            return x
    return reduce(reduce_func, desobj.decrypt(unhexlify(data.strip()))).strip()


#def tell(data, len):
#    if data:
#        return desobj.decrypt(data)[0:len]
#    else:
#        return None


if __name__ == '__main__':
    """
    -exxxxxx  encrypt file 
    -dxxxxxx  dycrypt file
    -oxxxxxx  output file
    """
    if len(sys.argv)!=2:
        sys.exit()

    encrypt = [x for x in sys.argv if x[:2] == '-e']
    decrypt = [x for x in sys.argv if x[:2] == '-d']
#    output  = [x for x in sys.argv if x[:2] == '-o']

#    if len(output)==0:
#        sys.exit()
#    else:
#        output=output[0][2:]

    if len(encrypt)>0:
        f = encrypt[0][2:]
        do = ask
    elif len(decrypt)>0:
        f = decrypt[0][2:]
        do = tell
    else:
        do = None

#    o = open(output,'w+b')
    if do is not None:
        for data in open(f).readlines():
            print do(data)

#    o.close()
