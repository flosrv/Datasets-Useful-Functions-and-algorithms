import json

leviaa_creds_path = r"c:\Credentials\leviaa_api_creds.json"
with open(leviaa_creds_path, 'r') as f:
    content = json.load(f)
    user = content['user']
    password = content['password']

domain = "cloud.leviia.com"
auth=(user,password)
url = "https://"+domain+"/remote.php/dav/files/"+auth[0]