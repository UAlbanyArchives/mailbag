from mailbag.parser import EmailFormatParser
from mailbag.emailModel import Email

import sys
import io

import pypff
import pandas as pd




class PST(EmailFormatParser):
    """PST - This concrete class parses PST file format"""
    parser_name = 'PST'






    def parse(self,*args,**kwargs):

        """Parses the PST file
               Return:
                    allMails (list) : list of email model object"""


        allmails = []


        for folder in self.sub_folders:
            messages = []
            mailObj = Email()
            if folder.number_of_sub_folders:
                messages += PST.parse(self=folder)
                #print(messages)
            #print(folder.name)
            for msg in folder.sub_messages:


                mailObj.From=msg.sender_name
                mailObj.Subject=msg.subject
                print("Folder name:",folder.name)
                print("Subject:", mailObj.Subject)
                print("From:", mailObj.From)
                allmails.append(mailObj)




        return allmails



##TEST MODULE
pst = pypff.file()
pst.open("test.pst")
root = pst.get_root_folder()
print(root)
mess=PST.parse(self=root)

