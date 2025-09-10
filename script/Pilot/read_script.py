import os
import subprocess
import re

def estrai_prefisso_numerico(nome_file):
    match = re.match(r"(\d+)", nome_file)
    return int(match.group(1)) if match else float('inf')

def esegui_curl_dai_file(cartella):   
    file_nomi = os.listdir(cartella)
    file_nomi = [f for f in file_nomi if re.match(r"\d+", f)]
    file_nomi.sort(key=estrai_prefisso_numerico)

    for nome_file in file_nomi:
        percorso_file = os.path.join(cartella, nome_file)
        print(f"\n📂 File processing: {nome_file}")

        with open(percorso_file, 'r') as f:
            contenuto = f.read()

        # Rimuovi continuazioni di linea ( \ )
        comando = contenuto.replace('\\\n', ' ').strip()

        if comando.startswith("curl"):
            print(f"➡️  I execute curl command from the: {nome_file}")
            try:
                result = subprocess.run(comando, shell=True, check=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                print(f"✅ STDOUT:\n{result.stdout}")
                if result.stderr:
                    print(f"⚠️ STDERR:\n{result.stderr}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error executing {nome_file}")
                print(f"➡️ Exit code: {e.returncode}")
                print(f"➡️ STDOUT:\n{e.stdout}")
                print(f"➡️ STDERR:\n{e.stderr}")
        else:
            print(f"⚠️  No curl command found in {nome_file}")

# 📁 Cartelle da elaborare
cartelle = [
    "./100 - CB - Create Entity",
    "./200 - IOT - Create Service Group",
    "./300 - IOT - Create Provisioned Device"
]

for cartella in cartelle:
    if os.path.isdir(cartella):
        print(f"\n🔄 Start processing for: {cartella}")
        esegui_curl_dai_file(cartella)
    else:
        print(f"⚠️  Folder not found: {cartella}")
