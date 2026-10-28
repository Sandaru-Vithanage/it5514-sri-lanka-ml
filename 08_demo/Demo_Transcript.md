# Front-end demo transcript

Narrated captured-interface walkthrough, using actual states of the working hosted Azure application. Visual panning is an edit, not continuous screen recording. Narration is the macOS Samantha system voice.

## 1. A Sri Lankan forecasting study

This is the Applied Machine Learning study prepared for Sandaru Rashmika, index number two six nine one eight two L. Lanka Dispatch forecasts next day recorded electricity dispatch energy in Sri Lanka. The source is a versioned public compilation of PUCSL records. We rebuilt daily energy after finding duplicate plant timestamps and a missing quarter hour conversion in the published daily file. The main unfamiliar algorithm is Gaussian Process Regression. This is historical research, with no live grid connection.

## 2. Replay a case on Azure

The working interface is deployed to Azure. Select fifteen January twenty twenty five and load recorded inputs. Six history values describe demand lags, the previous week mean, and variability. The date supplies calendar features. The original trained Gaussian process predicts forty two point three three gigawatt hours, with a nominal ninety five percent observation interval from thirty seven point four three to forty seven point two three. The historical actual is displayed separately. The browser calls real Python inference from the saved model.

## 3. Change history and inspect sensitivity

Change only previous day energy to forty two gigawatt hours and generate another forecast. The estimate becomes forty four point two two. Hypothetical inputs are clearly labelled and the historical actual stays fixed. Group replacement bars show separate changes against a representative training day. They are reference dependent sensitivity checks, not additive contributions or causal explanations. The wider study also includes grouped block permutation, partial dependence and retrained feature ablations.

## 4. Reject invalid values

A negative input produces an error, and the panel is labelled last valid estimate. Backend checks independently reject negative, non finite and oversized requests. Scenarios outside the evaluated date range receive warnings. These checks also passed against the actual hosted HTTPS service.

## 5. Interpret the original comparison

Three chronological validation windows selected settings before the original ninety seven day test. GPR has mean absolute error one point five nine nine gigawatt hours, twenty nine point seven percent below weekly naive. It does not dominate: SVR has the lowest test mean absolute error and random forest the lowest root mean squared error. Grouped importance indicates strongest reliance on demand history and weekly calendar. Nominal ninety five percent intervals cover ninety two point eight percent, so uncertainty estimates still need critical interpretation.

## 6. Test broader algorithms and data

The extension adds NGBoost, K nearest neighbours and gradient boosting, giving seven learned algorithms on two Sri Lankan tasks. Added electricity comparisons are explicitly post hoc because the original test was already seen. The separate Colombo rainfall audit uses CHIRPS records, delayed inputs and a training embargo for publication timing. Review corrected a preliminary timing issue; that history is preserved. The seasonal median wins with mean absolute error forty one point three nine millimetres, ahead of SVR and GPR. Novelty does not guarantee better accuracy.

## 7. Inspect deployment and source

The deployment panel shows the actual Azure address, public GitHub repository, source commit and model fingerprint. Anyone can inspect the code. Azure App Service uses Python three point thirteen and the free F one plan. Predictions match local inference within one millionth of a megawatt hour. The approved ten dollar credit cap is a maximum. Free tier quotas and cold starts limit availability.

## 8. Deploy automatically after validation

This successful GitHub Actions run validates the saved model before deployment. App or model changes pushed to main rebuild the explicit bundle, check all ninety seven saved predictions, deploy to Azure, and verify nine HTTPS checks. Pull requests validate only. Short lived federated credentials access this app. Deployment does not retrain the model.

## 9. Keep failure and limitations visible

Four February, Independence Day, is a large failure: the model forecasts about forty four point three seven gigawatt hours against recorded energy thirty three point seven three. Holiday indicators were omitted from the frozen predictors; future redesign needs fresh evaluation. Dispatch coverage and publication timing also constrain interpretation. The package includes reproducible code, pinned data, both notebooks, experiments, report and deployment evidence. This walkthrough uses genuine hosted interface captures, edited panning and synthesized narration. Student review and accurate assistance disclosure remain essential.