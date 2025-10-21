from auth import *
from imports import *

def get_files_from_leviaa_cloud_path(path, extension = ".pdf"):
    domain = "cloud.leviia.com"
    auth=(user,password)
    url = "https://"+domain+"/remote.php/dav/files/"+auth[0]
    r = requests.request('PROPFIND', url+path, data=None, auth=auth)
    data = ET.fromstring(r.text)
    files = [urllib.parse.unquote(os.path.basename(el[0].text)) for el in data]
    files = [file for file in files if file.endswith(extension)]
    if files:
        file_dict = []
        for file in files:
            file_dict.append({
                "path": path,
                "file": file
            })

    return file_dict
      

    print("No Files")

def write_file_from_leviaa_to_local(path, file, output_path):
        try:
            path_to_file = path + "/" + file
            r = requests.request('GET', url + path_to_file, auth=auth)

            file_name = os.path.basename(file)
            output_file_path = os.path.join(output_path, file_name)

            with open(output_file_path, 'wb') as f:
                f.write(r.content)

            print(f"✅ Fichier téléchargé : {file_name}")
        except Exception as e:
             print(str(e))

def upload_video_if_not_exists(local_file_path, remote_folder):
    """
    Upload une vidéo sur Leviaa uniquement si elle n'existe pas déjà dans le dossier distant.
    Peut être utilisée seule ou dans une boucle sur plusieurs vidéos.
    """

    file_name = os.path.basename(local_file_path)
    remote_path = f"{remote_folder}/{file_name}"

    # Vérifier si le fichier existe déjà
    r = requests.request('PROPFIND', url + remote_folder, data=None, auth=auth)
    if r.status_code != 207:
        print(f"❌ Impossible de lister le dossier distant {remote_folder}")
        return

    data = ET.fromstring(r.text)
    existing_files = [urllib.parse.unquote(os.path.basename(el[0].text)) for el in data]
    if file_name in existing_files:
        print(f"⚠️ La vidéo existe déjà : {file_name}")
        return

    # Upload
    with open(local_file_path, 'rb') as f:
        r_upload = requests.put(url + remote_path, data=f, auth=auth)

    if r_upload.status_code in [200, 201, 204]:
        print(f"✅ Vidéo uploadée : {file_name}")
    else:
        print(f"❌ Erreur {r_upload.status_code} lors de l'upload de {file_name}")
