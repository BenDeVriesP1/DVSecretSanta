from email.mime.text import MIMEText




class emailCreator:
    def __init__(self,templatePath: str):
        with open(templatePath,'r') as f:
            self.template = f.read()
        


    def makeEmail(self,sender :str,recipients: list[str],subject: str,body :str) -> str:
        message = MIMEText(body)
        message['Subject'] = subject
        message['From'] = sender
        message['To'] = ', '.join(recipients)
        return message.as_string()
    

    def createBody(self,santaName,giftee,drawingName):
        message = self.template
        message = message.replace("<santaName>",santaName)
        message = message.replace('<giftee>',giftee)
        message = message.replace('drawingName',drawingName)
        return message






# def main():
#     print(makeEmail("ben.devries@phase1eng.com",["bendrummerboy@gmail.com"],'what does this look like','your secret santa assingment'))

# if __name__ == '__main__':
#     main()