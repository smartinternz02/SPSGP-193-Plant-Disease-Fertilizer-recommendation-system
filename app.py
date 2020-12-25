import requests
from keras.preprocessing import image
from tensorflow.keras.models import load_model
import numpy as np
import pandas as pd
import tensorflow as tf
from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename
from tensorflow.python.keras.backend import set_session


app = Flask(__name__)
global sess
sess = tf.Session()
global graph
graph=tf.compat.v1.get_default_graph()
set_session(sess)

#load both the vegetable and fruit models
model = load_model("vegetable.h5")
model1=load_model("fruit.h5")

#integrate the api to retrieve the data based on email
def check(email):
    url = "https://xtcx2dz8nf.execute-api.us-east-1.amazonaws.com/plant-disease/login?email="+email
    status = requests.request("GET",url)
    print(status.json())
    return status.json()

#home page
@app.route('/')
def home():
    return render_template('home.html')


#registration page
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/afterreg', methods=['POST'])
def afterreg():
    x = [x for x in request.form.values()]
    print(x)
    params = "name="+x[0]+"&email="+x[1]+"&phone="+x[2]+"&password="+x[3]
    #check if the user is already registered or not
    if('errorType' in check(x[1])):
        url = " https://xtcx2dz8nf.execute-api.us-east-1.amazonaws.com/plant-disease?"+params
        response = requests.get(url)
        return render_template('register.html', pred="Registration Successful, please login using your details")
    else:
        return render_template('register.html', pred="You are already a member, please login using your details")

#login page
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/afterlogin',methods=['POST'])
def afterlogin():
    user = request.form['uname']
    passw = request.form['psw']
    print(user,passw)
    data = check(user)
    #check with the valid credentials
    if('errorType' in data):
        return render_template('login.html', pred="The username is not found, recheck the spelling or please register.")
    else:
        if(passw==data['password']):
            return redirect(url_for('prediction'))
        else:
            return render_template('login.html', pred="Login unsuccessful. You have entered the wrong password.") 
    
#prediction page
@app.route('/prediction')
def prediction():
    return render_template('predict.html')

@app.route('/predict',methods=['POST'])		
def predict():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['image']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)
        img = image.load_img(file_path, target_size=(128, 128))
        
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        plant=request.form['plant']
        print(plant)
        if(plant=="vegetable"):
            with graph.as_default():
                set_session(sess)
                preds = model.predict_classes(x)
            print(preds)
            df=pd.read_excel('precautions - veg.xlsx')
            print(df.iloc[preds[0]]['caution'])
        else:
            with graph.as_default():
                set_session(sess)
                preds = model1.predict_classes(x)
                
            df=pd.read_excel('precautions - fruits.xlsx')
            print(df.iloc[preds[0]]['caution'])
            
        
        return df.iloc[preds[0]]['caution']
    
@app.route('/logout')
def logout():
    return render_template('logout.html')
    
if __name__ == "__main__":
    app.run(debug=True)
