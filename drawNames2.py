import random
import os
import smtplib
import json
from createEmail import emailCreator
import argparse
import datetime


verbose_print=True

def printV(str):
    if verbose_print:
        print(str)

class santaObj:
    def __init__(self,name: str,email : str = '',rejects : str | list[str] = ''):
        self.name = name
        self.email = email if email != '' else 'N/A'
        if(type(rejects) == str):
            self.rejects = [rejects]
        else:
            self.rejects = rejects
        self.giftee = 'NoOne?'

    def setGiftee(self,giftee: str):
        self.giftee = giftee

    def getRejects(self) -> list[str]:
        return self.rejects
    
    def getGiftee(self) -> str:
        return self.giftee
    
    def getEmail(self) -> str:
        return self.email
    
    def getName(self) -> str:
        return self.name
    

def loadNamesFromFile(file :str) -> list[santaObj]:
    with open(file,'r') as f:
        raw = f.read()
    lines = raw.split('\n')
    if lines[0] != 'Name,Email,Rejects':
        raise Exception("bad file")
    lines.pop(0)
    santas = []
    

    for line in lines:
        words = line.split(',')
        name = words[0]
        if name == '':
            continue
        email = words[1] if (len(words) > 1) else ''
        lineIndex=2
        rejects = []
        while (len(words) > lineIndex):
            rejects.append(words[lineIndex])
            lineIndex=lineIndex+1
        santas.append(santaObj(name,email,rejects))
    
    return santas


def getSantaByName(santaList: list[santaObj],name: str) -> santaObj:
    for santa in santaList:
        if santa.getName() == name:
            return santa
    return None


def makeNameTrain(santaList: list[santaObj]) ->tuple[str,str]:
    nameList=[santa.getName() for santa in santaList]
    picklist=[]
    
    head=nameList[random.randint(0,len(nameList)-1)]
    picker=head
    nameList.pop(nameList.index(picker))
    while(len(nameList)):
        pickerSanta = getSantaByName(santaList,picker)
        indexes = [_ for _ in range(len(nameList))]
        random.shuffle(indexes)
        index=0
        for _ in range(0,len(indexes)):
            if(not nameList[indexes[index]] in pickerSanta.getRejects()):
                pickee=nameList[indexes[index]]
                break
            index=index+1
        if(index == len(indexes)):
            print(f"Could not find a match for {picker} retry")
            return makeNameTrain(santaList)

        pickerSanta.setGiftee(pickee)
        picklist.append((picker,pickee))
        picker=pickee
        nameList.pop(nameList.index(picker))
    picklist.append((picker,head))
    return picklist
    

def makeAssignmentFolder(drawingName : str):
    pathname=f"{os.path.dirname(os.path.abspath(__file__))}\\{drawingName.replace(' ','_').replace(':','-')}"
    if os.path.exists(pathname):
        tempfiles = os.listdir(pathname)
        for file in tempfiles:
            os.remove(pathname+"\\"+file)
    else:
        os.mkdir(pathname)
    return pathname

def saveRedundantCopy(path: str,drawingsName: str,train: tuple[str,str]):

    with open(f"{path}\\{drawingsName.replace(' ','_').replace(':','-')}_master_copy.txt",'w+') as bigfile:
        bigfile.write(f"the drawing for {drawingsName} was as follows\n")

        for car in train:
            bigfile.write(f"{car[0]} picked {car[1]}\n")
            with open(f"{path}\\{car[0]}s_assingment.txt",'w') as f:
                f.write(f"FOR {car[0].upper()}S EYES ONLY DONT BE A CHEATER AND PEEK\n\n\n\n\n\n\n")
                f.write(f"{car[0]} you are getting a gift for {car[1]}")




def main():
    global verbose_print
    parser = argparse.ArgumentParser(prog='Secret santa picker')
    parser.add_argument('--name','-n',type=str, help="Name of this little escipade",default=datetime.datetime.now().strftime("Drawing at %I:%M%p on %B %d %Y"))
    parser.add_argument('-list','-l',type=str, help="file to create strings for",default="example.csv")
    parser.add_argument('--creds','-c',help="email credentials")
    parser.add_argument('-v','--verbose',action='store_true')
    args = parser.parse_args()

    verbose_print = args.verbose
    theList=args.list
    name=args.name
    if(args.creds):
        sendEmail=True
    else:
        sendEmail=False

    santas = loadNamesFromFile(theList)
    listFolder=makeAssignmentFolder(name)
    santaTrain=makeNameTrain(santas)
    saveRedundantCopy(listFolder,name,santaTrain)
    for santa in santas:
        printV(f"{santa.getName()} has a email of: {santa.getEmail()} and rejects {[name for name in santa.getRejects()]}")
    for car in santaTrain:
        printV(f"{car[0]} picked {car[1]}")

    if(sendEmail):
        with open(args.creds,'r') as f:
            creds = json.loads(f.read())

        theCreator=emailCreator('LetterTemplate.txt')
        sendemail = creds['email']

        with smtplib.SMTP_SSL(creds['server'], creds['port']) as smtp_server:
            smtp_server.login(sendemail, creds['password'])
            for car in santaTrain:
                santa: santaObj = getSantaByName(santas,car[0])
                if '@' in santa.getEmail() and '.' in santa.getEmail(): #thats a good enough valid email regex right??
                    body=theCreator.createBody(car[0],car[1],name)
                    email=theCreator.makeEmail(sendemail,[santa.getEmail()],f"{name} secret santa drawing",body)
                    smtp_server.sendmail(creds['email'],santa.getEmail(),email)



if __name__ == "__main__":

    main()