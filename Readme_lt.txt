RC Patcher (SEPA XML Gavėjų Pavadinimų Atnaujinimas)

RC Patcher – tai įrankis, skirtas automatiškai atnaujinti gavėjų pavadinimus SEPA XML (ISO 20022) mokėjimų failuose.

Skriptas sutikrina mokėjimo faile esančius įmonių kodus (Juridinių asmenų kodas) su oficialia VĮ Registrų centras duomenų baze. Prireikus, gavėjo pavadinimas pakeičiamas į oficialiai registruotą.

Tai padeda išvengti mokėjimų atmetimo banke dėl pavadinimo ir kodo nesutapimo, nekeičiant duomenų apskaitos sistemoje (pvz., „1C:Primonė“).
🚀 Galimybės

    ⚡ Didelis našumas: Apdoroja dideles duomenų bazes (CSV) atmintyje per kelias sekundes.

    🔒 Duomenų saugumas: Veikia lokaliai, finansiniai duomenys niekada neperduodami į internetą.

    🛠 Suderinamumas su ISO 20022: Korektiškai dirba su XML „Namespaces“ (vardų sritimis), nepažeidžiant failo struktūros.

    🌍 Išmanus filtravimas: Ignoruoja užsienio gavėjus (kurių nėra Lietuvos registre), palikdamas jų duomenis nepakeistus.

    📝 Lankstumas: Palaiko naujo failo sukūrimo arba originalaus failo perrašymo režimus.

    🐞 „Debug“ režimas: Išsamus procesų registravimas konsolėje klaidų paieškai.

📋 Reikalavimai

    OS: „Windows“ (jei naudojamas sukompiliuotas .exe) arba bet kuri OS su įdiegtu „Python 3“.

    Duomenų bazės failas: Aktualus atvirų duomenų failas JAR_IREGISTRUOTI.csv.

        Atsisiųsti galima iš Registrų centro svetainės.

        Svarbu: Failo formatas turi būti CSV su | (vertikalaus brūkšnio) skyrikliu.

⚙️ Diegimas ir Kompiliavimas
1 būdas: Naudojant Python (išeities kodas)
Bash

git clone https://github.com/your-username/rc-patcher.git
cd rc-patcher
python rc_patcher.py

2 būdas: EXE failo kūrimas (serveriams be Python)

Norint naudoti kliento kompiuteriuose arba 1C serveriuose, rekomenduojama sukompiliuoti skriptą į vieną vykdomąjį failą:
Bash

pip install pyinstaller
pyinstaller --onefile rc_patcher.py

Failas rc_patcher.exe atsiras aplanke dist.
💻 Naudojimas

Įrankis paleidžiamas per komandinę eilutę (Command Line).
Sintaksė
Bash

rc_patcher.exe <APLANKO_KELIAS> <XML_FAILO_VARDAS> [PERRAŠYMO_REŽIMAS]

Parametrai

    APLANKO_KELIAS: Pilnas kelias iki katalogo, kuriame yra mokėjimo XML failas ir JAR_IREGISTRUOTI.csv.

    XML_FAILO_VARDAS: Mokėjimo failo pavadinimas (pvz., export.xml).

    PERRAŠYMO_REŽIMAS (Neprivalomas):

        1 (arba true, overwrite) – Skriptas perrašo originalų failą.

        0 (numatytasis) – Skriptas sukuria naują failą su galūne _UPDATED.xml.

Pavyzdžiai
Bash

# Sukurti naują failą plat_UPDATED.xml (Saugus režimas)
rc_patcher.exe "C:\BankExport" "plat.xml" 0

# Perrašyti originalų failą plat.xml (Integracijos režimas)
rc_patcher.exe "C:\BankExport" "plat.xml" 1

🔌 Integracija su „1C:Primonė“

Norėdami automatiškai pakeisti pavadinimus eksportuojant mokėjimus iš 1C, pridėkite skripto iškvietimą eksporto procedūros pabaigoje (po WriteXML.Close() arba ЗаписьXML.Закрыть()).

Pavyzdinis kodas (1C / BSL):

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

🔍 Veikimo principas (Logika)

    Skriptas įkelia JAR_IREGISTRUOTI.csv į operatyviąją atmintį (Hash Map).

    Analizuoja XML failą ir randa visas operacijas (CdtTrfTxInf).

    Ištraukia gavėjo kodą iš žymos <Id><OrgId><Othr><Id>.

    Ieško šio kodo įkeltoje duomenų bazėje.

        Jei randa: Lygina pavadinimą XML faile su pavadinimu bazėje. Jei jie skiriasi, pakeičia <Nm> žymos turinį į oficialų pavadinimą.

        Jei neranda: (pvz., užsienio įmonė ar fizinis asmuo) – palieka įrašą nepakeistą.

    Išsaugo rezultatą.

⚠️ Svarbios pastabos

    Koduotė: Skriptas tikisi failų UTF-8 koduote.

    Užsienio įmonės: Jei gavėjo kodas nerandamas Lietuvos bazėje (pvz., Bulgarijos įmonės kodas), skriptas konsolėje išves pranešimą NOT FOUND ir praleis tą operaciją. Tai yra normalus veikimas.

    CSV Formatas: Įsitikinkite, kad Registrų centro failas naudoja | (vertikalų brūkšnį) kaip skyriklį.

📄 Licencija

MIT Licencija. Galima laisvai naudoti ir modifikuoti.