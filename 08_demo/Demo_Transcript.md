# Front-end demo transcript

Narrated captured-interface walkthrough, using actual states of the working local app. Visual panning is an edit, not continuous screen recording. Narration is the macOS Samantha system voice.

## 1. A Sri Lankan forecasting study

This walkthrough presents Lanka Dispatch, the Applied Machine Learning prototype prepared for Sandaru Rashmika, index number two six nine one eight two L. It forecasts the next local day of recorded electricity dispatch energy in Sri Lanka. The source is the Sri Lankan raw subset of a versioned public dataset compiled from PUCSL records. The daily target was rebuilt from raw readings after detecting duplicate plant and timestamp records and a missing interval conversion in the published daily file. This is a historical research tool, with no connection to live grid operations.

## 2. Replay a recorded case

In the Forecast Lab, select the day to predict and load its recorded inputs. The six editable values describe earlier demand: one, two, seven and fourteen day lags, and the previous week's mean and variability. Calendar coordinates come from the selected date. For fifteen January twenty twenty five, the trained Gaussian process predicts about forty two point three three gigawatt hours. Its nominal ninety five percent observation interval runs from thirty seven point four three to forty seven point two three. The historical observed outcome is displayed separately. The interface calls the saved Python model, rather than a mock formula.

## 3. Edit an input and inspect the effect

Next, change only the previous day's energy to forty two gigawatt hours and generate another forecast. The estimate rises to about forty four point two two gigawatt hours. The badge identifies hypothetical inputs, while the recorded outcome stays unchanged. Below the estimate, three bars show separate group replacement sensitivities against a representative training day. They describe changes in this fitted model's output. They do not add up to the prediction and they do not prove causal effects. Internally consistent historical inputs remain preferable to arbitrary scenarios.

## 4. Reject invalid input

The interface also checks input validity. Entering a negative energy value produces an error instead of accepting a new prediction. The prediction panel is explicitly labelled as the last valid estimate. The backend independently rejects negative, oversized and non finite values. Dates outside the evaluated historical period receive a warning because no live data feed is available.

## 5. Read the comparative evidence

The evaluation tab reports the same saved experimental results as the report. Three chronological validation windows selected hyperparameters before the ninety seven day test. Gaussian process regression achieves a mean absolute error of one point five nine nine gigawatt hours, improving the weekly naive baseline by twenty nine point seven percent. It does not win every comparison: support vector regression has the lowest test mean absolute error, and random forest has the lowest root mean squared error. The global explanation shows greatest reliance on demand history and weekly calendar. Nominal ninety five percent intervals cover ninety two point eight percent of test outcomes.

## 6. Inspect a failure and its limits

Finally, replay four February twenty twenty five, Independence Day. The model forecasts about forty four point three seven gigawatt hours, while recorded dispatch is only thirty three point seven four. Several large errors coincide with verified Sri Lankan holidays omitted from the frozen predictors. That association suggests a future improvement, but adding holiday features now would require a fresh holdout. Recorded dispatch is also a coverage limited proxy for demand. The source package includes data provenance, code, executed notebook, model artefacts, explanations and independent checks. This video uses genuine interface captures with panning and synthesized narration. Student review and an accurate assistance disclosure remain part of submission.