import os
import subprocess
import distutils.spawn
from mailbagit.derivative import Derivative
from structlog import get_logger
import mailbagit.helper.derivative as derivative
import mailbagit.helper.common as common


skip_registry = False

try:
    chromes = ["google-chrome", "chrome.exe", "chrome"]
    chrome = next((c for c in chromes if distutils.spawn.find_executable(c)), None)
    skip_registry = True if chrome is None else False

except:
    skip_registry = True

log = get_logger()

if not skip_registry:

    class PDFChromeDerivative(Derivative):
        derivative_name = "pdf-chrome"
        derivative_format = "pdf"
        derivative_agent = "chrome"
        derivative_agent_version = "unknown"

        def __init__(self, email_account, **kwargs):
            log.debug("Setup account")
            super()

            self.args = kwargs["args"]
            mailbag_dir = kwargs["mailbag_dir"]
            self.pdf_dir = os.path.join(mailbag_dir, "data", self.derivative_format)
            if not self.args.dry_run:
                os.makedirs(self.pdf_dir)

        def do_task_per_account(self):
            print(self.account.account_data())

        def do_task_per_message(self, message):

            errors = {}
            errors["msg"] = []
            errors["stack_trace"] = []

            try:

                out_dir = os.path.join(self.pdf_dir, message.Derivatives_Path)
                filename = os.path.join(out_dir, str(message.Mailbag_Message_ID))
                html_name = filename + ".html"
                pdf_name = filename + ".pdf"

                if message.HTML_Body is None and message.Text_Body is None:
                    log.warn("No HTML or plain text body for " + str(message.Mailbag_Message_ID) + ". No PDF derivative will be created.")
                else:
                    log.debug("Writing HTML to " + str(html_name) + " and converting to " + str(pdf_name))
                    # Calling helper function to get formatted html
                    try:
                        html_formatted, encoding = derivative.htmlFormatting(message, self.args.css)
                    except Exception as e:
                        desc = "Error formatting HTML for PDF derivative"
                        errors = common.handle_error(errors, e, desc)

                    if not self.args.dry_run:
                        try:
                            if not os.path.isdir(out_dir):
                                os.makedirs(out_dir)

                            with open(html_name, "w", encoding="utf-8") as write_html:
                                write_html.write(html_formatted)
                                write_html.close()
                            command = [
                                chrome,
                                "--headless",
                                "--run-all-compositor-stages-before-draw",
                                "--disable-gpu",
                                "--print-to-pdf-no-header",
                                "--print-to-pdf=" + os.path.abspath(pdf_name),
                                os.path.abspath(html_name),
                            ]

                            # Adds --no-sandbox arg to run as root in docker container if env variable set
                            if os.environ.get("IN_CONTAINER", "").upper() == "TRUE":
                                command.insert(4, "--no-sandbox")

                            log.debug("Running " + " ".join(command))
                            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                            stdout, stderr = p.communicate()
                            if p.returncode == 0:
                                log.debug("Successfully created " + str(message.Mailbag_Message_ID) + ".pdf")
                            else:
                                if stdout:
                                    log.warn("Output converting to " + str(message.Mailbag_Message_ID) + ".pdf: " + str(stdout))
                                if stderr:
                                    desc = "Error converting to " + str(message.Mailbag_Message_ID) + ".pdf: " + str(stderr)
                                    errors = common.handle_error(errors, None, desc, "error")
                            # delete the HTML file
                            if os.path.isfile(pdf_name):
                                os.remove(html_name)

                        except Exception as e:
                            desc = "Error writing HTML and converting to PDF derivative"
                            errors = common.handle_error(errors, e, desc)

            except Exception as e:
                desc = "Error creating PDF derivative with chrome"
                errors = common.handle_error(errors, e, desc)

            message.Error.extend(errors["msg"])
            message.StackTrace.extend(errors["stack_trace"])

            return message