from llm.prompts import RESUME_ANALYZER_PROMPT
from langchain_core.runnables.base import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from typing import Dict, Annotated, Optional, Any, List, Sequence, Tuple, Literal, Union
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle 
import markdown2
from weasyprint import HTML
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

class ResumeAnalyzer:

    def __init__(self, llm: BaseChatModel, email_credentials: Dict[str, str]):
        self._llm = llm
        self._chain = self.get_resume_analyzer_chain(self._llm)
        self._email_credentials = email_credentials

    def get_resume_analyzer_chain(self, llm: BaseChatModel) -> Runnable:
        prompt = ChatPromptTemplate.from_messages([
            ("system", RESUME_ANALYZER_PROMPT),
            ("user", "{resume} {job_description}")
        ])
        chain = prompt | llm | StrOutputParser()
        return chain
    

    def analyze_resume(self, resume: Document, job_description: Document) -> str:
        analysis = self._chain.invoke({"resume": resume, "job_description": job_description})
        return analysis
    

    def markdown_to_pdf(self, md_content, output_path):
        """
        Convert Markdown content to a PDF file.

        Parameters:
        - md_content: str : Markdown content to be converted
        - output_path: str : Path to save the output PDF file
        """
        # Convert Markdown to HTML
        html_content = markdown2.markdown(md_content)

        # Convert HTML to PDF
        HTML(string=html_content).write_pdf(output_path)

        print(f"PDF successfully saved to {output_path}")

    
    def delete_file(self, file_path: str):
        """
        Delete a file from the filesystem.

        Parameters:
        - file_path: str : The path to the file to be deleted
        """
        try:
            os.remove(file_path)
            print(f"File {file_path} successfully deleted")
        except FileNotFoundError:
            print(f"File {file_path} not found")
        except PermissionError:
            print(f"Permission denied: Unable to delete {file_path}")
        except Exception as e:
            print(f"Error occurred while deleting the file: {e}")


    def send_gmail_with_pdf(self, sender_email, sender_password, receiver_email, subject, body, pdf_path):
        """
        Send an email with a PDF attachment using Gmail.

        Parameters:
        - sender_email: str : Sender's Gmail address
        - sender_password: str : Sender's Gmail password or app-specific password
        - receiver_email: str : Receiver's email address
        - subject: str : Subject of the email
        - body: str : Body of the email
        - pdf_path: str : Path to the PDF file to be attached
        """
        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Attach the body with the msg instance
        msg.attach(MIMEText(body, 'plain'))

        # Open the file to be sent
        with open(pdf_path, "rb") as attachment:
            # Create a MIMEApplication object
            part = MIMEApplication(attachment.read(), _subtype="pdf")
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(pdf_path)}"')
            msg.attach(part)

        # Create the SMTP session
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)  # Gmail SMTP server
            server.starttls()  # Enable security
            server.login(sender_email, sender_password)  # Login with sender's email and password

            # Send the email
            server.send_message(msg)
            server.quit()

            print(f"Email successfully sent to {receiver_email}")

        except Exception as e:
            print(f"Failed to send email. Error: {e}")

    
    def create_and_send_report(self, resume: Document, job_description: Document, email: str, temp_pdf_output_path: str = "report.pdf") -> str:
        status = {
            "status": None,
            "err": None
        }
        try:
            # Create report
            report = self.analyze_resume(resume=resume, job_description=job_description)
            # Save it as pdf
            self.markdown_to_pdf(md_content=report, output_path=temp_pdf_output_path)
            # Send it to the email address
            sender_email = self._email_credentials.get("user")
            email_password = self._email_credentials.get("password")
            subject = "Here is your Resume Report & Interview Toolkit!"
            body = "Thank you for trusting us with your resume. Please find your Resume Report and Interview Kit attached.\n\n- The Freestack Initiative"
            self.send_gmail_with_pdf(
                sender_email=sender_email,
                sender_password=email_password,
                receiver_email=email,
                subject=subject,
                body=body,
                pdf_path=temp_pdf_output_path
                )
            # Cleanup temp files
            self.delete_file(temp_pdf_output_path)
            status["status"] = "Success"

        except Exception as ex:
            status["status"] = "Failed"
            status["error"] = str(ex)

        return status

