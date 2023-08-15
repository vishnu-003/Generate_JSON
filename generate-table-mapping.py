schemas_file = "src.txt"
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

with open(schemas_file) as file:
    for i, line in enumerate(file):
        schema_name, table_name = line.strip().split(",")
        output_filename = f"{table_mapping_out}/table-mappings-{schema_name}.json"
        
        replacements = {
            "#SCHEMA_NAME#": schema_name,
            "#TABLE_NAME#": table_name,
            "#RULE_ID#":str(2010100 + i),  # Increment i to get unique rule-id
            "#RULE_NAME#": str(2010100 + i)  # Increment i to get unique rule-name
            
        }
        
        replace_placeholders(table_mapping_template, output_filename, replacements)

print("Table mapping JSON files generated and stored in", table_mapping_out)
