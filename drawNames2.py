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

def loadNamesFromFile(file :str) -> list[dict[str]]:
    with open(file,'r') as f:
        raw = f.read()
    lines = raw.split('\n')
    if 'Name,Email,Rejects' not in lines[0]:
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
        santas.append({"name": name, "email" : email, "rejects": rejects})
    
    return santas




def makeNameTrain(santaList: list[dict[str]]) ->list[tuple[dict[str],dict[str]]]:
    nameList=santaList.copy() #list assingments also pass by ref
    picklist : list[tuple[dict[str],dict[str]]] =[]
    
    head=nameList[random.randint(0,len(nameList)-1)]
    picker=head
    nameList.pop(nameList.index(picker))
    while(len(nameList)):
        indexes = [_ for _ in range(len(nameList))]
        random.shuffle(indexes)
        index=0
        for _ in range(0,len(indexes)):
            if(not nameList[indexes[index]]['name'] in picker['rejects']):
                pickee=nameList[indexes[index]]
                break
            index=index+1
        if(index == len(indexes)):
            print(f"Could not find a match for {picker['name']} retry")
            return makeNameTrain(santaList)

        picker["giftee"] = pickee
        picklist.append((picker,pickee))
        picker=pickee
        nameList.pop(nameList.index(picker))
    if(head['name'] in picker['rejects']):
        print(f"Could not find a match for {picker['name']} retry")
        return makeNameTrain(santaList)
    pickee = head
    picker["giftee"] = pickee
    picklist.append((picker,pickee))

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

def saveRedundantCopy(path: str,drawingsName: str,theList: str,train: tuple[str,str]):

    with open(theList,'r') as f:
        with open(f"{path}\\theList.csv","w+") as f2:
            f2.write(f.read())
    with open(f"{path}\\{drawingsName.replace(' ','_').replace(':','-')}_master_copy.txt",'w+') as bigfile:
        bigfile.write(f"the drawing for {drawingsName} was as follows\n")


        for car in train:
            bigfile.write(f"{car[0]['name']} picked {car[1]['name']}\n")
            with open(f"{path}\\{car[0]['name']}s_assingment.txt",'w') as f:
                f.write(f"FOR {car[0]['name'].upper()}S EYES ONLY DONT BE A CHEATER AND PEEK\n\n\n\n\n\n\n")
                f.write(f"{car[0]['name']} you are getting a gift for {car[1]['name']}")


def validateList(santaList: list[dict[str]]) -> bool:
    validList=True
    giverlist=[santa['name'] for santa in santaList]
    for santa in santaList:
        for reject in santa['rejects']:
            if reject not in giverlist:
                print(f"ERROR: {santa['name']} rejects {reject} who is not in this drawing")
                validList=False
    return validList


def main():
    global verbose_print
    parser = argparse.ArgumentParser(prog='Secret santa picker')
    parser.add_argument('--name','-n',type=str, help="Name of this little escipade",default=datetime.datetime.now().strftime("%I:%M%p on %B %d %Y"))
    parser.add_argument('--list','-l',type=str, help="file to create strings for",default="example.csv")
    parser.add_argument('--templateLetter','-t',type=str, help="file to create strings for",default="Example_Message.txt")
    parser.add_argument('--creds','-c',help="email credentials")
    parser.add_argument('--verbose','-v',action='store_true')
    #parser.add_argument()
    args = parser.parse_args()

    verbose_print = args.verbose
    theList=args.list
    drawingName=args.name
    letterTemplate=args.templateLetter
    if(args.creds):
        sendEmail=True
    else:
        sendEmail=False

    santas = loadNamesFromFile(theList)
    for santa in santas:
        printV(f"{santa['name']} has a email of: {santa['email']} and rejects {[name for name in santa['rejects']]}")

    if not validateList(santas):
        return


    listFolder=makeAssignmentFolder(drawingName)
    santaTrain=makeNameTrain(santas)
    saveRedundantCopy(listFolder,drawingName,theList,santaTrain)

    for car in santaTrain:
        printV(f"{car[0]['name']} picked {car[1]['name']}")

    if(sendEmail):
        with open(args.creds,'r') as f:
            creds = json.loads(f.read())

        theCreator=emailCreator(letterTemplate)
        sendemail = creds['email']

        with smtplib.SMTP_SSL(creds['server'], creds['port']) as smtp_server:
            smtp_server.login(sendemail, creds['password'])
            for car in santaTrain:
                if '@' in car[0]['email'] and '.' in car[0]['email']: #thats a good enough valid email regex right??
                    email=theCreator.createEmail(drawingName,creds['email'],car[0],car[1]['name'])
                    smtp_server.sendmail(creds['email'],car[0]['email'],email)



if __name__ == "__main__":

    main()