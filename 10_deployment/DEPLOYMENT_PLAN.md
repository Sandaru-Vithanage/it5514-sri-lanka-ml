# Bonus deployment scope and authorization

Initial authorization, 28 October 2026: private GitHub review and Azure hosting within US$10 of Azure for Students credit. Amendment, 29 October 2026: the student explicitly requested public GitHub source and automated deployment. This supersedes the initial private-only preference. Historical manual deployment records remain archived separately.

The implemented service is Azure App Service Linux Free F1, East Asia, Python 3.13, one Gunicorn worker/two threads and the default HTTPS address. The same original saved GPR/scaler and recorded evidence are deployed. No unrecorded cloud retraining or model selection occurs.

The dedicated group contains the free plan, app and a free user-assigned managed identity for GitHub OIDC. Website Contributor is scoped only to the app, Reader only to the plan, and federated trust only to the exact main-branch identity. No paid ML endpoint, GPU, database, registry, domain or monitoring was created. The US$10 cap remains a maximum; free configuration is not a final billing total or hard spending enforcement.

Runtime/model pushes to main validate nine packaged runtime cases and all 97 saved predictions, build an explicit 15-file ZIP, deploy the same tested artifact and verify nine HTTPS checks. Pull requests validate without cloud access. Documentation-only changes do not redeploy; a deliberate main-branch workflow dispatch is also available. Credentials and source lecture materials are excluded from the public repository and deliverables.

Release acceptance requires successful Actions validation/deployment, an exact embedded source commit and model fingerprint, historical/edited prediction agreement, invalid-request rejection and browser inspection. Durable records, public URLs and cleanup instructions are in this directory. The report, source ZIP and 3–5 minute video describe the current setup. Free quotas and cold starts limit availability; no SLA or live grid feed is claimed.
