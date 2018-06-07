from random import randint, random, shuffle, seed
from pprint import pprint
import math
import json
import unittest


class Ledger:
    def __init__(self):
        self.balances = {}  ## dictionary where the key is the user and the value is the balance the user have
        #### and it is updated each time a valid transaction is executed

        self.stats = {"n_tx": 0,  ## Total Number of transactions
                      "n_coin_tx": 0,  ## Total Number of transactions that 'coinbase' is the sender( fr )
                      "n_valid_tx": 0,
                      ## Total Number of transactions that are valid and the sender(fr) is not 'coinbase'
                      "n_invalid_to_tx": 0,  ## Total Number of transactions that are not valid because the reciver(to)
                      ## is 'coinbase'
                      "n_invalid_neg_amnt": 0,
                      ## Total Number of transactions that are not valid because the amount of trans.
                      ## is negative
                      "n_invalid_fr_tx": 0,  ## Total Number of transactions that are not valid because
                      ## the sender(fr) does not have balance
                      "n_invalid_nofund_tx": 0  ## ## Total Number of transactions that are not valid because
                      ## the amount of trans. is bigger than the balance of the sender(fr)
                      }

    def validate_transaction(self, fr, to, amount):
        # True Cases
        if fr == 'coinbase' and amount >= 0:
            self.stats['n_tx'] += 1
            self.stats['n_coin_tx'] += 1
            return True
        elif (fr in self.balances ) and (amount <= self.balances[fr]) and  ( amount >= 0) and  not ( to =='coinbase'):
            self.stats['n_tx'] += 1
            self.stats['n_valid_tx'] += 1
            return True
            # True_checker = None
            # TrueSender_checker = None
            # balance_checker = None
            # for key,value  in self.balances.items() :
            # if fr == key and amount < value:
            #    True_checker = True  # has an account
            # if key == to :
            # TrueSender_checker =True
            # if key == fr:
            # balance_checker = value

        # False Cases
        # (if not Elif because you don't stated that it couldn't be more than one False Case in the False transaction)
        if to == 'coinbase':
            self.stats['n_tx'] += 1
            self.stats['n_invalid_to_tx'] += 1
            #return False
        elif fr not in self.balances:
            self.stats['n_tx'] += 1
            self.stats['n_invalid_fr_tx'] += 1
            return False

        if amount < 0:
            self.stats['n_tx'] += 1
            self.stats['n_invalid_neg_amnt'] += 1
            #return False
        if amount > self.balances[fr]:
            self.stats['n_tx'] += 1
            self.stats['n_invalid_nofund_tx'] += 1
            #return False
        return False



            #### Add your code below
            #### check fr, to, amount variabile and return true if the transaction is valid , False otherwise
            #### in addition you should update the stats dictionary:
            ####  you should n_tx increment by 1 each time you call validate transaction and increment by 1
            ####  ( n_coin_tx ,n_valid_tx ,n_invalid_to_tx ,n_invalid_neg_amnt ,n_invalid_fr_tx ,n_invalid_nofund_tx )

    def execute_transaction(self, tx):

        if self.validate_transaction(tx['fr'], tx['to'], tx['amount']) == True:
            print tx
            if tx['fr'] == 'coinbase' and tx['amount'] >= 0:
                if tx['to'] not in self.balances:
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

        #elif self.validate_transaction(tx['fr'], tx['to'], tx['amount']) == False:
        else :
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

        print "==================================================="




        #### Add your code below
        #### use validate_transaction funtion to check if tx(transaction) is validate o not
        #### and update the stats and balance of users  if the tx is valid


class TestingLedger(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger()
        self.txs = json.load(open('transactions.json'))
        #print (self.txs[10])
        #print 'Hi', self.txs[14]

    def test_validate_transaction_valid_TX_NEWCOIN_OK(self):#1
        print 'Number 1'
        self.assertEqual(self.ledger.validate_transaction('coinbase', 'Eula Zahar', 100), True)
        self.assertEqual(self.ledger.stats['n_coin_tx'], 1)

    def test_validate_transaction_invalid_TX_BAD_FR(self):#2
        print 'Number 2'
        self.assertEqual(self.ledger.validate_transaction('Carol Clark', 'Eula Zahar', 100), False)
        self.assertEqual(self.ledger.stats['n_invalid_fr_tx'], 1)

    def test_validate_transaction_invalid_TX_BAD_FR_2(self):#3
        print 'Number 3'
        self.assertEqual(self.ledger.validate_transaction('Eula Zahar', 'Carol Clark', 100), False)
        self.assertEqual(self.ledger.stats['n_invalid_fr_tx'], 1)

    def test_validate_transaction_invalid_NO_FUNDS(self):#4
        print 'Number 4'
        self.ledger.execute_transaction(self.txs[0])
        self.assertEqual(self.ledger.validate_transaction('Eula Zahar', 'Leslie Collingsworth', 111), False)
        #print self.ledger.stats
        self.assertEqual(self.ledger.stats['n_invalid_nofund_tx'], 1)


    def test_validate_transaction_valid(self):#5
        print 'Number 5'
        self.ledger.execute_transaction(self.txs[0])
        self.assertEqual(self.ledger.validate_transaction('Eula Zahar', 'Leslie Collingsworth', 11), True)
        self.assertEqual(self.ledger.stats['n_valid_tx'], 1)
        self.assertEqual(self.ledger.stats['n_tx'], 2) # changed to 2

    def test_validate_transaction_valid_TX_NEWCOIN_OK_2(self):#6
        print 'Number 6'
        self.assertEqual(self.ledger.validate_transaction('coinbase', 'Eula Zahar', 0), True)
        self.assertEqual(self.ledger.stats['n_coin_tx'], 1)

    def test_validate_transaction_invalid_TX_NEGATIVE_AMOUNT(self):#7
        print 'Number 7'
        self.ledger.execute_transaction(self.txs[0])
        self.assertEqual(self.ledger.validate_transaction('Eula Zahar', 'Leslie Collingsworth', -11), False)
        self.assertEqual(self.ledger.stats['n_invalid_neg_amnt'], 1)

    def test_validate_transaction_invalid_TX_BAD_TO(self):#8
        print 'Number 8'
        self.ledger.execute_transaction(self.txs[0])
        self.assertEqual(self.ledger.validate_transaction('Eula Zahar', 'coinbase', 11), False)
        self.assertEqual(self.ledger.stats['n_invalid_to_tx'], 1)

    def test_execute_transaction_valid(self):#9
        print 'Number 9'
        self.assertEqual(self.ledger.balances, {})
        self.ledger.execute_transaction(self.txs[0])
        self.assertEqual(self.ledger.balances['Eula Zahar'], 100)
        self.assertEqual(self.ledger.stats['n_coin_tx'], 1)

    def test_execute_transaction_invalid_TX_BAD_FR(self):#
        print 'Number 10'
        self.assertEqual(self.ledger.balances, {})
        self.ledger.execute_transaction(self.txs[14])
        print 'Hi1', self.ledger.stats
        self.assertEqual( 'Donald Martin' in self.ledger.balances, False)
        #print 'Hi2' ,self.ledger.stats
        self.assertEqual(self.ledger.stats['n_invalid_fr_tx'], 1)######

    def test_execute_transaction_invalid_NO_FUNDS(self):
        self.assertEqual(self.ledger.balances, {})
        self.ledger.execute_transaction(self.txs[0])
        self.ledger.execute_transaction(self.txs[10])
        self.assertEqual(self.ledger.balances['Eula Zahar'], 100)
        self.assertEqual(self.ledger.stats['n_invalid_nofund_tx'], 1)
        self.assertEqual(self.ledger.stats['n_coin_tx'], 1)

    def test_execute_transaction_invalid_TX_NEGATIVE_AMOUNT(self):
        self.assertEqual(self.ledger.balances, {})
        self.ledger.execute_transaction(self.txs[0])
        self.assertEqual(self.ledger.balances['Eula Zahar'], 100)
        self.ledger.execute_transaction({'amount': -11, 'fr': 'Eula Zahar', 'to': 'Leslie Collingsworth'} )
        self.assertEqual(self.ledger.stats['n_coin_tx'], 1)
        self.assertEqual(self.ledger.stats['n_invalid_neg_amnt'], 1)
        self.assertEqual(self.ledger.balances['Eula Zahar'], 100)

    def test_execute_transaction_valid_TX_OK(self):
        self.assertEqual(self.ledger.balances, {})
        self.ledger.execute_transaction(self.txs[0])
        self.ledger.execute_transaction({'amount': 11, 'fr': 'Eula Zahar', 'to': 'Leslie Collingsworth'} )
        self.assertEqual(self.ledger.stats['n_coin_tx'], 1)
        self.assertEqual(self.ledger.stats['n_valid_tx'], 1)
        self.assertEqual(self.ledger.balances['Eula Zahar'], 89)
        self.assertEqual(self.ledger.balances['Leslie Collingsworth'], 11)

    def test_all_execute_transaction(self):

        self.assertEqual(self.ledger.balances, {})
        for tx in self.txs:
            self.ledger. execute_transaction(tx)
        self.assertEqual(self.ledger.stats['n_coin_tx'], 11)
        self.assertEqual(self.ledger.stats['n_invalid_fr_tx'], 2)
        self.assertEqual(self.ledger.stats['n_invalid_nofund_tx'], 4)
        self.assertEqual(self.ledger.stats['n_tx'], 21)
        self.assertEqual(self.ledger.stats['n_valid_tx'], 4)
        self.assertEqual(self.ledger.balances['Eula Zahar'], 34)
        self.assertEqual(self.ledger.balances['Carol Devoe'], 100)
        self.assertEqual(self.ledger.balances['Margaret Williams'], 100)
        self.assertEqual(self.ledger.balances['Sophie Hardin'], 100)
        self.assertEqual(self.ledger.balances['Alma Hindman'], 166)
        self.assertEqual(self.ledger.balances['Karen Langford'], 298)
        self.assertEqual(self.ledger.balances['Leslie Collingsworth'], 100)
        self.assertEqual(self.ledger.balances['Shannon Cano'], 2)
        self.assertEqual(self.ledger.balances['Steven Scott'], 100)
        self.assertEqual(self.ledger.balances['Donald Martin'], 100)

suite = unittest.TestLoader().loadTestsFromTestCase(TestingLedger)
unittest.TextTestRunner().run(suite)
