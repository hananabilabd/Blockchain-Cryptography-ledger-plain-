from random import randint, random, shuffle, seed #, choices
from ecdsa import SigningKey, VerifyingKey, BadSignatureError
from binascii import hexlify,unhexlify
from hashlib import sha256
from pprint import pprint
import unittest
import json


def serializeTx( tx):
    # this could be achived with json.dumps but it will not guarantee order
    return tx.encode()

tx_ser = serializeTx("hanna")
h = sha256(tx_ser)
d = h.digest()
##sk ==> private key
sk = SigningKey.from_string(unhexlify("f697f3ad18b3397dcb45e7e8430d9f12684ed0d5237ad56e"))
signature = sk.sign_deterministic(d)
hy = hexlify(signature)

try:


    tx_ser = serializeTx("hanna")
    h = sha256(tx_ser)
    d = h.digest()

    signature = hy
    ## vk ====> Public key
    vk = VerifyingKey.from_string(unhexlify("2c999df45c0a8397831007cd5df6c943578f073169124343df336ef92a41e3259e7646c908c0f09bca9840344c4be8e0"))

    vk.verify(unhexlify(signature), d)
    print("good sig")

except BadSignatureError as e:
    print("bad sig")

print d