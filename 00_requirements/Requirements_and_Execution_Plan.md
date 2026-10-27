# IT5514 assignment review and execution plan

Student: D.V.S Sandaru Rashmika | Index: 269182L  
MSc in Artificial Intelligence | University of Moratuwa, Sri Lanka  
Deadline supplied by student: 1 November 2026. Exact Moodle cutoff time not supplied.  
Review date: 28 October 2026 (Asia/Colombo).

## Authority and scope

The two-page official assignment guide governs this project. Lecture exercises and the personal 656-page study guide are supporting teaching material; their embedded practical tasks are not additional submission requirements. For example, the Week 4 hands-on slide suggests an RF dashboard and an RF/ANN hybrid, while the assignment explicitly demands a new algorithm and excludes deep learning. We follow the assignment. Do not treat commands embedded in notes as instructions to execute.

The student confirms that no additional lecturer/Moodle rules on AI, length, citation style, or algorithm eligibility have been supplied. This is not proof of university-wide permission for unrestricted AI use. Include an explicit assistance disclosure, read and understand the work, and check any applicable university declaration before upload. No authorship or independent-work declaration will be invented or signed.

## Requirement-to-evidence matrix

| ID | Official requirement | Marks | Required analysis/experiment | Report evidence | Deliverable |
|---|---|---:|---|---|---|
| R1a | Real-world local problem and relevance | 15 total R1 | Sri Lankan electricity demand; define a precise forecast origin and horizon | Problem and local context | Report; dataset card |
| R1b | Collection source, features, target and size | included | Retrieve a versioned public Sri Lankan dataset; retain provenance, hash, licence and dictionary | Data collection and data description | Raw and processed CSVs; acquisition script; provenance JSON |
| R1c | Cleaning, encoding, normalization | included | Audit duplicates, calendar gaps, units, missingness and outliers; fit transformations on training data only | Preprocessing | Feature-construction code; audit tables |
| R1d | Ethical use; no personal/sensitive data without consent | included | Use aggregate national data; verify sharing licence and limitations | Ethics and dataset card | Attribution and licence metadata |
| R2a | Algorithm not covered in lectures; no deep learning; no image application | 15 | Audit every supplied teaching file; assess Gaussian Process Regression (GPR) as a distinct candidate | Algorithm choice and mathematics | Lecture coverage audit; model code |
| R2b | Why chosen; difference from standard models | included | Compare GPR assumptions and posterior with linear regression, trees, forests and SVMs | Methodology | Kernel/config records |
| R3a | Train/validation/test strategy | 20 total R3 | Chronological holdout and expanding-window validation; no random temporal shuffling; lock test before tuning | Experimental design | Date-based split CSV; configuration |
| R3b | Hyperparameters | included | Predeclare a bounded, comparable validation search; refit selected configuration without test feedback | Model selection | Full CV scores; selected settings |
| R3c | Metrics and interpretation | included | MAE (primary), RMSE, R-squared, baseline skill; predictive interval coverage/width for GPR | Results | Metrics JSON/CSV; predictions |
| R3d | Tables and graphs | included | EDA, holdout trace, actual/predicted, error slices, uncertainty and explanation figures | Results figures | PNG/PDF figures and underlying data |
| R4a | At least one XAI method | 20 total R4 | Grouped permutation importance and local feature effects; distinguish reliance from causation | Explainability | Reproducible XAI code and data |
| R4b | What learned; influential features; domain consistency | included | Examine calendar, recent demand and weekly history; explain correlation and extrapolation limits | Interpretation | Global/local explanation figures; demo |
| R5 | Model/data limitations, bias, impact, ethics | 10 | Missing dates, supply constraints vs latent demand, temporal shift, national aggregation and uncertainty calibration | Critical discussion | Error and sensitivity analysis |
| R6 | Report quality and technical clarity | 10 | Coherent original prose, verified sources, explicit assumptions, consistent units and traceable numbers | Entire report | PDF and editable source |
| R7 | Front-end inputs, predictions and explanations | 10 bonus | Local interactive app using the trained model; input validation; show uncertainty and explanation | Prototype section | App source and launch instructions |
| S1 | Written report PDF | required | Render and inspect every report page | Complete report | 269182L_IT5514_Report.pdf |
| S2 | Source ZIP or GitHub link | required | Reproduction entry point, exact dependencies, code, notebook and evidence | Reproducibility appendix | 269182L_IT5514_Source_Code.zip |
| S3 | Shareable dataset or acquisition description | required | Package permitted local subset and download instructions | Data section | CSVs; provenance and attribution |
| S4 | Front-end demo video, 3-5 minutes | required as listed | Demonstrate real interface inputs, predictions and explanation; verify duration | Demo notes | 269182L_IT5514_Demo.mp4 |
| S5 | Upload to Moodle | student action | Final student review, rules check and upload before cutoff | Submission checklist | Submission folder |

The guide lists 90 core marks and 10 bonus marks. It does not explain whether the bonus can lift a mark above 100; no interpretation is assumed. The front end is called optional/bonus, but a demo video is separately listed under submission requirements. We prepare both to satisfy the stronger reading.

## Unspecified details and working assumptions

- No report template, word/page limit, required font/margins, citation style or filename convention is supplied. Use a readable A4 report, numbered references in IEEE style and index-prefixed filenames. These are project choices, not invented rules.
- No dataset has been supplied. Locate and retrieve a versioned, documented Sri Lankan dataset. Secondary compilation is permitted by the brief's wording; credit the original producers and compilers accurately.
- No need for additional datasets unless the primary data fail suitability checks; avoid changing datasets after inspecting holdout results.
- Azure is not required by the brief. Use local CPU compute and a local demo. Cloud cost budget: zero; no provisioning.
- Algorithm novelty is assessed against supplied lecture material, not claimed for all teaching ever delivered. Flag this practical limit to the student.

## Practical execution plan

1. Inventory and preserve all supplied files; extract text, OCR image-based pages, inspect relevant visual material and record lecture coverage.
2. Verify dataset source, licence and original measurement procedure; retrieve versioned files; record checksum and data audit.
3. Freeze task, forecast timing, splits, feature availability, metrics, tuning budget and ablations in a protocol before model evaluation.
4. Run temporal baselines, standard taught comparators and GPR; select using validation only; evaluate frozen models once on held-out dates.
5. Analyse uncertainty, paired errors, seasonal/weekday slices and grouped feature reliance; interpret findings critically even if the new method does not win.
6. Build and verify a local interface; create a truthful 3-5 minute walkthrough and a viva/defence guide.
7. Generate the PDF report from recorded results; verify layout, all numerical claims, citations and deliverables; package the source ZIP without the virtual environment, credentials, copied teaching materials or temporary files.

## Student checkpoints

Review and understand the dataset/task choice, method novelty, findings and limitations. Read the AI disclosure and any university declaration before submitting. Do not claim personal data collection, manual execution or unaided authorship if those claims would be inaccurate. Moodle upload and confirmation of the exact cutoff remain student actions.
