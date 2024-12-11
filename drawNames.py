from random import shuffle
import os
import smtplib
import json
from createEmail import makeEmail


class secretGiverReciver:
    def __init__(self,name: str,email : str = '',rejects : str | list[str] = ''):
        self.name = name
        self.email = email if email is not '' else 'N/A'
        if(type(rejects) == str):
            self.rejects = [rejects]
        else:
            self.rejects = rejects
        self.reciver = 'NoOne?'
    
    def doesReject(self,name : str) -> bool:
        return True if name in self.rejects else False

    def addReciver(self, recivername: str):
        self.reciver = recivername

    def getReciver(self) -> str:
        return self.reciver
    
    def getEmail(self):
        return self.email
    
    def makeAnouncementFile(self,path: str):
        with open(f"{path}\\{self.name}s_assingment.txt",'w') as f:
            f.write(f"FOR {self.name.upper()}S EYES ONLY DONT BE A CHEATER AND PEEK\n\n\n\n\n\n\n")
            f.write(f"{self.name} you are getting a gift for {self.reciver}")

    def createAssingmentEmail(self,whossanta :str,isfrom :str):
        header = f"{whossanta}'s Secret Santa Email"
        body = f"Hello {self.name},\n"
        body += f"You are reciving this email in order to inform you of your secret santa assingement for the {whossanta}'s secret santa drawing. You either gave Ben your email or he found it somewhere.\n\n\n"
        body += f"You are getting {self.reciver} a present this year\n\n\n"
        body += f"Merry Christmas\n\n\n"
        body += "To Unsubscribe from this email track down Ben DeVries and inform him of your wishs"
        return makeEmail(isfrom,[self.email],header,body)


itterations = 0

def assignNames(santas: dict[str,secretGiverReciver]) -> dict[str,secretGiverReciver]:
    global itterations
    itterations = itterations + 1
    names = list(santas.keys())
    shuffle(names)
    atemptedAssingments=[(name,names[(index+1)%len(names)]) for index,name in enumerate(names)] 
    for name in atemptedAssingments:
        if(santas[name[0]].doesReject(name[1])):
            return assignNames(santas)
    for name in atemptedAssingments:
        santas[name[0]].addReciver(name[1])
    return santas



def loadNamesFromFile(file :str) -> dict[str,secretGiverReciver]:
    with open(file,'r') as f:
        raw = f.read()
    lines = raw.split('\n')
    if lines[0] != 'Name,Email,Rejects':
        raise Exception("bad file")
    lines.pop(0)
    nameDict : dict[str,secretGiverReciver] = {}

    for line in lines:
        words = line.split(',')
        name = words[0]
        if name == '':
            continue
        email = words[1] if (len(words) > 1) else ''
        rejects = words[2] if (len(words) > 2) else ''
        nameDict[name] = secretGiverReciver(name,email,rejects)
    
    return nameDict


        
def makeAssingmentFolder(drawingName : str):
    pathname=f"{os.path.dirname(os.path.abspath(__file__))}\\{drawingName}s_asingments"
    if os.path.exists(pathname):
        tempfiles = os.listdir(pathname)
        for file in tempfiles:
            os.remove(pathname+"\\"+file)
    else:
        os.mkdir(pathname)
    return pathname
    


def main():
    santas = (loadNamesFromFile('example.csv'))
    santas = assignNames(santas)
    print(f"after {itterations} iterations it was decided that")
    assingmentFolder = makeAssingmentFolder("example")
    with open("gmailCreds.json",'r') as f:
        creds = json.loads(f.read())


    sendemail = creds['email']

    with smtplib.SMTP_SSL(creds['server'], creds['port']) as smtp_server:
        smtp_server.login(sendemail, creds['password'])

        for santaName in list(santas.keys()):
            santas[santaName].makeAnouncementFile(assingmentFolder)
            if '@' in santas[santaName].getEmail() and '.' in santas[santaName].getEmail(): #thats a good enough valid email regex right??
                smtp_server.sendmail(creds['email'],santas[santaName].getEmail(),santas[santaName].createAssingmentEmail('DeVries',sendemail))
            



if __name__ == '__main__':
    main()
