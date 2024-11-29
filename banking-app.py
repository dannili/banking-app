# A simple banking application that allows users to:
# - Create checking/savings accounts, withdraw, deposit, and transfer between accounts
# - Print out largest n transactions of all accounts, or for a given account

from abc import ABC, abstractmethod

# Logger class
class Logger:
    __instance = None

    def __init__(self):
        self.transactions = {}

    # getInstance() method for sigleton pattern
    @staticmethod
    def getInstance():
        if Logger.__instance is None:
            Logger.__instance = Logger()
        return Logger.__instance

    # log() method
    def log(self, account_id, action, amount, account_type):
        if account_id not in self.transactions:
            self.transactions[account_id] = []
        self.transactions[account_id].append({
            'Action:': action, 'Amount': amount, 'Account Type': account_type
            })

    # find_largest_transaction() method
    def find_largest_transaction_all_accounts(self):
        all_transactions = []
        for account_id, transactions in self.transactions.items():
            for transaction in transactions:
                all_transactions.append((account_id, transaction))
        # In a single line:
        # all_transactions = [(account_id, transaction) 
        #                     for account_id, transactions in self.transactions.items()
        #                     for transaction in transactions]
        largest_transaction = max(all_transactions, 
                                  key=lambda x:x[1]['Amount'])
        
        return largest_transaction
    
    # find top n transactions:
    def find_top_n_transactions_all(self, n):
        all_transactions = []
        for account_id, transactions in self.transactions.items():
            for transaction in transactions:
                all_transactions.append((account_id, transaction))
        
        top_n_transactions = sorted(all_transactions, key=lambda x:x[1]['Amount'], reverse=True)[:n]
        return top_n_transactions
    
    # find largest transction for an account
    def find_largest_transaction(self, account_id):
        if account_id not in self.transactions or self.transactions[account_id] is None:
            return None
        
        largest_transaction = max(self.transactions[account_id], key=lambda x:x['Amount'])

        return largest_transaction
    
# Sample transactions dictionary:
# {
#     101: [
#         {'message': 'Deposit', 'Amount': 500},
#         {'message': 'Withdrawal', 'Amount': 200},
#         {'message': 'Transfer', 'Amount': 300},
#         {'message': 'Deposit', 'Amount': 1500}
#     ],
#     102: [
#         {'message': 'Deposit', 'Amount': 300}
#     ]
# }

# Account abstract class
class Account(ABC):
    def __init__(self, account_id, balance = 0):
        self.account_id = account_id
        self.balance = balance
        self.logger = Logger.getInstance()

    @abstractmethod
    def account_type(self):
        pass

    # deposit() method
    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.logger.log(self.account_id, 'Deposit', amount, self.account_type())
            print(f'{self.account_type()} account {self.account_id} deposit ${amount}.')
    
    # withdraw() method
    def withdraw(self, amount):
        if self.balance < amount:
            ValueError('Insufficient amount.')
        else:
            self.balance -= amount
            self.logger.log(self.account_id, 'Withdraw', amount, self.account_type())
            print(f'{self.account_type()} account {self.account_id} withdraw ${amount}.')

    # transfer() method
    def transfer(self, amount, target_account):
        if self.balance < amount:
            ValueError('Insufficient amount.')
        else:
            self.balance -= amount
            self.logger.log(self.account_id, 'Withdraw', amount, self.account_type())
            target_account.balance += amount
            self.logger.log(self.account_id, 'Transfer', amount, self.account_type())
            print(f'{self.account_id} transfered ${amount} to {target_account.account_id}')

# SavingsAccount concrete class
class SavingsAccount(Account):
    def account_type(self):
        return 'Savings'

# CheckingAccount concrete class
class CheckingAccount(Account):
    def account_type(self):
        return 'Checking'


# AccountFactory abstract class
class AccountFactory(ABC):
    @abstractmethod
    def create_account(self, account_id, balance = 0):
        pass

# SavingsAccountFactory concrete class
class SavingsAccountFactory(AccountFactory):
    def create_account(self, account_id, balance):
        print(f'Savings account {account_id} created with a balance of ${balance}.')
        return SavingsAccount(account_id, balance)
    
# CheckingAccountFactory concrete class
class CheckingAccountFactory(AccountFactory):
    def create_account(self, account_id, balance):
        print(f'Checking account {account_id} created with a balance of ${balance}.')
        return CheckingAccount(account_id, balance)


# TODO: Test using command list:
commands = [
    ["CREATE_ACCOUNT", "A123", "Savings", 500],
    ["CREATE_ACCOUNT", "B456", "Checking", 300],
    ["DEPOSIT", "A123", 100],
    ["DEPOSIT", "B456", 700],
    ["WITHDRAW", "A123", 200],
    ["TRANSFER", "B456", "A123", 150],
    ["FIND_LARGEST_TRANSACTION_ALL"],
    ["FIND_TOP_N_TRANSACTIONS_ALL", 5],
    ["FIND_LARGEST_TRANACTION", "A123"],
]

def commands_processer(commands):
    accounts = {}

    for command in commands:
        action = command[0]

        if action == 'CREATE_ACCOUNT':
            account_id, account_type, balance = command[1], command[2], command[3]
            
            if account_type == 'Savings':
                try:
                    accounts[account_id] = SavingsAccountFactory().create_account(account_id, balance)
                except ValueError as e:
                    print(e)
            elif account_type == 'Checking':
                try:
                    accounts[account_id] = CheckingAccountFactory().create_account(account_id, balance)
                except ValueError as e:
                    print(e)

        elif action == 'DEPOSIT':
            account_id, amount = command[1], command[2]
            if account_id in accounts:
                accounts[account_id].deposit(amount)
            
        elif action == 'WITHDRAW':
            account_id, amount = command[1], command[2]
            if account_id in accounts:
                accounts[account_id].withdraw(amount)
        
        elif action == 'TRANSFER':
            from_account_id, target_account_id, amount = command[1], command[2], command[3]
            if from_account_id in accounts and target_account_id in accounts:
                accounts[from_account_id].transfer(amount, accounts[target_account_id])

        elif action == 'FIND_LARGEST_TRANSACTION_ALL':
            logger = Logger.getInstance()
            largest_transaction = logger.find_largest_transaction_all_accounts()
            if largest_transaction:
                account_id, details = largest_transaction
            print(f'Largest transaction account: {account_id},\nDetails: {details}')

        elif action == 'FIND_TOP_N_TRANSACTIONS_ALL':
            logger = Logger.getInstance()
            n = command[1]
            top_n_transactions = logger.find_top_n_transactions_all(n)
            print(f'Top {n} transactions:')
            for transaction in top_n_transactions:
                print(f'{transaction}')

        elif action == 'FIND_LARGEST_TRANACTION':
            logger = Logger.getInstance()
            account_id = command[1]
            largest_transaction = logger.find_largest_transaction(account_id)
            print(f'Largest transaction for account {account_id}: {largest_transaction}')

commands_processer(commands)
