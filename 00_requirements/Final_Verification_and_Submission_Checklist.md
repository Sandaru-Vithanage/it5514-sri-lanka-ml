# Final verification and submission checklist

Prepared for D.V.S Sandaru Rashmika, 269182L, IT5514 Applied Machine Learning. Review date: 29 October 2026. Deadline supplied by student: 1 November 2026; exact Moodle time remains to be checked.

## Requirement coverage

| ID | Requirement | Technical status | Evidence |
|---|---|---|---|
| R1 | Local problem, collection, target/features, size, preprocessing and ethics | Complete | Report sections 1-2; dataset card; raw release and audit |
| R2 | New algorithm, no deep learning/image application, justification | Complete against supplied-material evidence | GPR methodology; 38-file lecture audit; no GPR occurrence in extracted/OCR corpus |
| R3 | Train/validation/test, hyperparameters, metrics, graphs and interpretation | Complete | Frozen protocol; full three-fold CV record; original six-method comparison plus three added models and separate rainfall benchmark; test predictions |
| R4 | Explainability and domain interpretation | Complete | Grouped block permutation, PDP, non-additive local sensitivity and retrained ablations |
| R5 | Critical limitations, quality, bias, ethics and impact | Complete | Error and interval analysis; report section 11; explicit dispatch-proxy limits |
| R6 | Report quality and technical clarity | Complete technical review | 22-page A4 PDF; verified references; editable sources; rendered-page review |
| R7 | Bonus front end with inputs, predictions and explanations | Implemented and checked | Python inference API, HTML UI, actual model artefact, CUA checks and API verification |
| S1 | Report PDF | Prepared | `269182L_IT5514_Report.pdf` |
| S2 | Source ZIP or GitHub link | ZIP and public repository prepared | `269182L_IT5514_Source_Code.zip` |
| S3 | Dataset or acquisition instructions | Included in source | CC-BY-4.0 Sri Lankan subset, provenance, hashes and acquisition script |
| S4 | Front-end video, 3-5 minutes | Prepared and decoded | `269182L_IT5514_Demo.mp4`; 273.5 seconds (approximately 4 min 34 sec) |
| S5 | Moodle upload | Student action, not performed | Confirm exact cutoff and upload limits |

The official marking items total 90 core marks plus 10 bonus. No mark, grade guarantee, lecturer approval or platform acceptance is asserted.

## Executed verification

- Ten independent numerical/leakage checks passed. They verify chronological unique rows, every lag/rolling value against earlier calendar dates, target quality, development-only transforms/training, saved-model prediction reproduction, every main metric, and validation-only selection.
- The notebook executed all eight code cells with zero error outputs in an isolated project reproduction. Every numeric heldout prediction matches the recorded run exactly (maximum absolute difference 0 MWh on this machine).
- API checks passed for model health, historical prediction equality, changed-input inference, preserved historical actuals, invalid values, and future-period warnings.
- Browser checks verified historical replay, an edited input, invalid-input rejection and the last-valid-estimate label, evaluation evidence and the data/method tab.
- The latest PDF was rendered and all 22 pages visually inspected. No clipped text, orphan overflow pages or overlapping figures/tables were found. A character-bound check found zero characters outside the safe page bounds.
- All main score tables were independently recalculated from saved prediction rows. All main numerical report claims were checked against JSON/CSV evidence. Figures come from the same saved outputs.
- Online references were checked at their primary sources; the source register records HTTP verification. Dataset v1 and the original raw CSV are pinned by checksum. The source paper is labelled a preprint.
- The H.264/AAC video decodes fully without ffmpeg errors and meets the 3-5 minute limit. Representative frames were visually inspected. Its synthetic voice and captured-state editing are disclosed; it is not presented as continuous live recording.
- Package checks exclude virtual environments, credentials, copied teaching materials, unrelated source-country data, scratch files and temporary audio. The raw Sri Lankan CSV is intentionally retained so the central target reconstruction can be independently reproduced.

## Limitations that remain visible

1. GPR eligibility is established against supplied files, not unsupplied classroom material. Confirm if the lecturer discussed it elsewhere.
2. The data are a historical dispatch proxy with changing plant coverage and an unverified publication-latency assumption. No live-grid, current-demand or household-fairness claim is made.
3. The test is short, and nominal interval coverage falls short empirically. GPR does not dominate taught comparators. Missing holiday indicators are discussed; no post-test redesign is hidden.
4. University/module-wide permission for this level of AI assistance has not been confirmed by an explicit policy document. The student reports no additional rules. The report discloses assistance and requires human review rather than claiming unaided authorship.
5. No institutional Turnitin/similarity report, AI-use approval, lecturer sign-off or Moodle upload has been obtained. Source verification is not a substitute for those processes.
6. The video is a narrated capture-based walkthrough with synthesized voice. The guide does not specify personal narration, but the student should check any later instruction and rerecord if required.

## Student actions before upload

- Read and revise the report based on your own understanding; rehearse using the defence guide. Inspect code and reproduce an example.
- Confirm acceptance of the algorithm and comply with applicable AI/academic-integrity declarations. Keep the assistance disclosure accurate. Do not sign a statement of unaided authorship if it would be false.
- Check the precise 1 November cutoff, Moodle accepted formats and file-size limits. No such limits appear in the supplied PDF.
- Review the PDF, play the whole video and open the source ZIP. If a presenter or personal narration is required, rerecord using the transcript and working interface.
- Upload the PDF, source ZIP and MP4 from `09_submission/`; verify Moodle acknowledges successful submission. The dataset and instructions are included within the source ZIP.

The report uses an index-prefixed naming convention and numbered IEEE-style references because the supplied brief specifies no names or style. The report is approximately 6,972 words including tables, references and captions; there is no supplied word limit.


## Verified extension and deployment

- Two Sri Lankan tasks now compare seven learned algorithms each (linear regression, RF, SVR, GPR, NGBoost, KNN, gradient boosting) and two transparent baselines. GPR remains the primary unfamiliar algorithm; NGBoost is an additional method absent from supplied notes.
- Added electricity results are post-hoc supplementary benchmarking. The original six-method study, model and explanation results are unchanged.
- Rainfall availability review caught unavailable late-year fitting labels. Protocol v1.1 adds a two-month training embargo before each January validation/test origin. The invalid preliminary run is archived and excluded from final conclusions. Corrected rainfall scores are retrospectively reanalysed on an already inspected period; no fresh-test claim or score-driven retuning is made.
- The corrected seasonal median rainfall MAE is 41.39 mm, ahead of SVR 48.17 and GPR 51.86. Negative findings and distribution-support/coverage limits remain explicit.
- Two executed extension runs reproduce all predictions within 10^-8 in native units. All 78 arithmetic, ordering, selection, availability, model-persistence and repeatability checks pass. Nine additional checks independently recompute interval coverage, width, Normal NLPD and support violations.
- The extension evidence notebook executed three code cells with zero errors. It inspects saved evidence and performs verification; it does not falsely claim that display cells retrain models.
- Public repository: https://github.com/Sandaru-Vithanage/it5514-sri-lanka-ml . The student explicitly requested public release and automation on 29 October, superseding private review. Anonymous browser access was verified; original teaching files and credentials are excluded.
- Live app: https://lanka-dispatch-it5514-sv.azurewebsites.net . Azure App Service Linux, East Asia, Python 3.13, Free F1. The dedicated group contains one free plan, one app and a user-assigned managed identity for OIDC (no extra identity charge). No paid resources were created; the US$10 authorized cap is not treated as a spending target or a final invoice claim.
- The main-push Actions run passed validation and deployment. Nine packaged runtime cases check all 97 saved means/standard deviations, the 15-file ZIP and invalid inputs. Nine HTTPS checks verify the actual release commit, model hash, historical/edited forecasts, fixed actual, extension tables and request rejection within 10^-6 MWh tolerance. Browser captures show public source, release provenance and both successful jobs. Historical manual checks are archived separately.
- Report Sections 13–17 and the approximately 4 min 34 sec video cover the extension and deployed repository-backed prototype. All 22 final PDF pages were rendered and visually checked; character bounds show zero out-of-margin characters. Source/test/video checks do not imply lecturer approval or Moodle upload.

Cloud limitations: free shared-compute quotas and cold starts may interrupt access. The source ZIP and captured demo provide durable evidence. `10_deployment/README.md` records reproduction, access, budget boundaries and cleanup. The repository is publicly reviewable; the submitted source ZIP pins a complete assessment snapshot.

Fresh extraction verification also passed: all payload hashes and ZIP CRC, the main/extension/probabilistic checks, rebuilding the 15-file deployment bundle, importing the packaged WSGI app and model inference, and both notebooks’ executed-cell/error status. Evidence: `05_experiments/final_package_verification.json`.


## Automated release evidence

- Successful push run: https://github.com/Sandaru-Vithanage/it5514-sri-lanka-ml/actions/runs/40758348528 . Commit `fb13708f15b44e5e51eb5e2d8a263607aa49e402`; first attempt succeeded.
- App/model pushes to main validate, deploy the same artifact, and verify HTTPS inference. Pull requests validate without Azure permissions. Documentation-only changes do not deploy. Training and model selection remain separate from deployment.
- OIDC trust matches the exact main-branch claim including immutable owner/repository IDs. Website Contributor is app-scoped; Reader is plan-scoped. No long-lived client secret or publish-profile password was created.
- Current durable records: `10_deployment/github_actions_run.json`, `remote_verification.json`, `bundle_manifest.json`, `oidc_configuration.json`. Source ZIP includes `.github/workflows/azure-deploy.yml`. Original private/manual records remain historical, clearly dated.
