import json
schemas_file = "src2.txt"
table_mapping_out = "./output/table-mappings"
table_mapping_template = "table-mapping-template.json"

def replace_placeholders(input_file, output_file, replacements):
    try:
        with open(input_file, 'r') as f:
            content = f.read()
            
            for placeholder, replacement in replacements.items():
                content = content.replace(placeholder, replacement)

        with open(output_file, 'w') as f:
            f.write(content)
        
        print("Replacement successful. Modified content saved to", output_file)
    except Exception as e:
        print("An error occurred:", e)

schema_tables = {}  # Dictionary to store tables for each schema

with open(schemas_file) as file:
    for i, line in enumerate(file):
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        
        parts = line.split(",")
        schema_name = parts[0]
        table_names = parts[1:]
        
        
        if schema_name not in schema_tables:
            schema_tables[schema_name] = []
        
        schema_tables[schema_name].extend(table_names)
        

# Read the template JSON file
with open(table_mapping_template) as f:
    template = json.load(f)

# Generate a single JSON file for each schema with templates for each table
for schema_name, table_names in schema_tables.items():
    output_filename = f"{table_mapping_out}/table-mappings-{schema_name}.json"

    #Create a copy of the template JSON object
    new_template = template.copy()
    

    # # Update the copy with the table names for the current schema
    new_template["rules"] = []
    
    
    for table_name in table_names:
        new_rule = {
            "rule-type":"selection",
            "rule-action":"include",
            "filters":[],
            "schema": schema_name,
            "table": table_name,
            "rule_id": str(201000+i),  # Increment i to get unique rule-id
            "rule_name": str(201000+i)# Increment i with a different value for unique rule-name
        }
    
        
        i=i+1
        new_template["rules"].append(new_rule)
      
    # Write the updated JSON object to a file
    with open(output_filename, 'w') as f:
        json.dump(new_template, f, indent=4)

print("Table mapping JSON files generated and stored in", table_mapping_out)
