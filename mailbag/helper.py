from pathlib import Path
import os, shutil, glob
from structlog import get_logger
from warcio.capture_http import capture_http
from warcio import WARCWriter
import requests  # requests *must* be imported after capture_http

import http.server
import socketserver
import sys

log = get_logger()


def moveFile(dry_run, oldPath, newPath):
    os.makedirs(os.path.dirname(newPath), exist_ok=True)
    try:
        log.debug("from: " + str(oldPath))
        log.debug("to: " + str(newPath))
        shutil.move(oldPath, newPath)
    except IOError as e:
        log.error('Unable to move file. %s' % e)


def emailFolder(mainPath, file):
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
        
        subFolders = str(fullFilePath.relative_to(fullPath).parents[0])
        return subFolders

        
def moveWithDirectoryStructure(dry_run, mainPath, mailbag_name, input, emailFolder, file):
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

        fullPath = Path(mainPath).resolve()
        fullFilePath = Path(file).resolve()
        filename = fullFilePath.name
        folder_new = os.path.join(fullPath, mailbag_name, input)
        
        file_new_path = os.path.join(folder_new, emailFolder, filename)

        log.debug('Moving: ' + str(fullFilePath) + ' to: ' + str(file_new_path) + ' SubFolder: ' + str(emailFolder))
        if(not dry_run):
            moveFile(dry_run, fullFilePath, file_new_path)
            # clean up old directory structure
            p = fullFilePath.parents[0]
            while p != p.root and p != fullPath:
                if not os.listdir(p):
                    log.debug('Cleaning: ' + p)
                    os.rmdir(p)
                    # dirty hack since rmdir is not synchronous on Windows
                    if os.name == "nt":
                        import time
                        time.sleep(0.01)
                p = p.parent

        return file_new_path


def saveAttachments(part):
    return (part.get_filename(), part.get_payload(decode=True))


def saveFile(filePath, text):
    with open(filePath, 'w') as f:
        f.write(text)


def deleteFile(filePath): 
    if os.path.exists(filePath):
        os.remove(filePath)


def startServer(port=5000):
    try:
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), Handler) as httpd:
            httpd.serve_forever()
    # Stopped the server
    except KeyboardInterrupt:
        httpd.server_close()
        log.debug("The server is stopped.")

                        
def saveWARC(dry_run, warc_dir, message, port=5000):
    message_warc_dir = os.path.join(warc_dir, str(message.Mailbag_Message_ID))
    filename = os.path.join(message_warc_dir, str(message.Mailbag_Message_ID) + ".warc.gz")
    log.debug('Saving WARC:' + filename)
    
    if not dry_run:
        os.mkdir(message_warc_dir)
        with capture_http(filename):
            saveFile('tmp.html', message.HTML_Body)            
            requests.get('http://localhost:' + str(port) + '/tmp.html')
        deleteFile('tmp.html')
