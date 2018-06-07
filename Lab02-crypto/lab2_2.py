from random import randint, random, shuffle, seed #, choices
from ecdsa import SigningKey, VerifyingKey, BadSignatureError
from binascii import hexlify,unhexlify
from hashlib import sha256
from pprint import pprint
import unittest
import json


class KeyGen:
    @classmethod
    def genKeyPair(self):
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


class TxUtils:
    @classmethod
    def serializeTx(self, tx):
        # this could be achived with json.dumps but it will not guarantee order
        return ("{fr:%s, to:%s, amount:%s }" % (tx['fr'], tx['to'], tx['amount'])).encode()

    @classmethod
    def signTx(self, tx, privateKeyHex):
        #if tx['fr']=='coinbase':
        tx_ser = self.serializeTx(tx)
        h = sha256(tx_ser)
        d = h.digest()
        # x = h.hexdigest()
        sk = SigningKey.from_string(unhexlify(privateKeyHex))

        # sk = SigningKey.from_pem(publicKeyHex)
        signature = sk.sign_deterministic(d)
        hy = hexlify(signature)
        return hy


    @classmethod
    def verifyTx(self, tx, publicKeyHex):

        try:

            x = {'amount': tx['amount'], 'fr': tx['fr'], 'to': tx['to']}
            tx_ser = self.serializeTx(x)
            h = sha256(tx_ser)
            d = h.digest()
            # print tx_ser
            # signature = self.signTx(tx, publicKeyHex)
            signature = tx['sig']
            # vk = .get_verifying_key()
            vk = VerifyingKey.from_string(unhexlify(publicKeyHex))
            # vk.verify(bytes.fromhex(signature), tx_ser)
            vk.verify(unhexlify(signature), d)
            print("good sig")
            return True
        except BadSignatureError as e:
            print("bad sig")
            return False



class Ledger:
    def __init__(self, keys):
        self.balances = {}
        self.stats = {"n_tx": 0,  ## Total Number of transactions
                      "n_coin_tx": 0,  ## Total Number of transactions that 'coinbase' is the sender( fr )
                      "n_valid_tx": 0,  ## Total Number of transactions that are valid and
                      ## the sender(fr) is not 'coinbase'
                      "n_invalid_to_tx": 0,  ## Total Number of transactions that are not valid because the reciver(to)
                      ## is 'coinbase'
                      "n_invalid_neg_amnt": 0,
                      ## Total Number of transactions that are not valid because the amount of trans.
                      ## was negative
                      "n_invalid_fr_tx": 0,  ## Total Number of transactions that are not valid because
                      ## the sender(fr) does not have balance
                      "n_invalid_nofund_tx": 0,  ## ## Total Number of transactions that are not valid because
                      ## the amount of trans. is bigger than the balance of the sender(fr)
                      "n_invalid_no_sig_tx": 0,  ## ## Total Number of transactions that were not valid because
                      ## the sig  of trans. is empty
                      "n_invalid_bad_sign_tx": 0  ## ## Total Number of transactions that are not valid because
                      ## the sig  of trans. is not from the sender'fr'
                      }
        self.keys = keys
        self.TxUtil = TxUtils()

    def validate_transaction(self, tx):

        # True Cases
        if (tx['fr'] == 'coinbase' ) and (tx['amount'] >= 0 ) and not (tx['sig'] == '') and (self.TxUtil.signTx(tx,self.keys['coinbase']['privKey'])== tx['sig'] or self.TxUtil.verifyTx(tx, self.keys[tx['fr']]['pubKey']) == True):
            self.stats['n_tx'] += 1
            self.stats['n_coin_tx'] += 1
            return True
        elif (tx['fr'] in self.balances) and (tx['amount'] <= self.balances[tx['fr']]) and (tx['amount'] >= 0) and not (tx['to'] == 'coinbase') and not (tx['sig'] == '')and (self.TxUtil.signTx(tx,self.keys['coinbase']['privKey'])== tx['sig'] or self.TxUtil.verifyTx(tx, self.keys[tx['fr']]['pubKey']) == True ):

            self.stats['n_tx'] += 1
            self.stats['n_valid_tx'] += 1
            return True

        # False Cases
        # (if not Elif because you don't stated that it couldn't be more than one False Case in the False transaction)


        if tx['to'] == 'coinbase':
            self.stats['n_tx'] += 1
            self.stats['n_invalid_to_tx'] += 1
            # return False

        elif not  tx['fr'] == 'coinbase':
            if tx['amount'] > self.balances[tx['fr']]  :
                self.stats['n_tx'] += 1
                self.stats['n_invalid_nofund_tx'] += 1

        elif (tx['fr'] not in self.balances )and not ( tx['fr'] == 'coinbase'):
            self.stats['n_tx'] += 1
            self.stats['n_invalid_fr_tx'] += 1
            return False

        if tx['amount'] < 0:
            self.stats['n_tx'] += 1
            self.stats['n_invalid_neg_amnt'] += 1
            # return False

        if tx['sig'] == '':
            self.stats['n_tx'] += 1
            self.stats['n_invalid_no_sig_tx'] += 1
        elif self.TxUtil.signTx(tx,self.keys[tx['fr']]['privKey']) !=tx['sig'] or self.TxUtil.verifyTx(tx, self.keys[tx['fr']]['pubKey']) == False:
            self.stats['n_tx'] += 1
            self.stats['n_invalid_bad_sign_tx'] += 1

            # return False

        return False


    def execute_transaction(self, tx):

        if self.validate_transaction(tx) == True:
            print tx
            if tx['fr'] == 'coinbase' and tx['amount'] >= 0:
                if tx['to'] not in self.balances :
                    self.balances[tx['to']] = 0
                print 'TX NEWCOIN OK:', tx['fr']
                print tx['to'], self.balances[tx['to']]
                # update self.balances
                self.balances[tx['to']] += tx['amount']
                print tx['amount'], "-->", tx['to']
                print (tx['to'], self.balances[tx['to']])
            elif tx['fr'] in self.balances and tx['amount'] <= self.balances[tx['fr']]:
                if tx['to'] not in self.balances:
                    self.balances[tx['to']] = 0
                print 'TX OK'
                print '--before--'
                print (tx['fr'], self.balances[tx['fr']])
                print (tx['to'], self.balances[tx['fr']])
                print '----------'
                # update self.balances
                self.balances[tx['fr']] -= tx['amount']
                self.balances[tx['to']] += tx['amount']
                print  tx['fr'], '-- ', tx['amount'], '-->', tx['to']
                print '--after--'
                print (tx['fr'], self.balances[tx['fr']])
                print (tx['fr'], self.balances[tx['to']])

        # elif self.validate_transaction(tx['fr'], tx['to'], tx['amount']) == False:
        else:
            print tx
            # print 'tx is invalid'
            if tx['to'] == 'coinbase':
                print 'reciver(to) is equal to coinbase '
            elif tx['amount'] < 0:
                print 'TX NEGATIVE AMOUNT', tx['amount']
            elif tx['fr'] not in self.balances:
                print "sender(fr) does not have an account (NOT in the balance dictionary) "

            elif tx['amount'] > self.balances[tx['fr']]:

                print 'the balance of', tx['fr'], 'is equal to', self.balances[tx['fr']]
                print 'TX NO FUNDS', self.balances[tx['fr']] - tx['amount']
            elif self.TxUtil.signTx(tx, self.keys[tx['fr']]['privKey']) != tx['sig']:
                print 'No the Right Signature'

        print "==================================================="




class TestingLedger(unittest.TestCase):
    def setUp(self):
        self.keys_decode = json.load(open('keys.json'))
        self.signedTxs_decode = json.load(open('signed_transactions.json'))
        self.keys = dict(
            map(lambda kv: (kv[0], {'pubKey': kv[1]['pubKey'].encode(), 'privKey': kv[1]['privKey'].encode()}),
                self.keys_decode.items()))
        self.signedTxs = list(
            map(lambda x: {'fr': x['fr'], 'to': x['to'], 'sig': x['sig'].encode(), 'amount': x['amount']},
                self.signedTxs_decode))
        self.ledger = Ledger(self.keys)

    def test_validate_transaction_valid_TX_NEWCOIN_OK(self):
        self.assertEqual(self.ledger.validate_transaction(self.signedTxs[0]), True)
        self.assertEqual(self.ledger.stats['n_coin_tx'], 1)

    def test_validate_transaction_invalid_TX_NO_SIGNATURE(self):
        self.assertEqual(self.ledger.validate_transaction({'amount': 100, 'fr': 'coinbase', 'to': 'Eula Zahar', 'sig': ''}), False)
        self.assertEqual(self.ledger.stats['n_invalid_no_sig_tx'], 1)

    def test_validate_transaction_invalid_NO_FUNDS(self):
        pprint(self.signedTxs[3])
        pprint(self.signedTxs[11])

        self.ledger.execute_transaction(self.signedTxs[3])
        self.assertEqual(self.ledger.validate_transaction(self.signedTxs[11]), False)
        self.assertEqual(self.ledger.stats['n_invalid_nofund_tx'], 1)

    def test_validate_transaction_valid(self):
        self.ledger.execute_transaction(self.signedTxs[0])
        self.assertEqual(self.ledger.validate_transaction(self.signedTxs[13]), True)
        self.assertEqual(self.ledger.stats['n_valid_tx'], 1)
        self.assertEqual(self.ledger.stats['n_tx'], 2)

    def test_validate_transaction_valid_TX_NEWCOIN_OK_2(self):
        tx = {'amount': 0, 'fr': 'coinbase', 'to': 'Eula Zahar'}
        tx["sig"] = TxUtils.signTx(tx, self.keys[tx['fr']]['privKey'])
        self.assertEqual(self.ledger.validate_transaction(tx), True)
        self.assertEqual(self.ledger.stats['n_coin_tx'], 1)

    def test_validate_transaction_invalid_TX_NEGATIVE_AMOUNT(self):
        self.ledger.execute_transaction(self.signedTxs[0])
        tx = {'amount': -11, 'fr': 'Eula Zahar', 'to': 'Leslie Collingsworth'}
        tx["sig"] = TxUtils.signTx(tx, self.keys[tx['fr']]['privKey'])
        self.assertEqual(self.ledger.validate_transaction(tx), False)
        self.assertEqual(self.ledger.stats['n_invalid_neg_amnt'], 1)

    def test_validate_transaction_invalid_TX_BAD_TO(self):
        self.ledger.execute_transaction(self.signedTxs[0])
        tx = {'amount': 11, 'fr': 'Eula Zahar', 'to': 'coinbase'}
        tx["sig"] = TxUtils.signTx(tx, self.keys[tx['fr']]['privKey'])
        self.assertEqual(self.ledger.validate_transaction(tx), False)
        self.assertEqual(self.ledger.stats['n_invalid_to_tx'], 1)

    def test_execute_transaction_valid(self):
        self.assertEqual(self.ledger.balances, {})
        self.ledger.execute_transaction(self.signedTxs[0])
        self.assertEqual(self.ledger.balances['Eula Zahar'], 1962)
        self.assertEqual(self.ledger.stats['n_coin_tx'], 1)

    def test_execute_transaction_invalid__BAD_SIGNATURE(self):
        self.assertEqual(self.ledger.balances, {})
        tx = {'amount': 100, 'fr': 'coinbase', 'to': 'Leslie Collingsworth'}
        tx["sig"] = TxUtils.signTx(tx, self.keys[tx['to']]['privKey'])
        self.ledger.execute_transaction(tx)
        self.assertEqual('Leslie Collingsworth' in self.ledger.balances, False)
        self.assertEqual(self.ledger.stats['n_invalid_bad_sign_tx'], 1)

    def test_execute_transaction_invalid_NO_FUNDS(self):
        self.assertEqual(self.ledger.balances, {})

        self.ledger.execute_transaction(self.signedTxs[3])
        self.ledger.execute_transaction(self.signedTxs[11])
        #self.ledger.execute_transaction(self.signedTxs[10])
        self.assertEqual(self.ledger.balances['Sophie Hardin'], 1655)
        self.assertEqual(self.ledger.stats['n_invalid_nofund_tx'], 1)
        self.assertEqual(self.ledger.stats['n_coin_tx'], 1)

    def test_execute_transaction_invalid_TX_NEGATIVE_AMOUNT(self):
        self.assertEqual(self.ledger.balances, {})
        self.ledger.execute_transaction(self.signedTxs[0])
        self.assertEqual(self.ledger.balances['Eula Zahar'], 1962)
        tx = {'amount': -11, 'fr': 'Eula Zahar', 'to': 'Leslie Collingsworth'}
        tx["sig"] = TxUtils.signTx(tx, self.keys[tx['fr']]['privKey'])
        self.ledger.execute_transaction(tx)

        self.assertEqual(self.ledger.stats['n_coin_tx'], 1)
        self.assertEqual(self.ledger.stats['n_invalid_neg_amnt'], 1)
        self.assertEqual(self.ledger.balances['Eula Zahar'], 1962)

    def test_execute_transaction_valid_TX_OK(self):
        self.assertEqual(self.ledger.balances, {})
        self.ledger.execute_transaction(self.signedTxs[0])

        tx = {'amount': 11, 'fr': 'Eula Zahar', 'to': 'Leslie Collingsworth'}
        tx["sig"] = TxUtils.signTx(tx, self.keys[tx['fr']]['privKey'])
        self.ledger.execute_transaction(tx)

        self.assertEqual(self.ledger.stats['n_coin_tx'], 1)
        self.assertEqual(self.ledger.stats['n_valid_tx'], 1)
        self.assertEqual(self.ledger.balances['Eula Zahar'], 1951)
        self.assertEqual(self.ledger.balances['Leslie Collingsworth'], 11)

    def test_all_execute_transaction(self):
        self.assertEqual(self.ledger.balances, {})
        for tx in self.signedTxs:
            self.ledger.execute_transaction(tx)
        pprint(self.ledger.stats)
        pprint(self.ledger.balances)
        self.assertEqual(self.ledger.stats['n_coin_tx'], 12)
        self.assertEqual(self.ledger.stats['n_invalid_bad_sign_tx'], 3)
        self.assertEqual(self.ledger.stats['n_invalid_nofund_tx'], 3)
        self.assertEqual(self.ledger.stats['n_tx'], 25)
        self.assertEqual(self.ledger.stats['n_valid_tx'], 7)

        self.assertEqual(self.ledger.balances['Alma Hindman'], 4154)
        self.assertEqual(self.ledger.balances['Carol Devoe'], 682)
        self.assertEqual(self.ledger.balances['Donald Martin'], 1879)
        self.assertEqual(self.ledger.balances['Eula Zahar'], 2184)
        self.assertEqual(self.ledger.balances['Karen Langford'], 5119)
        self.assertEqual(self.ledger.balances['Leslie Collingsworth'], 113)
        self.assertEqual(self.ledger.balances['Margaret Williams'], 1485)
        self.assertEqual(self.ledger.balances['Shannon Cano'], 238)
        self.assertEqual(self.ledger.balances['Sophie Hardin'], 1655)
        self.assertEqual(self.ledger.balances['Steven Scott'], 1945)


suite = unittest.TestLoader().loadTestsFromTestCase(TestingLedger)
unittest.TextTestRunner().run(suite)

