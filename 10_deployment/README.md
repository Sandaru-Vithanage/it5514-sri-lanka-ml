# Public source and automated Azure deployment

Current setup, 29 October 2026: the student explicitly requested a public repository and automatic deployment. The original 28 October private/manual deployment is preserved as historical evidence. The existing Azure for Students spending cap remains US$10; hosting stays on **Azure App Service Linux Free F1**, East Asia, Python 3.13, one Gunicorn worker/two threads.

- Public source: https://github.com/Sandaru-Vithanage/it5514-sri-lanka-ml
- Workflow and runs: https://github.com/Sandaru-Vithanage/it5514-sri-lanka-ml/actions/workflows/azure-deploy.yml
- Live model: https://lanka-dispatch-it5514-sv.azurewebsites.net
- Live release identity: https://lanka-dispatch-it5514-sv.azurewebsites.net/api/health
- Resource group: `rg-it5514-lanka-review`; app: `lanka-dispatch-it5514-sv`; plan: `plan-it5514-free`.

## What triggers deployment

Push reviewed application, model or inference-evidence changes to `main`. The workflow first builds and tests, then uploads the validated ZIP and verifies the active HTTPS release. A pull request runs validation only. Documentation-only changes do not deploy. To redeploy deliberately, open Actions, select **Validate and deploy Azure model**, choose **Run workflow**, and select `main`.

This automates deployment of a saved model. It does not retrain models, choose new hyperparameters, add test-driven features or alter the frozen research protocol. A changed model must be accompanied by appropriate reviewed experimental evidence and compatible dependencies.

## Build, tests and provenance

`03_code/build_deployment.py` uses an explicit allowlist. The 15-file ZIP includes runtime source, pinned inference requirements, the GPR pipeline, historical feature/reference data, saved evidence and generated `release.json`. Raw data archives, lecture material, notebooks, other model pickles and all account state are excluded. ZIP entry timestamps are fixed so identical inputs and commit yield identical archives.

The build job installs `10_deployment/requirements.txt`, validates the packaged app, compares all 97 saved GPR predictions/std deviations, and checks nine runtime cases including changed inputs, preserved actuals, invalid/nonfinite/oversized requests, public source metadata and experiment tables. Only the validated artifact reaches deployment.

`release.json` embeds the actual GitHub source SHA and model SHA-256. The app reads it from the deployed package at startup. The smoke verifier waits for that exact SHA and model hash, then compares real HTTPS predictions/evidence with the offline tested bundle. It does not trust an environment variable changed before the new code is uploaded. A failed build or live verification fails the run; no automatic rollback is claimed. Revert the problematic main-branch commit and push to restore a reviewed earlier implementation.

The Actions run stores `validated-inference-release` and `azure-deployment-evidence` for seven days. The latter includes manifest and live verification JSON. Durable verification for the first successful automated rollout is recorded in this folder after the run completes.

## Scoped authentication

Authentication uses **GitHub OIDC** with the user-assigned managed identity `id-it5514-github`. GitHub includes immutable owner/repository IDs in the observed token. Its federated subject is exactly `repo:Sandaru-Vithanage@92751836/it5514-sri-lanka-ml@1436283939:ref:refs/heads/main`, issuer `https://token.actions.githubusercontent.com`, audience `api://AzureADTokenExchange`.

Azure roles are **Website Contributor at this app only** and **Reader at this F1 plan only**. The workflow verifies F1 before uploading; it cannot provision or scale the plan with those roles. Azure credentials are granted only to the deploy job, which is excluded from pull-request runs. The validation job has repository read permission. Checkout does not persist credentials. Public PRs use hosted runners, not the student's laptop.

GitHub Actions secrets hold the three identity identifiers `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`. They are identifiers used with federation, not password credentials. No client secret or publish-profile password was created. Local Azure CLI/MSAL state remains in excluded `work/azure_state` and is never uploaded. Actions are pinned to verified release SHAs; review newer patched release SHAs when maintaining the workflow.

For a fresh installation, create a user-assigned managed identity, add the exact federated subject above, grant the two scoped roles, and configure those three GitHub Actions secrets. The non-secret trust/role design is recorded in `oidc_configuration.json`. Do not grant subscription-wide Contributor to solve an app deployment error.

## Local reproduction and deliberate manual deployment

```bash
python -m pip install -r 10_deployment/requirements.txt
python 03_code/build_deployment.py --commit YOUR_FULL_40_CHARACTER_REVIEWED_GIT_SHA
python 03_code/ci_validate.py
```

Use the automatic workflow for the production app. A manual deployment remains possible for recovery after interactive `az login`, verification that `plan-it5514-free` is still F1, and review of the bundle:

```bash
az webapp deploy -g rg-it5514-lanka-review -n lanka-dispatch-it5514-sv --src-path 10_deployment/deployment.zip --type zip
python 03_code/ci_verify_deployment.py --expected 10_deployment/smoke_expected.json --output work/manual_release_verification.json
```

A public repository does not require a local model registry or Azure ML workspace. The fitted scaler and GPR object are inside `05_experiments/models/GPR.joblib`; Python loads that file with `joblib.load`. GitHub stores the source/model, and Actions builds/uploads a copy to Azure. The laptop can be offline during automated deployments.

## Cost, availability and cleanup

The plan remains F1 / Free. Managed identities have no extra charge; no paid plan, GPU, Azure ML endpoint, database, registry, custom domain or paid monitoring was created. Free shared compute has quotas and cold starts, so uptime is not guaranteed. The US$10 credit cap is a maximum, not a spending target or an enforceable Azure hard stop. Posted billing may lag; no invoice balance is invented.

After assessment, inspect and remove the dedicated resource group if no longer needed. This also removes its managed identity and federated credential; disable the workflow or remove its trust to stop future deployments. No deletion has been performed. Keep the source ZIP and demo as durable assessment evidence. Dataset licences and attribution remain applicable to public copies. The repository includes the student's assignment name/index and disclosed AI assistance; copied lecture files and account state are excluded.

Primary references: [Microsoft App Service GitHub deployment](https://learn.microsoft.com/en-us/azure/app-service/deploy-github-actions), [managed identity federation](https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation-create-trust-user-assigned-managed-identity), [managed identity cost](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview).

## Verified automatic release

[Successful Actions run](https://github.com/Sandaru-Vithanage/it5514-sri-lanka-ml/actions/runs/40758348528), commit `fb13708f15b44e5e51eb5e2d8a263607aa49e402`, attempt 1. Nine packaged runtime cases check all 97 saved predictions; nine HTTPS checks verify the actual release and model. Durable records: `github_actions_run.json`, `remote_verification.json` and `bundle_manifest.json`.
