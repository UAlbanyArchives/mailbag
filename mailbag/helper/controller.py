import os, shutil, glob
import datetime
from time import time

import mailbag.globals as globals

from structlog import get_logger
log = get_logger()


def progress(current, total, start_time, prefix="", suffix="", decimals=1, length=100, fill="█", print_End="\r"):
    """
    Call in a loop to create terminal progress bar

    Parameters:
        current (int): current progress
        total (int): total iterations
        start_time (float): start time
        prefix (String): prefix string
        suffix (String): suffix string
        decimals (int): positive number of decimals in percent complete
        length (int): character length of bar (Int)
        fill (String): bar fill character (Str)
        printEnd (String): end character (e.g. "\r", "\r\n")
    """

    time_spent = time() - start_time
    remaining_time = round(time_spent * (total / current - 1), 2)
    e = datetime.datetime.now()
    percent = ("{0:." + str(decimals) + "f}").format(100 * (current / float(total)))
    # filledLength = int(length * current // total)
    style = globals.style
    # bar = fill * filledLength + '-' * (length - filledLength)

    dt = f"{e.year}-{e.month:02d}-{e.day:02d} {e.hour:02d}:{e.minute:02d}.{e.second:02d}"
    message_type = f'[{style["cy"][0]}{prefix}{style["b"][1]}]'
    # deco_prefix = f'{style["b"][0]}{prefix}{style["b"][1]}'
    # statusBar = f'|{bar}| {percent}% [{current}MB out of {total}MB] {suffix}'
    status = f"{percent}% [{current} / {total} messages] {remaining_time}s remaining"

    print(f"\r{dt} {message_type} {status}", end=print_End)


def processedFile(filePath):
    """
    Add size of this file to counter

    Parameters:
        filePath (String): Location to find the file
    """

    increment = os.path.getsize(filePath) / (1024**2)
    globals.processedSize += increment
    globals.processedSize = round(globals.processedSize, 2)


def getDirectorySize(directory, format):
    """
    Calculate total size of relevant files in the directory

    Parameters:
        directory (String): Location to find files
        format (String): format of the mail type

    Returns:
        String: emailFolder
    """

    filePath = os.path.join(directory, "**", "*." + format)
    total = sum(os.path.getsize(f) for f in glob.iglob(filePath, recursive=True) if os.path.isfile(f))
    total = round(total / (1024**2), 2)
    log.debug(f"Total files to be processed: {total}MB")
    return total


def saveAttachmentOnDisk(dry_run, attachments_dir, message):
    """
    Takes an email message object and writes any attachments in the model
    to the attachments subdirectory according to the mailbag spec

    Parameters:
        dry_run (Boolean): Option to do a test run without writing changes
        attachments_dir (Path): Path to the attachments subdirectory
        message (Email): A full email message object desribed in models.py
    """

    if not dry_run:
        message_attachments_dir = os.path.join(attachments_dir, str(message.Mailbag_Message_ID))
        os.mkdir(message_attachments_dir)

    for attachment in message.Attachments:
        log.debug("Saving Attachment:" + str(attachment.Name))
        log.debug("Type:" + str(attachment.MimeType))
        if not dry_run:
            attachment_path = os.path.join(message_attachments_dir, attachment.Name)
            f = open(attachment_path, "wb")
            f.write(attachment.File)
            f.close()


