# Final verification and submission checklist

Prepared for D.V.S Sandaru Rashmika, 269182L, IT5514 Applied Machine Learning. Review date: 28 October 2026. Deadline supplied by student: 1 November 2026; exact Moodle time remains to be checked.

## Requirement coverage

| ID | Requirement | Technical status | Evidence |
|---|---|---|---|
| R1 | Local problem, collection, target/features, size, preprocessing and ethics | Complete | Report sections 1-2; dataset card; raw release and audit |
| R2 | New algorithm, no deep learning/image application, justification | Complete against supplied-material evidence | GPR methodology; 38-file lecture audit; no GPR occurrence in extracted/OCR corpus |
| R3 | Train/validation/test, hyperparameters, metrics, graphs and interpretation | Complete | Frozen protocol; full three-fold CV record; six-method comparison; test predictions |
| R4 | Explainability and domain interpretation | Complete | Grouped block permutation, PDP, non-additive local sensitivity and retrained ablations |
| R5 | Critical limitations, quality, bias, ethics and impact | Complete | Error and interval analysis; report section 11; explicit dispatch-proxy limits |
| R6 | Report quality and technical clarity | Complete technical review | 15-page A4 PDF; verified references; editable sources; rendered-page review |
| R7 | Bonus front end with inputs, predictions and explanations | Implemented and checked | Python inference API, HTML UI, actual model artefact, CUA checks and API verification |
| S1 | Report PDF | Prepared | `269182L_IT5514_Report.pdf` |
| S2 | Source ZIP or GitHub link | ZIP prepared | `269182L_IT5514_Source_Code.zip` |
| S3 | Dataset or acquisition instructions | Included in source | CC-BY-4.0 Sri Lankan subset, provenance, hashes and acquisition script |
| S4 | Front-end video, 3-5 minutes | Prepared and decoded | `269182L_IT5514_Demo.mp4`; 220.88 seconds (3 min 41 sec) |
| S5 | Moodle upload | Student action, not performed | Confirm exact cutoff and upload limits |

The official marking items total 90 core marks plus 10 bonus. No mark, grade guarantee, lecturer approval or platform acceptance is asserted.

## Executed verification

- Ten independent numerical/leakage checks passed. They verify chronological unique rows, every lag/rolling value against earlier calendar dates, target quality, development-only transforms/training, saved-model prediction reproduction, every main metric, and validation-only selection.
- The notebook executed all eight code cells with zero error outputs in an isolated project reproduction. Every numeric heldout prediction matches the recorded run exactly (maximum absolute difference 0 MWh on this machine).
- API checks passed for model health, historical prediction equality, changed-input inference, preserved historical actuals, invalid values, and future-period warnings.
- Browser checks verified historical replay, an edited input, invalid-input rejection and the last-valid-estimate label, evaluation evidence and the data/method tab. No browser console error was observed during the check.
- The latest PDF was rendered and all 15 pages visually inspected. No clipped text, orphan overflow pages or overlapping figures/tables were found. A character-bound check found zero characters outside the safe page bounds.
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

The report uses an index-prefixed naming convention and numbered IEEE-style references because the supplied brief specifies no names or style. The report is approximately 4,843 words including tables, references and captions; there is no supplied word limit.
