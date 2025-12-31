RC Patcher (SEPA XML Name Updater)

RC Patcher is a utility for automatically updating recipient names in SEPA XML (ISO 20022) payment files.

The script verifies company codes (Juridinių asmenų kodas) from the payment file against the official database of the Lithuanian State Enterprise Centre of Registers (VĮ Registrų centras). If necessary, it replaces the recipient's name with the officially registered one.

This helps avoid payment rejections by banks due to name/code mismatches without requiring changes to the data within your accounting system (e.g., 1C:Enterprise).
🚀 Features

    ⚡ High Performance: Processes large databases (CSV) in memory within seconds.

    🔒 Data Privacy: Works locally; financial data is never transmitted to the internet.

    🛠 ISO 20022 Compatible: Correctly handles XML Namespaces without breaking the file structure.

    🌍 Smart Filtering: Ignores foreign recipients (those not found in the Lithuanian registry), leaving their data untouched.

    📝 Flexibility: Supports creating a new file or overwriting the original one.

    🐞 Debug Mode: Detailed console logging for troubleshooting.

📋 Requirements

    OS: Windows (if using the .exe) or any OS with Python 3 installed.

    Database File: The current open data file JAR_IREGISTRUOTI.csv.

        You can download it from the Registrų centras website.

        Note: The file format must be CSV with a | (pipe) delimiter.

⚙️ Installation & Build
Option 1: Using Python (Source)
Bash

git clone https://github.com/your-username/rc-patcher.git
cd rc-patcher
python rc_patcher.py

Option 2: Building an EXE (For servers without Python)

For deployment on client machines or 1C servers, it is recommended to compile the script into a single executable:
Bash

pip install pyinstaller
pyinstaller --onefile rc_patcher.py

The rc_patcher.exe file will be generated in the dist folder.
💻 Usage

The utility is run from the command line.
Syntax
Bash

rc_patcher.exe <FOLDER_PATH> <XML_FILENAME> [OVERWRITE_MODE]

Parameters

    FOLDER_PATH: Full path to the directory containing the payment XML and the JAR_IREGISTRUOTI.csv file.

    XML_FILENAME: Name of the payment file (e.g., export.xml).

    OVERWRITE_MODE (Optional):

        1 (or true, overwrite) — The script overwrites the original file.

        0 (default) — The script creates a new file with the suffix _UPDATED.xml.

Examples
Bash

# Create a new file plat_UPDATED.xml (Safe Mode)
rc_patcher.exe "C:\BankExport" "plat.xml" 0

# Overwrite the original plat.xml (Integration Mode)
rc_patcher.exe "C:\BankExport" "plat.xml" 1

🔌 Integration with 1C:Enterprise

To automatically swap names when exporting payments from 1C, add the script execution call at the end of your export procedure (after WriteXML.Close()).

Example code in 1C (BSL):
Фрагмент кода

// ... (XML generation code finished, file closed)

// Path settings
FileDir = "C:\Exchange\"; // Path containing XML and CSV
XMLFileName = "sepa_payment.xml";
ExePath = FileDir + "rc_patcher.exe";

// Check if script exists
ScriptFile = New File(ExePath);
If ScriptFile.Exist() Then
    // Build command: exe "folder" "file" 1 (overwrite mode)
    // Important: Watch out for quotes if paths contain spaces
    Command = """" + ExePath + """ """ + FileDir + """ """ + XMLFileName + """ 1";
    
    // Run and wait for completion
    RunApp(Command, , True);
    
    Message("Recipient names updated using the Centre of Registers database.");
Else
    Message("rc_patcher script not found, sending file as is.");
EndIf;

🔍 How It Works (Logic)

    The script loads JAR_IREGISTRUOTI.csv into RAM (Hash Map).

    It parses the XML file and locates all transactions (CdtTrfTxInf).

    It extracts the recipient's code from the <Id><OrgId><Othr><Id> tag.

    It searches for this code in the loaded database.

        If found: Compares the name in the XML with the name in the database. If they differ, it replaces the content of the <Nm> tag with the official name.

        If not found: (e.g., a foreign company or an individual) — leaves the record unchanged.

    It saves the result.

⚠️ Important Notes

    Encoding: The script expects files in UTF-8 encoding.

    Foreign Companies: If a recipient's code is not found in the Lithuanian database (e.g., a Bulgarian company code), the script will log a NOT FOUND message and skip that transaction. This is expected behavior.

    CSV Format: Ensure the Centre of Registers file uses the | (vertical bar) delimiter.

📄 License

MIT License. Free to use and modify.