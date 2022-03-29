import bagit
from structlog import get_logger
import csv
from mailbag.email_account import EmailAccount
from mailbag.derivative import Derivative
from dataclasses import dataclass, asdict, field, InitVar
from pathlib import Path
import os, shutil, glob
import mailbag.helper as helper


log = get_logger()


class Controller:
    """Controller - Main controller"""

    def __init__(self, args):
        self.args = args
        self.format = self.format_map[args.input]
        self.derivatives_to_create = [self.derivative_map[d] for d in args.derivatives]

    @property
    def format_map(self):
        return EmailAccount.registry

    @property
    def derivative_map(self):
        return Derivative.registry

    def generate_mailbag(self):
        mail_account: EmailAccount = self.format(self.args.directory, self.args)

        derivatives = [d(mail_account) for d in self.derivatives_to_create]

        # do stuff you ought to do with per-account info here
        # mail_account.account_data()
        #for d in derivatives:
        #    d.do_task_per_account()

        #Create folder mailbag folder before writing mailbag.csv
        if os.path.isfile(self.args.directory):
            parent_dir = os.path.dirname(self.args.directory)
        else:
            parent_dir = self.args.directory
        mailbag_dir = os.path.join(parent_dir, self.args.mailbag_name)
        attachments_dir = os.path.join(str(mailbag_dir),'attachments')
        log.debug("Creating mailbag at " + str(mailbag_dir))

        if not self.args.dry_run:
            os.mkdir(mailbag_dir)
            os.mkdir(attachments_dir)

        #Creating a bag
        bag = bagit.make_bag(mailbag_dir)
        csv_dir = os.path.join(parent_dir, self.args.mailbag_name)
        #Setting up mailbag.csv
        header = ['Error', 'Mailbag-Message-ID', 'Message-ID', 'Message-Path', 'Original-Filename','Date', 'From', 'To', 'Cc', 'Bcc', 'Subject',
                  'Content_Type']
        csv_data = []
        mailbag_message_id = 0
        csv_portion_count = 0
        csv_portion = []
        csv_portion.append(header)


        for message in mail_account.messages():
            # do stuff you ought to do per message here

            # Generate mailbag_message_id
            mailbag_message_id += 1
            message.Mailbag_Message_ID = mailbag_message_id
            
            if message.AttachmentNum and message.AttachmentNum>0:
                attachments_dir=os.path.join(mailbag_dir,"data","attachments")
                helper.saveAttachmentOnDisk(self.args.dry_run,attachments_dir,message)
            
            # Setting up CSV data
            # checking if the count of messages exceed 100000 and creating a new portion if it exceeds
            if csv_portion_count > 100000:
                csv_data.append(csv_portion)
                csv_portion = []
                csv_portion.append(header)
                csv_portion.append(
                    [" ".join(message.Error), message.Mailbag_Message_ID, message.Message_ID, message.Message_Path, message.Original_Filename, message.Date, message.From,
                     message.To, message.Cc,message.Bcc, message.Subject, message.Content_Type])
                csv_portion_count = 0
            #if count is less than 100000 , appending the messages in one list
            else:
                csv_portion.append(
                    [" ".join(message.Error), message.Mailbag_Message_ID, message.Message_ID, message.Message_Path, message.Original_Filename, message.Date, message.From,
                     message.To, message.Cc,message.Bcc, message.Subject, message.Content_Type])
            csv_portion_count += 1

            #Generate derivatives
            for d in derivatives:
                d.do_task_per_message(message, self.args, mailbag_dir)

        # append any remaining csv portions < 100000
        csv_data.append(csv_portion)

        # Write CSV data to mailbag.csv
        log.debug("Writing mailbag.csv to " + str(csv_dir))
        if not self.args.dry_run:
            #Creating csv
            # checking if there are multiple portions in list or not
            if len(csv_data) == 1:
                filename = os.path.join(csv_dir, "mailbag.csv")
                with open(filename, 'w', encoding='UTF8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(csv_data[0])
            else:
                portion_count = 0
                for portion in csv_data:
                    portion_count += 1
                    filename = os.path.join(csv_dir, "mailbag-" + str(portion_count) + ".csv")
                    with open(filename, 'w', encoding='UTF8', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerows(portion)

        #Loading the bag and saving manifests
        bag = bagit.Bag(mailbag_dir)
        bag.save(manifests=True)

        return mail_account.messages()
