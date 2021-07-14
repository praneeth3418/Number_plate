import cv2
import os
import matplotlib.pyplot as plt
import easyocr
import json
import requests
import xmltodict
from logging import debug
from flask import Flask, render_template, request


def number_plate(image):
     model=cv2.CascadeClassifier("haarcascade_russian_plate_number.xml")
     if image is not None:
       cimg=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
       vet=model.detectMultiScale(cimg,1.1,4)
       x1 ,y1, w, h =vet[0]
       plate=image[y1:y1+h,x1:x1+w]
       reader = easyocr.Reader(['en'])
       result = reader.readtext(plate)
       num_plate=result[0][-2]
       fin_number=""
       for x in num_plate:
         if x!=" ":
           fin_number += x
       response = requests.get("http://www.regcheck.org.uk/api/reg.asmx/CheckIndia?RegistrationNumber={0}&username=<user_name>".format(str(fin_number)))    
       data_dict = xmltodict.parse(response.content)
       json_data = json.dumps(data_dict)
       resultnum=json.loads(json.loads(json_data)['Vehicle']['vehicleJson'])    
       return fin_number , resultnum
     else:
       return "No number plate found."



app=Flask(__name__)
root=os.path.dirname(os.path.abspath(__file__))
fname=None
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=["POST"])
def upload():
    global fname
    path=os.path.join(root, 'static/')
    if not os.path.isdir(path):
        os.mkdir(path)
   
    for file in request.files.getlist("user_img"):
        f_name=file.filename
        dst="/".join([path, f_name])
        fname = f_name
        file.save(dst)
        return render_template('index.html', data=f_name)

@app.route('/info')
def get_info():
    number, a=number_plate(cv2.imread(f"static/{fname}"))
    number = number
    Owner = a['Owner']
    Description = a['ModelDescription']
    Model = Description['CurrentTextValue']
    RegistrationDate = a['RegistrationDate']
    Insurance = a['Insurance']
    Location = a['Location']
    VechileIdentificationNumber = a['VechileIdentificationNumber']
    EngineNumber = a['EngineNumber']
    FuelType = a['FuelType']
    FuelType = FuelType["CurrentTextValue"]
    Fitness = a['Fitness']
    st=f'''Owner ====>{Owner}+Vehicle Number ===> {number}+Model ====>{Model}+Registration date ====>{RegistrationDate}+Engine Number====>
    {EngineNumber}+Vehicle Identification Number ====>{VechileIdentificationNumber}+Insurance ====>{Insurance}+Fuel Type ====>{FuelType}+Fitness ====>{Fitness}+Location ====>{Location}'''
    return st


app.run(debug=True, port=5001)