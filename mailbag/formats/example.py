# This is an example parser, meant to show how
# to hook up a real parser

# Does nothing currently
from mailbag.email_account import EmailAccount
from mailbag.models import Email
class ExampleAccount(EmailAccount):
    format_name = 'example'

    def __init__(self, target_account, **kwargs):
        print("Parsity parse")
        # code goes here to set up mailbox and pull out any relevant account_data
        account_data = {}
        messages = []

    def account_data(self):
        return account_data

    def messages(self):
        for message in messages:
            yield Email(**message)
