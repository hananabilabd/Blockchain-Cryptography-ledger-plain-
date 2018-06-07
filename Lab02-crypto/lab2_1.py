from random import randint, random, shuffle, seed #, choices
from ecdsa import SigningKey, VerifyingKey, BadSignatureError
from binascii import hexlify,unhexlify
from hashlib import sha256
from pprint import pprint
from collections import OrderedDict
import unittest
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
#!pip install ecdsa
class KeyGen:
    @classmethod
    def genKeyPair(self):
        # private_key = rsa.generate_private_key(public_exponent=65537,key_size=2048,backend=default_backend())
        # public_key = private_key.public_key()
        sk = SigningKey.generate()  # private
        vk = sk.get_verifying_key()  # public
        h1 = sk.to_pem().decode()
        h2 = vk.to_pem().decode()
        private_h = hexlify(h1)
        public_h = hexlify(h2)



        return {"privKey": private_h, "pubKey": public_h}

    def __generate_keys(self, users):
        return {k: self.genKeyPair() for k in users}

    def get_keys(self):
        return self.__users_keys

    def __init__(self, users):
        self.__users_keys = self.__generate_keys(users)
        self.__users_keys['coinbase'] = self.genKeyPair()


t = KeyGen.genKeyPair()
print t['privKey']


class TxUtils:
    @classmethod
    def serializeTx(self, tx):
        # this could be achived with json.dumps but it will not guarantee order
        # tx=json.dumps(OrderedDict(tx))
        # a = OrderedDict(tx)
        # json_format = json.dumps(a.items())
        # tx=OrderedDict(json.loads(json_format))
        return ("{fr:%s, to:%s, amount:%s }" % (tx['fr'], tx['to'], tx['amount'])).encode()

    @classmethod
    def signTx(self, tx, privateKeyHex):  # private

        print tx
        #### added you code here
        #### you should hash the tx then using the publicKeyHex && SigningKey Class && hashed_tx
        #### to generate signature of the transaction and return it as hex
        tx_ser = self.serializeTx(tx)
        h = sha256(tx_ser)
        d = h.digest()
        #x = h.hexdigest()
        sk = SigningKey.from_string(unhexlify(privateKeyHex))

        # sk = SigningKey.from_pem(publicKeyHex)
        signature = sk.sign_deterministic(d)
        hy = hexlify(signature)
        return hy

    @classmethod
    def verifyTx(self, tx, publicKeyHex):
        print tx
        try:


            x = {'amount': tx['amount'], 'fr': tx['fr'], 'to': tx['to']}
            tx_ser = self.serializeTx(x)
            h = sha256(tx_ser)
            d = h.digest()
            #print tx_ser
            #signature = self.signTx(tx, publicKeyHex)
            signature =tx['sig']
            #vk = .get_verifying_key()
            vk=VerifyingKey.from_string(unhexlify(publicKeyHex))
            #vk.verify(bytes.fromhex(signature), tx_ser)
            vk.verify(unhexlify(signature), d)
            print("good sig")
            return True
        except BadSignatureError as e:
            print("bad sig")
            return False
            #### added you code here
            #### using publicKey of user, check the signature of the transaction has been signed by the private key of user
            #### and return true if the signature of the transaction is valid , False otherwise
            #### you will have to handle the case of BadSignatureError by using try, except


# b={ "name": "Hannon", "city": "Cairo", "status": "%s", "country": "%s" }
# x = {'amount': 1962, 'fr': 'coinbase', 'to': 'Eula Zahar'}
# g=TxUtils.serializeTx(x)
# print g

class TestingTxUtils(unittest.TestCase):
    def setUp(self):
        self.TxUtils = TxUtils()
        self.keys = {
            'Eula Zahar': {'privKey': b'9fa53211241764d768ccfc5807638e37e6589f38e4eb2758',
                           'pubKey': b'f6f2a561c6c323728b736940098b7bb042258eb25e6052d0dcc46d8174390fc2abeb15c2ffd7a569fb8b742da95f52fd'},

            'coinbase': {'privKey': b'2b762ffc63a75f87cb7d321a62ee9e0ee8d5374352a35b12',
                         'pubKey': b'301dd8c64346bffef813ad4ece38ce4fa75ef2aa4064661da49a75357a2f520d801b7569efcf3db35aa0d9b45cd090f1'}
        }

        self.tx = {'amount': 1962, 'fr': 'coinbase', 'to': 'Eula Zahar'}
        self.signedTx = {'amount': 1962, 'fr': 'coinbase', 'to': 'Eula Zahar',
                         'sig': b'52df468cd2c99f41b0663fdac2cb361ee6971357b7dfe619e88e7137845f771e52f124c541e62948bfbb0c6d045d59c9'}

    def test_signTx_True(self):
        self.assertEqual(self.TxUtils.signTx(self.tx, self.keys['coinbase']['privKey']), self.signedTx['sig'])

    def test_signTx_False(self):
        self.assertNotEqual(self.TxUtils.signTx(self.tx, self.keys['Eula Zahar']['privKey']), self.signedTx['sig'])

    def test_verifyTx_True(self):
        self.assertEqual(self.TxUtils.verifyTx(self.signedTx, self.keys['coinbase']['pubKey']), True)

    def test_verifyTx_False(self):
        self.assertEqual(self.TxUtils.verifyTx(self.signedTx, self.keys['Eula Zahar']['pubKey']), False)



suite = unittest.TestLoader().loadTestsFromTestCase(TestingTxUtils)
unittest.TextTestRunner().run(suite)
