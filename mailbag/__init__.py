# __init__.py

# Version of the mailbag package
__version__ = "0.0.1"


from bagit import _make_parser, Bag
from gooey import Gooey

from mailbag.parser import EmailFormatParser

print(EmailFormatParser.registry)

bagit_parser = _make_parser()
bagit_parser.description = f"Mailbag ({bagit_parser.description})"
mailbagit_args = bagit_parser.add_argument_group("Mailbag")
# add mailbag-specific args here
mailbagit_args.add_argument("--foo", help="The foo argument, you know, that one")
mailbagit_args.add_argument("--input_type", help="input type MBOX/PST/IMAP/EML/PDF")
mailbagit_args.add_argument("--output", help="output type MBOX/PST/EML/PDF/WARC")
mailbagit_args.add_argument("--exclude_input_file", help="excludes the original PST, MBOX, or EML file(s) from the mailbag")
mailbagit_args.add_argument("--imap_host", help="the host for creating a mailbag from an IMAP connection")
mailbagit_args.add_argument("--imap_host", help="host for creating a mailbag from an IMAP connection")
mailbagit_args.add_argument("--imap_password", help="password for creating a mailbag from an IMAP connection")
mailbagit_args.add_argument("--exclude_folders", help="email folders to be excluded from the mailbag")
mailbagit_args.add_argument("--exclude_messages", help="a line-separated text file of Message-IDs to be excluded from a mailbag")
mailbagit_args.add_argument("--exclude_input", help="will also exclude email folders and/or messages from the input PST or MBOX file before including it in the mailbag")
mailbagit_args.add_argument("--crawl_links", help="will attempt to capture links in messages and include them in WARC output")
mailbagit_args.add_argument("--crawl-attached-links", help="will attempt to capture links attached to messages and include them in WARC output")
mailbagit_args.add_argument("--no-headers", help="will not include email headers in mailbag.csv")
mailbagit_args.add_argument("--folder_info", help="provide folder details like total no. of folders and emails")
mailbagit_args.add_argument("--pdf-customizable", help="CSS file to customize PDF")
mailbagit_args.add_argument("--export-email-header", help="outputs headers of individual mails")
mailbagit_args.add_argument("--c compress", help="Compress the mailbag as ZIP, TAR, or TAR.GZ")




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
