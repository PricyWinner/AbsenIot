import pandas as pd
import cv2
import urllib.request
import numpy as np
import os
from datetime import datetime
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
        print("there iss..")
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
    
    #cap = cv2.VideoCapture(0)
    
    while True:
        #success, img = cap.read()
        img_resp=urllib.request.urlopen(url)
        imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
        img=cv2.imdecode(imgnp,-1)
    # img = captureScreen()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    
        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
    
        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            print(matches)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            print(faceDis)
    # print(faceDis)
            matchIndex = np.argmin(faceDis)
            print(matchIndex)
            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
    # print(name)
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                markAttendance(name)
    
        cv2.imshow('Webcam', img)
        key=cv2.waitKey(5)
        if key==ord('q'):
            break
    cv2.destroyAllWindows()
    cv2.imread

def firebaseInit():
    # cred = credentials.ApplicationDefault()
    # firebase_admin.initialize_app(cred, {
    # 'projectId': project_id,
    # })
    cred = credentials.Certificate("abseniot-4c2f98454c78.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    doc_ref = db.collection(u'users').document(u'alovelace')
    doc_ref.set({
        u'first': u'Ada',
        u'last': u'Lovelace',
        u'born': 1815
    })
 
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList
 
 
def markAttendance(name):
    # print(f'marking attendance | {os.path} | {os.getcwd()}')
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