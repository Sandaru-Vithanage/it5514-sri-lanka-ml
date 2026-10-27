# IT5514 Applied Machine Learning: Sri Lankan dispatch forecasting

D.V.S Sandaru Rashmika — 269182L  
MSc in Artificial Intelligence, University of Moratuwa, Sri Lanka  
Prepared 28 October 2026. Student-supplied deadline: 1 November 2026; verify the exact Moodle cutoff.

## Start here

Read `07_report/269182L_IT5514_Report.pdf`, `00_requirements/Requirements_and_Execution_Plan.md`, and `00_requirements/Final_Verification_and_Submission_Checklist.md`. This is an AI-assisted research package for student review and defence. The assistance disclosure is part of the report and must not be replaced by a false unaided-authorship declaration.

The task forecasts next-local-day **recorded dispatch energy**, using Gaussian Process Regression (GPR). No GPR coverage was found in the supplied lecture corpus; final eligibility against unsupplied teaching is a student/lecturer check. This is a non-deep-learning tabular/time-series study. The requested bonus review version is hosted on Azure App Service Linux Free F1, with a private GitHub repository. No paid tier, Azure ML endpoint or live grid feed is used. See `10_deployment/README.md` for deployment, cost boundaries and cleanup.

## Main findings

- The released daily CSV is inconsistent with raw MW integration. The study deduplicates plant/timestamp records and integrates each 15-minute interval with a 0.25-hour multiplier; the original files are preserved.
- GPR test MAE: 1.599 GWh; RMSE: 2.492 GWh; R²: 0.544. MAE improvement against weekly seasonal naïve: 29.7%.
- SVR has the lowest test MAE; RF has the lowest test RMSE. GPR's MAE difference from RF is inconclusive in a paired block bootstrap.
- Nominal 95% observation intervals cover 90/97 outcomes (92.8%). Demand history and weekly calendar have the greatest grouped feature reliance.
- Several large errors coincide with public holidays. No test-driven feature redesign is hidden in the results.

## Extended evidence and review deployment

Seven learned algorithms are compared: linear regression, random forest, SVR, GPR, NGBoost, KNN and conventional gradient boosting. GPR remains the main new algorithm; NGBoost adds a second unfamiliar probabilistic method. Taught models provide comparators rather than being misrepresented as new.

The original electricity experiment is frozen. Added electricity comparisons are explicitly supplementary and post-hoc because that holdout was already examined. A separate Colombo CHIRPS-v2 rainfall task uses delayed rainfall features and a training-target embargo before each January evaluation origin. An invalid preliminary rainfall run was preserved after review caught a final-publication timing issue; corrected results are transparently retrospective reanalysis, not newly untouched validation. This correction follows source-availability evidence, not score optimization. No post-test hyperparameter chasing is performed. Full results include failures and seasonal baselines.

- Live historical research demo: https://lanka-dispatch-it5514-sv.azurewebsites.net
- Private review repository: https://github.com/Sandaru-Vithanage/it5514-sri-lanka-ml
- Deployment source commit and actual model hash: `10_deployment/deployment_record.json` and `/api/health`.
- The repository requires reviewer permission. The standalone source ZIP avoids access dependence; it also includes the 94 MB raw energy CSV, which Git acquires from the immutable Zenodo release instead.

## Project layout

| Folder | Contents |
|---|---|
| `00_requirements/` | Rubric matrix, source manifest, lecture audit, frozen protocol, source register and final checks |
| `01_source_materials/` | Preserved originals, local project only; not redistributed in the source ZIP |
| `02_data/raw/` | Pinned Sri Lankan data, original metadata and provenance |
| `02_data/processed/` | Audited daily targets, feature eligibility and modelling table |
| `03_code/` | Canonical acquisition, training, XAI, verification, report and interface source |
| `04_notebooks/` | Executed notebook calling the canonical code |
| `05_experiments/` | Full CV scores, splits, selected settings, metrics, predictions, models and logs |
| `06_figures/` | Figures generated from recorded experiment outputs |
| `07_report/` | PDF, editable content JSON, Markdown reading copy and build details |
| `08_demo/` | Actual interface captures, video, transcript and captions |
| `09_submission/` | Report, source ZIP, demo and upload checklist |
| `10_deployment/` | Minimal inference wrapper, bundle hashes, Azure evidence and deployment/cleanup instructions |
| `work/`, `.venv/` | Local intermediates and environment, excluded from submission |

## Environment

Python 3.13.1 was used on macOS ARM. The canonical runtime dependencies are pinned in `requirements.txt`; notebook, PDF and video utilities are in `requirements-authoring.txt`. Machine-level package versions are recorded separately. A cross-platform environment can be created with Python 3.13:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Install `requirements-extension.txt` for NGBoost and the independent rainfall task. The full recorded environment is `05_experiments/environment_extension_freeze.txt`; inference-only pins are `10_deployment/requirements.txt`. Install `requirements-authoring.txt` as well to execute the notebook or rebuild report/video assets. The source package includes the trained model for convenience. Python joblib/pickle artefacts are only for this trusted project: rebuild from source if provenance is uncertain, and use the pinned scikit-learn version.

## Reproduce the numerical study

Run from the extracted project root:

```bash
python 03_code/prepare_data.py
python 03_code/train_evaluate.py
python 03_code/explain_and_plot.py
python 03_code/validate_project.py
```

The code detects the project location from its own file path. When the pinned raw subset is present and its SHA-256 matches, preparation works offline. If files are missing, it downloads the original 15.2 MB source archive from Zenodo, verifies the archive checksum and extracts only the required Sri Lankan files. The raw Sri Lankan CSV is approximately 94 MB uncompressed; this is intentional evidence needed to independently reconstruct targets. It compresses well in the source ZIP. No Kaggle account, Azure subscription or API key is required.

Rerunning overwrites derived results in that extracted project. To preserve the original evidence, reproduce in a separate extracted copy. Small numerical differences may occur across numerical libraries or hardware; the saved metrics and reference predictions are the recorded run, while an isolated reproduction comparison is also provided. Original model selection is preserved. Added electricity comparisons and the corrected rainfall audit are labelled retrospective; no model or feature is reselected based on test scores. Data preparation takes additional time beyond the approximately 10-second recorded fitting/evaluation stage.

The notebook `04_notebooks/269182L_IT5514_Study.ipynb` runs these same scripts. Launch Jupyter using the project environment or select its Python kernel. The supplied executed copy is output from an isolated project reproduction, not fabricated notebook cells.

## Reproduce the supplementary experiments

Use a separate extracted copy to preserve recorded evidence:

```bash
python -m pip install -r requirements-extension.txt
python 03_code/acquire_rainfall.py
python 03_code/extension_experiments.py
python 03_code/summarize_extension.py
python 03_code/verify_extension.py
```

The rainfall snapshot is pinned in the repository/source ZIP; its rolling HDX URL may change, and acquisition refuses an unexpected hash. A minimum six-dekad feature delay handles publication latency, while the final model trains through October 2023 and excludes November–December before January 2024. Each CV fit uses the same two-month embargo. The model stays frozen through each annual validation period and the two-year test; lagged inputs update only when available under the stated delay. Archived original vintages are unavailable, so revisions remain a limitation. See the dataset card, protocol v1.1 and preserved availability-review archive.

`04_notebooks/269182L_IT5514_Extended_Evidence.ipynb` is an executed evidence-inspection notebook with independent checks and regeneration commands. It does not pretend its display cells retrain the study. Extension model pickles are included in the source ZIP; the repository provides reproducible training source. Both tasks have seven learned models and two baselines, in different target units. Do not average their raw MAEs.

## Run the front end

```bash
python 03_code/app.py --port 8765
```

Open http://127.0.0.1:8765 in a browser. Load a historical date, edit the six energy inputs if desired and generate a forecast. Inputs/outputs are shown in GWh; backend values are MWh. For example, 15 January 2025 with recorded inputs produces approximately 42.33 GWh. Changing only previous-day energy to 42 GWh produces approximately 44.22 GWh. The historical observed outcome remains 42.07 GWh. Negative energy inputs are rejected and the existing output is explicitly labelled the last valid estimate.

The model is trained through 31 December 2024; evaluation ends 7 April 2025. This interface is a retrospective educational prototype with a publication-latency assumption. It is not a current electricity-demand service. Stop the local server with Ctrl+C.

## Report and video sources

`07_report/report_content.json` is the editable source used by the renderer; `07_report/269182L_IT5514_Report.md` is an editable reading copy generated from it. Edit the JSON blocks to rebuild the PDF with:

```bash
python 03_code/build_report.py
```

The demo is a narrated sequence of genuine captures of the functioning interface, with panning and explanatory captions. It is not presented as continuous live screen recording. It uses macOS's system voice and is disclosed accordingly. Its transcript is supplied so the student can understand the walkthrough or rerecord personal narration. The guide requires a 3–5 minute front-end video but does not require a presenter or a particular narration style. `03_code/build_demo_video.py` reproduces the edited video from existing captures and macOS `say`; direct recapture uses browser automation and is not needed to reproduce predictions.

## Data attribution

Original producer: Public Utilities Commission of Sri Lanka. Public compilation: O. G. Coombes, K. Hunt and H. Bloomfield, *SASEA Electricity Demand Data for 2013-2025*, Zenodo v1, 22 September 2025, DOI https://doi.org/10.5281/zenodo.17175212, CC BY 4.0. This project adapts the Sri Lankan raw subset through documented deduplication, local-date conversion, energy integration and feature construction. See `02_data/DATASET_CARD.md` and raw provenance. Do not remove the attribution or claim original measurement collection.

## Submission boundary

The private GitHub repository is supplied in addition to the complete code ZIP, and the video covers the hosted interface and repository provenance. Use the three required submission files in `09_submission/`: report PDF, source ZIP and 3–5 minute MP4. The written brief explicitly permits a source ZIP or GitHub link, so a source ZIP is prepared; no additional all-in-one submission ZIP is necessary. Dataset and instructions are inside the source package. Confirm Moodle size limits, exact cutoff, method eligibility and academic-integrity declarations before upload. The package has not been uploaded to Moodle.
