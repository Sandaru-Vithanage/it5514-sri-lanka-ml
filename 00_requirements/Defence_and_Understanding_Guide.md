# Student defence and understanding guide

Use these questions to explain the work in your own words. Read the report and execute the code before making a declaration about your contribution. AI assistance is disclosed; these are preparation prompts rather than a script to conceal assistance.

| Question | Evidence-based answer to understand | Where to inspect |
|---|---|---|
| What exactly is predicted? | The next local day's recorded dispatch energy in MWh, not household consumption or all latent electricity demand. | Data card; `prepare_data.py` |
| Why is Sri Lanka an authentic local context? | The raw measurements are from PUCSL generating-unit dispatch; the public release contains a specific Sri Lankan subset. | Raw YAML and provenance |
| What did the student actually collect? | A pinned public secondary dataset; the original API collection belongs to PUCSL and the dataset compilers. | Provenance disclosure |
| What was wrong with the released daily file? | It equals the undeduplicated local-day sum of MW readings. It omits multiplying by 0.25 hours and includes repeated timestamp/plant keys. The ratio to reconstruction is about 4.041, rather than exactly four. | Data audit and original CSVs |
| Why not just divide by four? | That leaves duplicate inflation. Rebuild from deduplicated raw readings. | `prepare_data.py` |
| Why drop boundary days and null days? | Partial timestamp coverage and explicit missing plant readings make energy labels incomplete. This is a quality decision, with a disclosed selection-bias cost. | Daily quality table |
| Do 96 timestamps prove national completeness? | No. Plant coverage varies, and unreported plants or distributed generation can be absent. | Data card limitations |
| Why keep negatives and zeros? | Their physical/measurement meanings are not settled. Blind clipping can erase genuine station-use or interruption signals. The magnitude of negative clipping was audited. | Data audit |
| Is GPR a new algorithm here? | It was not found in all supplied lecture/OCR text; GMM and Gaussian linear bases are different. Unsupplied classroom material still needs confirmation. | Lecture coverage audit |
| What is a Gaussian process? | A distribution over function values whose finite subsets are jointly Gaussian; the kernel expresses covariance. Conditioning gives a posterior mean and variance. | Report section 3; GPML chapter 2 |
| How is it different from SVR? | Different objective and inference: SVR uses an epsilon-insensitive point-prediction objective; GPR conditions a probabilistic prior and supplies model-based uncertainty. Both may use kernels. | `models.py` |
| What does Matérn-5/2 imply? | A smooth but less infinitely smooth function prior than RBF, with a tunable length scale. The scalar distance operates after training-only standardization. | Model source and report |
| What are the units of the fitted noise? | Variance in normalized target space. Predictions and SD are transformed back to MWh. | Saved GPR kernel |
| Why no random split? | Future rows must not inform earlier forecasts. Chronological folds evaluate later periods with earlier fitted parameters. | Frozen protocol |
| Why are previous test outcomes used as later lags? | For the declared rolling one-day-ahead task, yesterday's completed reading is known today. This is not a fixed-origin 97-day-ahead forecast. | Feature construction and validation |
| Why no purge gap? | Targets cover one day, and evaluation inputs use only completed prior days. There are no overlapping future targets or future-dependent transforms. Publication latency remains an assumption. | Task timing in protocol |
| Which model won? | RF won mean validation MAE. SVR has lowest test MAE, RF lowest test RMSE; GPR improves weekly naïve but does not dominate. | CV and test metrics |
| Why compare RF using a bootstrap? | RF was selected as the best taught comparator by CV, not chosen retrospectively from the test. Paired block resampling addresses local error dependence. | Bootstrap JSON |
| Are GPR and RF significantly different? | The 7- and 14-day-block intervals for their MAE difference include zero. No established advantage is claimed. | Report section 7 |
| Is 92.8% coverage calibrated? | It is the empirical coverage on 97 outcomes, below nominal 95%; small dependent samples and model assumptions limit a formal calibration conclusion. | Uncertainty JSON |
| Why are the intervals wide? | They include the learned observation noise and uncertainty conditional on the kernel; exceptional events remain unmodelled. | GPR implementation |
| What explains the worst errors? | Several coincide with verified Sri Lankan holidays; a zero-interval day may also reflect interruption or telemetry problems. The model has no holiday flag. This is an association, not causal proof. | Worst errors and holiday source |
| Why not add holidays now? | Diagnosing and redesigning on the same test would contaminate final assessment. A revised model needs a fresh holdout or new outer validation. | Frozen-test policy |
| What does grouped importance mean? | How much this fitted model's MAE worsens when a feature group is shuffled; correlated histories stay together. It is not a causal effect. | Permutation repeats and summary |
| Why a random phase after block shuffling? | Shuffling whole weeks can leave cyclic weekday coordinates unchanged. A phase offset avoids that degeneracy. | `explain_and_plot.py` |
| What is the difference between permutation and ablation? | One perturbs inputs to a fixed model; the other retrains a different model with fewer features. They measure different quantities. | Ablation CSV |
| Are the local bars SHAP values? | No. They are separate signed output differences against representative group replacements; they do not add to the prediction. | Local sensitivity table |
| Why might PDPs mislead? | Replacing one lag while fixing correlated histories can generate physically unsupported combinations. The plotted effects are model responses, not interventions. | Report section 10 |
| Is the app actually connected to ML? | Yes. The Python API loads the saved scaler/GPR pipeline; changing an input calls the model and changes its prediction. | `app.py`; app verification |
| Why no Azure? | Daily data and exact GPR fit readily on the local CPU. Azure adds cost without resolving data or validity limitations. | Execution log |
| Can the work be submitted without review? | No. Understand, verify and revise the draft, retain accurate disclosure, confirm module rules and exact Moodle cutoff, and upload personally. | Submission checklist |

## Suggested rehearsal

1. Open the report and explain the target reconstruction without reading the text verbatim.
2. Run the four canonical scripts in a separate extracted copy. Inspect a test row and independently calculate its lag 7 by subtracting seven calendar days.
3. Open the interface and reproduce 15 January 2025. Change previous-day energy to 42 GWh, and explain why the outcome is hypothetical while the historical actual stays unchanged.
4. Load 4 February 2025 and explain the large error without claiming certainty about its cause.
5. Describe one methodological weakness you would fix in a genuinely new experiment, and how you would reserve a new holdout.


## Broader experiments and deployment

- Why GPR plus NGBoost? GPR is the focal new method; NGBoost compares conditional distributions through natural-gradient tree boosting. Familiar KNN/gradient boosting test whether the outcome depends on one model family. Novelty is not evidence of superiority.
- Which algorithms were actually run? Linear regression, random forest, SVR, GPR, NGBoost, KNN and conventional gradient boosting on both tasks. Electricity also has persistence/weekly-naive baselines; rainfall has prior-year naive/training-only seasonal median.
- Why are extra electricity results post-hoc? Its original holdout had already been inspected before adding algorithms. Settings still use development folds, but its status cannot be reset to untouched.
- What did rainfall review catch? Delaying features does not make late training labels available at the forecast origin. Final rainfall totals may be published the following month. Version 1.1 leaves November–December out of each preceding training year, in addition to lagging inputs by at least six dekads. The invalid first pass is archived. Since outcomes were already seen, corrected scores are transparently retrospective.
- What are the corrected rainfall results? Seasonal median MAE 41.39 mm; SVR 48.17; GPR 51.86; NGBoost 63.09. Do not turn a test ranking into a deployment-selection rule. GPR's broad intervals cover 94.4% but 51 lower bounds are negative; NGBoost covers 80.6%. A positive-support distribution is a future hypothesis, not a hidden post-test fix.
- What proves deployment? Actual HTTPS API responses reproduce local original GPR predictions within 10^-6 MWh; health exposes the identical model SHA-256 and application source commit. The hosted UI accepts edited inputs, labels hypothetical history and rejects invalid values.
- Why Azure App Service? One Python 3.13 Flask/Gunicorn application hosts the existing CPU model and integrated UI. F1 is free shared compute, sufficient for a small research demo; quotas/cold starts limit reliability. No paid ML endpoint, GPU or database is needed. The authorized US$10 is a maximum, not a spend target.
- Why a private repo and ZIP? The user requested private review. Repository visibility was verified. A marker requires access, so the source ZIP provides a complete assessment fallback. No collaborators were invited automatically.
- What does the video show? Genuine captured states of the hosted interface, edited with panning and synthesized narration; not continuous screen recording. It covers real forecasts, edits, validation, original/extended evidence, failures, Azure URL and repository provenance. Read the transcript and rerecord personal narration if required.
