# GCP Infrastructure Continuous Compliance Demo

## Set Up The Preventative Controls


#### [Checkmarx KICS](https://github.com/Checkmarx/kics) and the 1st Cloud Build



1. In the CloudShell or your local IDE, clone the demo code from [here](https://github.com/kenpkz/gcp-continuous-compliance-demo);
2. Create a Source Repository and push the downloaded code to your own Source Repository using [this guide](https://cloud.google.com/source-repositories/docs/pushing-code-from-a-repository#cloud-sdk);
3. Create two Cloud Storage buckets, one for the IaC scan results and one for the Terraform state;
4. Create a Pub/Sub topic for the 2nd Cloud Build trigger, success builds from the 1st Cloud Build will push a message to this topic, and messages in this topic will trigger the 2nd Cloud Build for Terraform apply;
5. Create the 1st Cloud Build trigger
    1. Use the “Push to a branch” as the triggering event, choose the Source Repository you configured in step #2 above
    2. Use the Inline for the Cloud Build instructions, copy YAML from the ```KICS buildspecs.yaml``` file in the ```gcp-continuous-compliance-demo/continuous-compliance-demo-cloudbuild``` folder
    3. Paste the YAML the Inline Editor and make following changes
        a. On line 14, change the bucket name from “kics-results” to the one you created in step #3 
        b. On line 55, change the Pub/Sub topic from “KICS-pipeline” to the topic you created in step #4)

#### Terraform and the 2nd Cloud Build

1. In the cloned repository, in the ```/continuous-compliance-demo-cloudbuild```, modify the ```main.tf``` file, change the Terraform backend from ```your-bucket``` to the Terraform backend bucket you created in step #3 above

2. Set up the 2nd Cloud Build using the Pub/Sub as the trigger, pick the Pub/Sub topic that you created in step #4 above, use the same Source Repository and the same branch as the 1st Cloud Build (You can inspect the &lt;cloudbuild.yaml> file in the same folder for the build instructions)

#### IAM Permissions for both Cloud Build



1. For the sake of simplicity (challenge for you - set the IAM permissions on the least privilege principle), give the Cloud Build Service Account following roles
    a. [Cloud Build Service Account](https://cloud.google.com/build/docs/cloud-build-service-account) - this will allow your Cloud Build to upload the scan report, publish the Pub/Sub message etc.
    b. Compute Admin - this role will allow your Cloud Build to create firewalls, VPCs etc. for the sample Terraform code


#### Test the Preventative Controls

1. Go to the working folder ```cd gcp-continuous-compliance-demo```
2. Use your choice of code/text editor to make changes to the ```bad-fw.tf``` file in the ```continuous-compliance-demo-cloudbuild``` folder  ```vi ./continuous-compliance-demo-cloudbuild/bad-fw.tf```, you can make a change on line 3 the description field

3. Push the changes to the Source Repository to trigger the 1st Cloud Build ```git add . && git commit -m "demo" && git push```
4. Inspect the Cloud Build history, you should see the build is failed, scroll up to see the scan results console output showing the SSH port was the reason why it was failed

5. Use your choice of code/text editor to update the ```bad-fw.tf``` file in the ```continuous-compliance-demo-cloudbuild``` folder, you can change the firewall port from 22 to 443 on line 31
6. Push the changes again ```git add . && git commit -m "demo" && git push```
7. Inspect the Cloud Build, VPC and Firewall rules, you will see both the builds are successful, VPC and firewall rules are created

## Set Up The Detective & Responsive Controls


#### SCC to Slack channel 

1. Ensure your SCC is up and running, API enabled etc. for the working project;
2. Create a Pub/Sub topic and corresponding Subscription for the Slack notification (default settings will do)
3. In CloudShell, run the following command, replace the &lt;>s with your Pub/Sub topic created in #1 above and the Organisation ID (you can find it running - gcloud organizations list). You can only set up SCC notification via SDK/API not console for now.

```
gcloud scc notifications update scc-open-ssh-slack --pubsub-topic &lt;your-pub-sub-topic> --organization &lt;your org id> --filter "category=\"OPEN_SSH_PORT\" AND state=\"ACTIVE\""
```

4. In Slack, click the “+” next to the Apps, select Browse App Directory;

5. In the popped up browser window, click the “Build” on the top right, select “Create an app” and choose “From scratch”

6. Under OAuth & Permissions -> Scopes -> Bot Token Scopes, create ```chat:write``` and ```chat:write.public``` scopes 

7. Scroll up and “Install App To The Workspace”, copy the Bot User OAuth Access Token

8. Modify the scc-slack.py file under the continuous-compliance-demo-scc folder, paste the Bot User OAuth Access Token on line 5, and change the Slack channel name on line 14 to your own channel name

9. Create a Cloud Function with Pub/Sub as the trigger, using the Pub/Sub you’ve created in step #2, choose Python 3.8, paste the ```scc-slack.py``` in the console and the modules in the ```requirement.txt```

!!! Note
    Make sure the Entry Point is the same as your Python function name. In my example, it is ```send_slack_chat_notification```


10. IAM - the default App Engine default service account service account has sufficient permissions for this Cloud Function


#### SCC Auto-remediation

1. Create another Pub/Sub topic and corresponding Subscription for the auto-remediation (default settings will do)
2. In CloudShell, run the following command, replace the the Pub/Sub topic with your Pub/Sub topic created in #1 above and the Organisation ID (you can find it running - gcloud organizations list). 

```gcloud scc notifications update scc-open-ssh-auto-remedy --pubsub-topic your-pub-sub-topic --organization your org id --filter "category=\"OPEN_SSH_PORT\" AND state=\"ACTIVE\"" ```



3. Create another Cloud Function with Pub/Sub you created in step #2 as the trigger, paste the code in continuous-compliance-demo-scc/cloudfunction_remedy.py to the inline code editor, paste the modules in the requirements.txt

!!! Note
    Make sure the Entry Point has the same name as your Python function



4. In addition to the App Engine default service account permissions, you will need to add the Compute Security Admin managed role (again, in Prod or customer engagements, you will want to follow the least privilege principle)


#### Test Detective And Responsive Controls

1. Create a firewall rule with ```0.0.0.0/0``` as the source and TCP port 22 as the destination port;
2. Monitor SCC notifications and you should see ```OPEN_SSH_PORT``` finding, your Slack channel should also have the message posted by the bot, and the bad firewall rule may have already been deleted by your Cloud Function (in my tests, usually within 5 seconds)