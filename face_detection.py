from getpass import getuser
from time import time
import pandas as pd
import cv2
import urllib.request
import numpy as np
import os
from datetime import datetime, timezone
from datetime import date
import face_recognition
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def main():
    firebaseInit()
    path = r'C:\\Alex Binus\\Iot\\Absen\\image_folder'
    url='http://192.168.50.237/cam-hi.jpg'
    ##'''cam.bmp / cam-lo.jpg /cam-hi.jpg / cam.mjpeg '''
    
    if 'Attendance.csv' in os.listdir(os.path.join(os.getcwd(),'')):
        os.remove("Attendance.csv")
    # else:
    df=pd.DataFrame(list())
    df.to_csv("Attendance.csv")
        
    
    images = []
    classNames = []
    myList = os.listdir(path)
    print(myList)
    for cl in myList:
        print(cl)
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    print(classNames)
    
    encodeListKnown = findEncodings(images)
    print('Encoding Complete')
    
    while True:
        img_resp=urllib.request.urlopen(url)
        imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
        img=cv2.imdecode(imgnp,-1)
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    
        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
    
        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            print(matches)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            print(faceDis)
            matchIndex = np.argmin(faceDis)
            print(matchIndex)
            if matches[matchIndex]:
                name = classNames[matchIndex]
                name2 = getUsername(name)
                print(name2)
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name2, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                markAttendance(name)
    
        cv2.imshow('Webcam', img)
        key=cv2.waitKey(5)
        if key==ord('q'):
            break
    cv2.destroyAllWindows()
    cv2.imread

def firebaseInit():
    cred = credentials.Certificate("abseniot-4c2f98454c78.json")
    firebase_admin.initialize_app(cred)
    global db
    db = firestore.client()
    # doc_ref = db.collection(u'users').document(u'alovelace')
    # doc_ref.set({
    #     u'first': u'Ada',
    #     u'last': u'Lovelace',
    #     u'born': 1815
    # })

def writeFirestore(name):
    today = date.today()
    currentDate = today.strftime("%d-%m-%y")
    now = datetime.now(timezone.utc)
    # nowSrtring = now.strftime('%H:%M:%S')

    print(currentDate)
    try:
        doc_ref = db.collection(u'days').document(currentDate)
        user_ref = doc_ref.collection(u'user').document(name)
        user_ref.update({
            u'time': now,
            u'uid': name,
        })
    except:
        doc_ref = db.collection(u'days').document(currentDate)
        user_ref = doc_ref.collection(u'user').document(name)
        user_ref.set({
            u'time': now,
            u'uid': name,
        })
        print('belum ada entry hari ini')
    else: 
        print('sudah ada entry hari ini')

def getUsername(id):
    
    doc_ref = db.collection(u'users').document(id)
    doc = doc_ref.get()
    if doc.exists:
        # print(id)
        # print(f'Document data: {doc.to_dict()["name"]}')
        newName = doc.to_dict()["name"]
        return(newName)
    else:
        print(u'No such document!')

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList
 
 
def markAttendance(name):
    writeFirestore(name)
    try:
        with open("Attendance.csv", 'r+') as f:
            myDataList = f.readlines()
            nameList = []
            for line in myDataList:
                entry = line.split(',')
                nameList.append(entry[0])
                if name not in nameList:
                    now = datetime.now()
                    dtString = now.strftime('%H:%M:%S')
                    f.writelines(f'\n{name},{dtString}')
    except FileNotFoundError:
        print('file not found error')
 
main()