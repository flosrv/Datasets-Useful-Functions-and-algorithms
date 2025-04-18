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

