from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class emailCreator:
    def __init__(self,templatePath: str,subjectTemplate: str = "@@drawingName@@ secret santa drawing"):
        with open(templatePath,'r') as f:
            self.template = f.read()
        with open("htmlTemplate.html",'r') as f:
            self.html = f.read()
        self.subjectTemplate = subjectTemplate
        


    def createEmail(self,drawingName: str,sender:str,santa: dict[str],giftee) -> str:
        body=self.template

        message = MIMEMultipart('alternative')
        part1 = MIMEText(body, 'plain')
        
        htmlMessage=''
        for line in body.split('\n'):
            htmlMessage+='<p>'
            htmlMessage+=line
            htmlMessage+='</p>\n'

        htmlCopy=self.html
        htmlCopy=htmlCopy.replace("@@mainHTMLMessage@@",htmlMessage)
        
        part2 = MIMEText(htmlCopy, 'html')
        
        message['Subject'] = self.subjectTemplate
        message['From'] = sender
        message['To'] = ', '.join([santa['email']])
        message.attach(part1)
        message.attach(part2)
        rawMessage=message.as_string()
        rawMessage=rawMessage.replace("@@name@@",santa['name'])
        rawMessage=rawMessage.replace("@@giftee@@",giftee)
        rawMessage=rawMessage.replace("@@drawingName@@",drawingName)
        return rawMessage