from flask import *
import shutil
import os
import uuid
import csv
import json

app = Flask(__name__)

line_count = 0
data = {}

def writeJSON(id,filename):
    print(id)
    op = f'uploads/{id}/table-mappings/table-mappings-{filename.split("-")[1].split(".")[0]}.json'
    print(op)
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

    generate_table_mappings(id,split_out_dir)

def generate_table_mappings(id,split_out_dir):
    if("/" in split_out_dir):
        separator = "/"
    else:
        separator = "\\"
    listOfFiles = os.listdir(split_out_dir)
    for entry in listOfFiles:
        data['rules'] = []
        if (entry.startswith("include") or entry.startswith("raw")):
            createJSON(split_out_dir+separator+entry,"include")
            writeJSON(id, entry)
        elif (entry.startswith("exclude")):
            createJSON(split_out_dir+separator+entry, "exclude")
            writeJSON(id, entry)
    print("CSV files created for separate schemas.")

aws_cli_template = "aws-cmd-template"
validation_template = "validation_template.json"

def generate_aws_cli_cmds(input_file, output_file, placeholder, replacement):
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

def zip_files(output_filename, dir_name):
    zip_res = shutil.make_archive(output_filename, 'zip', dir_name)
    print(zip_res)
    return zip_res

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/upload',methods = ['POST', 'GET'])
def upload():
    output_folder = 'uploads'
    if request.method == 'POST':
        try:
            user = request.form['json-output']
            json_split = request.form['json_split']
        except:
            json_split = "0"
        user = user.replace("\n","")
        user = user.rstrip()
        id = uuid.uuid1()
        raw_filename = f"{output_folder}/{id}/raw-{id}.csv"
        os.makedirs(os.path.dirname(raw_filename), exist_ok=True)
        os.makedirs(os.path.dirname(f"uploads/{id}/aws-cli/aws-cli-cmds.sh"), exist_ok=True)
        os.makedirs(f"./uploads/{id}/validations", exist_ok=True)
        os.makedirs(f"./uploads/{id}/split_files", exist_ok=True)

        with open(raw_filename, 'w') as f:
            f.write(user)  
        if json_split == '1':
            json_split = True
            split_schema_file(raw_filename,id,output_folder)
        else:
            json_split = False
            splitfile_dir=f'{output_folder}/{id}/split_files'
            shutil.copy(raw_filename,splitfile_dir)
            generate_table_mappings(id,splitfile_dir)
        
        with open(raw_filename) as file:
            schema_names=set()
            for line in file:
                schema_name = line.split(',')[0]
                schema_names.add(schema_name)

            for schema_name in schema_names:
                generate_validation(validation_template, f"./uploads/{id}/validations/validations-{schema_name}.json", "#SCHEMA_NAME#", schema_name)
                generate_aws_cli_cmds(aws_cli_template, f"./uploads/{id}/aws-cli/aws-cli-cmds.sh", "#SCHEMA_NAME#", schema_name)
        
        zip_res = zip_files(f"downloads/{id}/{id}-{len(schema_names)}-schemas", f"{output_folder}/{id}")

        return send_file(f'downloads/{id}/{os.path.basename(zip_res)}', as_attachment=True)
        # return render_template('index.html', download_link=True, zip_file_name=f'{id}/{os.path.basename(zip_res)}')

if __name__ == '__main__':
   app.run(debug = True, host="0.0.0.0", port=8080)
