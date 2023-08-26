from flask import *
import requests
import os
import uuid
import csv
import json

app = Flask(__name__)

line_count = 0
data = {}

def writeJSON(id,filename):
    op = f'uploads/{id}/table-mappings/table-mapping-{filename.split("-")[1].split(".")[0]}-with-pk.json'
    os.makedirs(os.path.dirname(op), exist_ok=True)
    with open(op, 'w') as outfile:
        json.dump(data, outfile)

def createJSON(csvfile,action):
    global line_count
    with open(csvfile) as file:
       csv_reader = csv.reader(file, delimiter=',')
       next(csv_reader, None)
       for row in csv_reader:
           counter = str(line_count + 1)
           data['rules'].append({
               "rule-type": "selection",
               "rule-id": counter,
               "rule-name": counter,
               "object-locator": {
                   "schema-name": row[0].strip(),
                   "table-name": row[1].strip()
               },
               "rule-action": action
           })
           line_count += 1

def split_schema_file(filename,id,output_folder):
    
   #  output_folder = 'output'
    schema_tables = {}
    split_out_dir = f'{output_folder}/{id}/split_files'
    os.makedirs(split_out_dir, exist_ok=True)
    with open(filename, 'r') as file:
        for line in file:
            schema, table = line.strip().split(',')
            if schema in schema_tables:
                schema_tables[schema].append(table)
            else:
                schema_tables[schema] = [table]

    for schema, tables in schema_tables.items():
        with open(f'{split_out_dir}/include-{schema}.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Schema', 'Table'])
            csvwriter.writerows([(schema, table) for table in tables])

    if("/" in split_out_dir):
        separator = "/"
    else:
        separator = "\\"
    listOfFiles = os.listdir(split_out_dir)
    for entry in listOfFiles:
      #   data = {}
        data['rules'] = []
        if (entry.startswith("include")):
            createJSON(split_out_dir+separator+entry,"include")
            writeJSON(id, entry)
        elif (entry.startswith("exclude")):
            createJSON(split_out_dir+separator+entry, "exclude")
            writeJSON(id, entry)
    print("CSV files created for separate schemas.")
aws_cli_template = "aws-cmd-template"
validation_template = "validation_template.json"

def replace_placeholder(input_file, output_file, placeholder, replacement):
    try:
        with open(input_file, 'r') as f:
            content = f.read()
            modified_content = content.replace(placeholder, replacement)

        with open(output_file, 'a') as f:
            f.write(modified_content)
        
        print("Replacement successful. Modified content saved to", output_file)
    except Exception as e:
        print("An error occurred:", e)

def generate_validation(input_file, output_file, placeholder, replacement):
    try:
        with open(input_file, 'r') as f:
            content = f.read()
            modified_content = content.replace(placeholder, replacement)

        with open(output_file, 'w') as f:
            f.write(modified_content)
        
        print("Replacement successful. Modified content saved to", output_file)
    except Exception as e:
        print("An error occurred:", e)

@app.route('/')
def success():
   return render_template('index.html')

@app.route('/upload',methods = ['POST', 'GET'])
def upload():
   output_folder = 'uploads'
   if request.method == 'POST':
      user = request.form['json-output']
      user = user.replace("\n","")
      id = uuid.uuid1()
      filename = f"{output_folder}/{id}/raw-{id}.txt"
      os.makedirs(os.path.dirname(filename), exist_ok=True)
      os.makedirs(os.path.dirname(f'uploads/{id}/aws-cli/{filename.split("-")[1].split(".")[0]}'), exist_ok=True)
      os.makedirs(os.path.dirname(f'uploads/{id}/table-validations/{filename.split("-")[1].split(".")[0]}'), exist_ok=True)


      with open(filename, 'w') as f:
         f.write(user)    
      split_schema_file(filename,id,output_folder)

      with open(filename) as file:
         schema_names=set()
         for line in file:
            schema_name = line.split(',')[0]
            schema_names.add(schema_name)

         for schema_name in schema_names:
            generate_validation(validation_template, f"./uploads/{id}/table-validations/validations-{schema_name}.json", "#SCHEMA_NAME#", schema_name)
            replace_placeholder(aws_cli_template, f"./uploads/{id}/aws-cli/aws-cli-cmds.sh", "#SCHEMA_NAME#", schema_name)

      return redirect(url_for('success'))
   
if __name__ == '__main__':
   app.run(debug = True)

   