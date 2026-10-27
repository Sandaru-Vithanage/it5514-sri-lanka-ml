# Azure review deployment

The user approved a private GitHub repository and a maximum US$10 of Azure for Students credit on 28 October 2026. The service uses **Azure App Service Linux Free F1**, one Python 3.13 application, one Gunicorn worker/two threads, default HTTPS hostname. No paid Azure ML endpoint, VM, database, registry, custom domain or paid monitoring was created. Free shared compute has quotas and cold starts; availability is not guaranteed. This is an academic historical demonstration, not a production grid service.

- Review app: https://lanka-dispatch-it5514-sv.azurewebsites.net
- Private source: https://github.com/Sandaru-Vithanage/it5514-sri-lanka-ml
- Region: East Asia. The subscription policy rejected Southeast Asia; the allowed-region policy was read before selecting East Asia.
- Resource group: `rg-it5514-lanka-review`
- Plan: `plan-it5514-free`, SKU F1 / Free (verified with plan-show).
- App: `lanka-dispatch-it5514-sv`

## Build and deploy

Install Azure CLI from Microsoft's official instructions and authenticate interactively (`az login`). Keep all tokens and account state outside the repository. The current local session uses a task-local credential directory in the excluded `work/azure_state`; it is not distributed. These commands assume your own selected subscription and reuse the named resources.

```bash
python 03_code/build_deployment.py
az appservice plan show -g rg-it5514-lanka-review -n plan-it5514-free --query sku
# Verify F1 / Free before continuing. Do not silently upgrade to a paid tier.
az webapp config appsettings set -g rg-it5514-lanka-review -n lanka-dispatch-it5514-sv --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true STUDY_COMMIT=YOUR_VERIFIED_SOURCE_COMMIT
az webapp config set -g rg-it5514-lanka-review -n lanka-dispatch-it5514-sv --startup-file 'sh startup.sh' --min-tls-version 1.2 --ftps-state Disabled
az webapp deploy -g rg-it5514-lanka-review -n lanka-dispatch-it5514-sv --src-path 10_deployment/deployment.zip --type zip
python 03_code/verify_production.py https://lanka-dispatch-it5514-sv.azurewebsites.net
```

`build_deployment.py` writes a 14-file inference bundle from an explicit allowlist; it records hashes in `bundle_manifest.json`. It includes the original GPR pipeline, feature table needed for historical replay/reference ranges, explanations and recorded scores. It excludes raw datasets, lecture files, other model pickles, notebooks and credentials. The Flask/Gunicorn runtime pins only inference dependencies. The health endpoint exposes a non-secret model fingerprint and source commit to connect the deployed application with its provenance. Root HTML omits the student's full name/index; the private academic report retains them.

See `remote_verification.json` and `deployment_record.json` for actual completed verification. Creation is not considered successful inference until those checks pass. The report and video refer to that evidence.

## Review access, cost and cleanup

The repository is private by instruction. A marker needs collaborator access or the standalone source ZIP. No invitations or public-visibility change have been performed. The source ZIP includes both pinned datasets; Git excludes the 94 MB energy CSV and provides the immutable Zenodo acquisition method instead.

The selected F1 plan is the free tier, rather than a spend target of US$10. A paid-resource budget is not a hard Azure spending stop. Do not add a paid service or change SKU without reviewing the resulting cost. Cost reporting can lag: configured free resources are evidence of configuration, not a fabricated invoice total. No future monitoring job is implied.

After assessment, remove the dedicated resource group in the Azure portal, or consciously run `az group delete --name rg-it5514-lanka-review` after checking that it contains only this assignment's resources. Deletion is not run by this package. Stopping an application is not a universal way to remove charges if someone later changes to a paid plan. Keep the source ZIP and demo as durable assessment evidence even if cloud availability ends.
