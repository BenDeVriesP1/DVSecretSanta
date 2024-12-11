from email.mime.text import MIMEText




def makeEmail(sender :str,recipients: list[str],subject: str,body :str) -> str:
    message = MIMEText(body)
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = ', '.join(recipients)
    return message.as_string()


def main():
    print(makeEmail("ben.devries@phase1eng.com",["bendrummerboy@gmail.com"],'what does this look like','your secret santa assingment'))

if __name__ == '__main__':
    main()