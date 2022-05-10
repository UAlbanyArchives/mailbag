import os, shutil, glob
from pathlib import Path
import mimetypes
import urllib.parse
from mailbag.models import Attachment

from structlog import get_logger
log = get_logger()

def relativePath(mainPath, file):
    """
    Gets the relative path of an input file within the input directory structure
    Useful for getting the path of messages within an email account

    Parameters:
        mainPath (String): Parent or provided directory path
        file (String): Email file path

    Returns:
        String: emailFolder
    """

    fullPath = Path(mainPath).resolve()
    fullFilePath = Path(file).resolve()
    relPath = str(fullFilePath.relative_to(fullPath))
    if relPath == ".":
        return ""
    else:
        return relPath


def parse_part(part, bodies, attachments, errors):
    """
    Used for EML and MBOX parsers
    Parses a part of an email message for multipart messages or a full message with a single part

    Parameters:
        part (email.Message.message part):
            "msg" contains a list of human readable error messages
            "stack_trace" contains a list of full stack traces
        bodies (dict):
            "msg" contains a list of human readable error messages
            "stack_trace" contains a list of full stack traces
        attachments (list): a list of attachment object as defined in models.py
        errors (dict):
            "msg" contains a list of human readable error messages
            "stack_trace" contains a list of full stack traces
    Returns:
        bodies (dict):
            "msg" contains a list of human readable error messages
            "stack_trace" contains a list of full stack traces
        attachments (list): a list of attachment object as defined in models.py
        errors (dict):
            "msg" contains a list of human readable error messages
            "stack_trace" contains a list of full stack traces
    """
    content_type = part.get_content_type()
    content_disposition = part.get_content_disposition()

    # Extract body
    try:
        if content_type == "text/html" and content_disposition != "attachment":
            bodies["html_encoding"] = part.get_charsets()[0]
            bodies["html_body"] = part.get_payload(decode=True).decode(bodies["html_encoding"])
        if content_type == "text/plain" and content_disposition != "attachment":
            bodies["text_encoding"] = part.get_charsets()[0]
            bodies["text_body"] = part.get_payload(decode=True).decode(bodies["text_encoding"])
    except Exception as e:
        desc = "Error parsing message body"
        errors = handle_error(errors, e, desc)

    # Extract attachments
    if part.get_content_maintype() == "multipart":
        pass
    elif content_disposition is None:
        pass
    else:
        try:
            attachmentName = part.get_filename()
            attachmentFile = part.get_payload(decode=True)
            attachment = Attachment(
                Name=attachmentName if attachmentName else str(len(attachments)),
                File=attachmentFile,
                MimeType=content_type,
            )
            attachments.append(attachment)
        except Exception as e:
            desc = "Error parsing attachments"
            errors = handle_error(errors, e, desc)

    return bodies, attachments, errors


def messagePath(headers):
    """
    Tries to read any email folder arragement from headers
    Useful for getting the path of messages within an email account

    Parameters:
        headers (email.message.Message): Can be used as a dict of email headers

    Returns:
        String: messagePath (must at least return an empty string)
    """

    if headers["X-Folder"]:
        messagePath = Path(headers["X-Folder"]).as_posix()
    else:
        messagePath = ""
    return messagePath


def normalizePath(path):
    # this is not sufficent yet
    if os.name == "nt":
        specials = ["<", ">", ":", '"', "/", "|", "?", "*"]
        special_names = [
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        ]
        new_path = []
        for name in os.path.normpath(path).split(os.sep):
            illegal = False
            for char in specials:
                if char in name:
                    illegal = True
            if illegal:
                new_path.append(urllib.parse.quote_plus(name))
            else:
                new_path.append(name)
        out_path = Path(os.path.join(*new_path)).as_posix()
    else:
        out_path = path

    if out_path == ".":
        return ""
    else:
        return out_path


def moveFile(dry_run, oldPath, newPath):
    os.makedirs(os.path.dirname(newPath), exist_ok=True)
    try:
        log.debug("from: " + str(oldPath))
        log.debug("to: " + str(newPath))
        shutil.move(oldPath, newPath)
    except IOError as e:
        log.error("Unable to move file. %s" % e)


def getFileBeforeAfterPath(mainPath, mailbag_name, input, file):
    """
    Creates file paths for input mail files and new paths

    Parameters:
        mainPath (String) :
        mailbag_name (String) :
        input (String) :
        file (String) :
    """
    fullPath = Path(mainPath).resolve()
    fullFilePath = Path(file).resolve()
    relPath = fullFilePath.relative_to(fullPath).parents[0]
    filename = fullFilePath.name
    folder_new = os.path.join(fullPath, mailbag_name, "data", input)
    file_new_path = os.path.join(folder_new, relPath, filename)

    return fullPath, fullFilePath, file_new_path, relPath


def moveWithDirectoryStructure(dry_run, mainPath, mailbag_name, input, file):
    """
    Create new mailbag directory structure while maintaining the input data's directory structure.
    Useful for MBOX, EML, and MSG files.

    Parameters:
        dry_run (Boolean):
        mainPath (String): Parent or provided directory path
        mailbag_name (String): Mailbag name
        input (String): Mail type
        emailFolder (String): Path of the email export file relative to mainPath
        file (String): Email file path

    Returns:
        file_new_path (Path): The path where the file was moved
    """

    fullPath, fullFilePath, file_new_path, relPath = getFileBeforeAfterPath(mainPath, mailbag_name, input, file)
    log.debug("Moving: " + str(fullFilePath) + " to: " + str(file_new_path) + " SubFolder: " + str(relPath))

    if not dry_run:
        moveFile(dry_run, fullFilePath, file_new_path)
        # clean up old directory structure
        p = fullFilePath.parents[0]
        while p != p.root and p != fullPath:
            if not os.listdir(p):
                log.debug("Cleaning: " + str(p))
                os.rmdir(p)
                # dirty hack since rmdir is not synchronous on Windows
                if os.name == "nt":
                    import time

                    time.sleep(0.01)
            p = p.parent

    return file_new_path


def guessMimeType(filename):
    """
    Takes an file name and uses mimetypes to guess the mime type

    Parameters:
        filename (String): Attachment filename

    Returns:
        Mimetype (String)
    """
    return mimetypes.guess_type(filename)[0]
