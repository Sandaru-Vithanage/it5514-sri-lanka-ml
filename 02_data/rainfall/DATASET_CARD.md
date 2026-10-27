# Independent task: Colombo dekadal rainfall

Publisher: World Food Programme (WFP), distributed through the Humanitarian Data Exchange (HDX). Source measurements: Climate Hazards Center CHIRPS version 2; administrative aggregation is provided by WFP. This project uses existing tabular administrative aggregates and performs no image processing.

- Dataset page: https://data.humdata.org/dataset/lka-rainfall-subnational
- Metadata API: https://data.humdata.org/api/3/action/package_show?id=lka-rainfall-subnational
- Package: 4302257e-5fa6-4c88-b8f7-f78730d8c48b
- Resource: afc6a8ca-dc55-4eb4-baf0-4afaa2c6673e
- Snapshot retrieved 28 October 2026 local time; original CSV and full metadata retained unchanged.
- SHA-256: `0cbede43ed79c8ac198e64592bd4a2d04da647b06853e9ca7083e3725f0716b5`
- HDX licence metadata: `cc-by`, Creative Commons Attribution International (CC BY), https://opendefinition.org/licenses/cc-by/. The record does not specify a numbered CC version; no version is invented here. Retain this attribution and the source metadata when sharing adaptations.

The CSV has 56,066 rows, 25 districts and nine provinces. Select admin level 2, Colombo PCODE LK11, `version=final`, finite nonnegative `rfh` (mm). Colombo has 1,647 final records and no duplicate final dates. Reindex on the 36-dekad annual calendar (days 1, 11, 21 each month) before lagging; the third dekad has variable length. Modelling uses 936 complete rows, 2000–2025. No extreme-value trimming or target interpolation is performed.

The task predicts the final rainfall amount for the next dekad retrospectively, using lag6, lag7, lag9, lag36; the three-dekad mean/std ending at lag6; annual sine/cosine; trend. WFP metadata explains that final observations arrive mid-month after the observed month. The six-dekad minimum delay conservatively handles that latency, but archived real-time vintages are unavailable: later revisions remain a limitation. No supplied same-period rolling totals, anomaly ratios or climatology fields enter the model. The training-only seasonal-median baseline is computed independently inside every fold and from 2000–2023 for the final 2024–2025 holdout.

Development: 864 rows, 2000–2023. Validation: 2021, 2022 and 2023 expanding annual folds. Test: 72 rows, 2024–2025. The protocol was written before scoring this independent task. Models are refitted on rainfall: this is not an external validation of the electricity-trained model. Selection uses mean validation MAE, all comparisons are disclosed, and no model is retuned after test inspection.

HDX is a rolling download, so rerunning acquisition in the future may yield changed bytes. `03_code/acquire_rainfall.py` refuses a mismatched hash. The pinned original snapshot is included in the private Git repository and standalone source ZIP for exact reproduction. Adaptations comprise final-record filtering, Colombo selection, lag/calendar features, chronological splitting and model evaluation. CHIRPS is a gridded estimate, not a district-wide gauge census; spatial aggregation, revisions, distribution support and two-year holdout length limit interpretation.
