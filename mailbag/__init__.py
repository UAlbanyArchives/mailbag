# __init__.py

# Version of the mailbag package
__version__ = "0.0.1"


from bagit import _make_parser, Bag
from gooey import Gooey

from mailbag.email_account import EmailAccount

print(EmailAccount.registry)

bagit_parser = _make_parser()
bagit_parser.description = f"Mailbag ({bagit_parser.description})"
mailbagit_args = bagit_parser.add_argument_group("Mailbag")
# add mailbag-specific args here
mailbagit_args.add_argument("--foo", help="The foo argument, you know, that one")

def cli():
    bagit_parser.parse_args()
    # do the thing

@Gooey
def gui():
    bagit_parser.parse_args()
    #do the thing

class Mailbag:
    def __init__(self):
        print("Hello world!")
