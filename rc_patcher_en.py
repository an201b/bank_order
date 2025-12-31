import sys
import os
import csv
import xml.etree.ElementTree as ET

def print_help():
    """Prints help on how to use the script."""
    print("=" * 60)
    print(" RC Patcher - Updating names in SEPA XML using Registru Centras database")
    print("=" * 60)
    print("Usage:")
    print("  rc_patcher.exe <FOLDER> <XML_FILE> [OVERWRITE_MODE]")
    print("\nParameters:")
    print("  1. FOLDER         : Full path to the folder containing CSV and XML files.")
    print("  2. XML_FILE       : Name of the payment file (e.g., export.xml).")
    print("  3. OVERWRITE_MODE : (Optional) 1 - Overwrite the original file.")
    print("                                 0 - Create a new file (suffix _UPDATED).")
    print("                                 Default: 0 (Creates a new file).")
    print("\nExamples:")
    print('  rc_patcher.exe "C:\\Bank" "export.xml" 1       (Overwrites export.xml)')
    print('  rc_patcher.exe "C:\\Bank" "export.xml" 0       (Creates export_UPDATED.xml)')
    print("=" * 60)

def load_rc_data(csv_path):
    """Reads JAR_IREGISTRUOTI CSV file and creates a dictionary {code: name}."""
    company_map = {}
    print(f"--- Reading RC database: {csv_path}")
    
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='|', quotechar='"')
            header = next(reader, None)
            for row in reader:
                if len(row) > 1:
                    code = row[0].strip()
                    name = row[1].strip()
                    company_map[code] = name
        print(f"--- Companies loaded: {len(company_map)}")
        return company_map
    except FileNotFoundError:
        print(f"ERROR: Database file {csv_path} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR reading CSV: {e}")
        sys.exit(1)

def update_payment_file(xml_path, company_map, overwrite_mode):
    """Opens XML, updates names, and saves the result (WITH DEBUGGING)."""
    print(f"--- Processing file: {xml_path}")
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Namespace handling
        if '}' in root.tag:
            ns_url = root.tag.split('}')[0].strip('{')
            ns = {'ns': ns_url}
            ET.register_namespace('', ns_url)
        else:
            ns = {}
            
        replaced_count = 0
        # Looking for all transactions
        transactions = root.findall('.//ns:CdtTrfTxInf', ns) if ns else root.findall('.//CdtTrfTxInf')
        
        print(f"--- Transactions (payments) found: {len(transactions)}")

        for i, tx in enumerate(transactions):
            # Looking for Creditor
            cdtr = tx.find('ns:Cdtr', ns) if ns else tx.find('Cdtr')
            if cdtr is None:
                print(f"  [Tx {i+1}] Cdtr (Creditor) block not found")
                continue
                
            # More reliable ID search (direct path)
            # Path: Id -> OrgId -> Othr -> Id
            org_id_tag = cdtr.find('ns:Id/ns:OrgId/ns:Othr/ns:Id', ns) if ns else cdtr.find('Id/OrgId/Othr/Id')
            
            # If not found via direct path, try deep search (in case of XML variations)
            if org_id_tag is None:
                 org_id_tag = cdtr.find('.//ns:Id/ns:OrgId/ns:Othr/ns:Id', ns) if ns else cdtr.find('.//Id/OrgId/Othr/Id')

            if org_id_tag is not None and org_id_tag.text:
                code = org_id_tag.text.strip()
                current_xml_name_tag = cdtr.find('ns:Nm', ns) if ns else cdtr.find('Nm')
                current_xml_name = current_xml_name_tag.text if current_xml_name_tag is not None else "(no name)"
                
                print(f"  [Tx {i+1}] Code in XML: '{code}' | Name in XML: '{current_xml_name}'")
                
                if code in company_map:
                    correct_name = company_map[code]
                    print(f"      -> FOUND in RC database. Correct name: '{correct_name}'")
                    
                    if current_xml_name != correct_name:
                        if current_xml_name_tag is not None:
                            print(f"      -> CHANGING: {current_xml_name} -> {correct_name}")
                            current_xml_name_tag.text = correct_name
                            replaced_count += 1
                        else:
                            print("      -> Error: Nm tag missing, nowhere to write the name.")
                    else:
                        print("      -> Names match, no replacement needed.")
                else:
                    print(f"      -> NOT FOUND in CSV file. Skipping.")
            else:
                print(f"  [Tx {i+1}] No OrgId in this transaction (possibly payment to individual or structure error).")
        
        # Saving
        if overwrite_mode:
            output_path = xml_path
            mode_str = "OVERWRITE"
        else:
            output_path = xml_path.replace('.xml', '_UPDATED.xml')
            mode_str = "NEW FILE"
            
        tree.write(output_path, encoding='UTF-8', xml_declaration=True)
        print(f"--- Done. Records updated: {replaced_count}")
        print(f"--- Mode: {mode_str}. Saved to: {output_path}")

    except ET.ParseError:
        print("ERROR: Invalid XML format.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR processing XML: {e}")
        sys.exit(1)

def main():
    # If no arguments or too few - print help
    if len(sys.argv) < 3:
        print_help()
        # Do not exit with error, just finish normally after showing help
        return

    folder_path = sys.argv[1]
    payment_filename = sys.argv[2]
    
    # Processing 3rd parameter (Overwrite)
    overwrite = False # Default is creating a new file
    if len(sys.argv) >= 4:
        arg3 = sys.argv[3].lower()
        if arg3 in ['1', 'true', 'y', 'yes', 'overwrite']:
            overwrite = True
    
    csv_file_path = os.path.join(folder_path, "JAR_IREGISTRUOTI.csv")
    payment_file_path = os.path.join(folder_path, payment_filename)
    
    if not os.path.exists(csv_file_path):
        print(f"ERROR: CSV file not found: {csv_file_path}")
        sys.exit(1)
        
    rc_map = load_rc_data(csv_file_path)
    
    if not os.path.exists(payment_file_path):
        print(f"ERROR: Payment file not found: {payment_file_path}")
        sys.exit(1)
        
    update_payment_file(payment_file_path, rc_map, overwrite)

if __name__ == "__main__":
    main()