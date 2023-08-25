from flask import *
import requests
import os
import uuid
from datetime import *
import os
app = Flask(__name__)

@app.route('/')
def success():
   return render_template('index.html')

@app.route('/upload',methods = ['POST', 'GET'])
def upload():
   output_folder = 'output1'
   if request.method == 'POST':
      user = request.form['json-output']
      user = user.replace("\n","")
      id = uuid.uuid1()
      filename = f"{output_folder}/{id}/upload-{id}.txt"
      os.makedirs(os.path.dirname(filename), exist_ok=True)
      with open(filename, 'w') as f:
         f.write(user)    
      
      return redirect(url_for('success'))
   
   
if __name__ == '__main__':
   app.run(debug = True)