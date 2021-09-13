import json
import base64
import google.auth
import google.auth.transport.requests
from google.cloud import compute_v1

def ssh_remedy(event, context):
    content = base64.b64decode(event['data']).decode('utf-8')
    content_json = json.loads(content)
    creds, project = google.auth.default()
    fw_client = compute_v1.FirewallsClient()
    rule_long = content_json['resource']['name']
    rule = rule_long.split('/')[-1]
    project = content_json['resource']['projectDisplayName']
    delete = fw_client.delete(project = project, firewall = rule)



"""
Copy and paste these modules for the requirements.txt

google-auth
google-cloud-compute

"""