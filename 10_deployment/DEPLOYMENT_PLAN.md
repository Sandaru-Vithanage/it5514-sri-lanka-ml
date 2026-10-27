# Bonus deployment plan

User authorization on 28 October 2026: create a private GitHub repository under Sandaru-Vithanage; consume at most US$10 of the Azure for Students credit for this assignment.

First-choice service: Azure App Service, Linux, Free F1 shared plan, one Python web application, supported Python 3.13 runtime if available, default azurewebsites.net HTTPS hostname. Use one Gunicorn worker and two threads. The original saved GPR model, scaler and verification results are reused; no unrecorded cloud retraining. A minimal deployment ZIP contains only inference code, required public/processed data, the model and result metadata.

No Azure ML managed endpoint, GPU, database, private container registry, custom domain, paid certificate or paid monitoring is required. No paid SKU is to be provisioned merely because the account has US$100 in credit. If F1 is unavailable, review a specific alternative and its retention/cleanup cost before provisioning. An account balance is not a spending target, and an Azure budget alert by itself is not a hard spending stop.

The hosted application contains only public aggregate energy data and historical research predictions. The public HTML omits the student's full name and index; these remain in the private academic repository and submitted report. Public app health returns a model fingerprint for deployment verification, never credentials or subscription/tenant IDs.

Required verification before saying the model is deployed:

1. Confirm the actual Azure plan SKU and state.
2. Fetch the HTTPS health endpoint and match its model SHA-256 to the tested local artefact.
3. Reproduce 15 January 2025 and compare the result with the saved prediction.
4. Change one input and confirm a changed inference response; reject invalid values.
5. Inspect the public interface in a browser.
6. Record the live URL, private repository URL and commit in a non-secret deployment record.
7. Update the report, README and 3-5 minute video to show the real deployed service and repository.

Private GitHub access requires reviewer permission. Do not make the repository public or add collaborators without the student's instruction. The submission ZIP remains an accessible code alternative if the marker has not been granted repository access.
