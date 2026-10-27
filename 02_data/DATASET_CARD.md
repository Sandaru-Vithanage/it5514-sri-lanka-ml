# Sri Lankan recorded dispatch energy: dataset card

## Provenance and permission

Original producer: Public Utilities Commission of Sri Lanka (PUCSL), actual system dispatch API. Dataset compilers: Oliver G. Coombes, Kieran Hunt and Hannah Bloomfield. Pinned release: SASEA Electricity Demand Data for 2013-2025, Zenodo v1, 22 September 2025, DOI https://doi.org/10.5281/zenodo.17175212. Licence in the verified Zenodo API metadata and Sri Lankan YAML: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Accessed 28 October 2026. The student did not personally measure electricity or collect the original API records.

The source ZIP checksum is MD5 22921011c0fdabea0df5f926f3372a9e. The extracted raw Sri Lankan CSV SHA-256 is 7dc4665e317d3fa718cea7845587cc97b7a5c13de110a5bddbd57c524f2b5a97. Preserve attribution to both PUCSL and the dataset authors. Processed files are adaptations produced for this project; the original files are retained unchanged.

Original source endpoint documented by the authors: https://gendata.pucsl.gov.lk/api/actual-system-dispatch. Reproduction uses the pinned archive, rather than assuming the current API returns identical historical values. Upstream scripts were read as documentation, not executed. No household, personal or sensitive data are present in the selected data.

## Raw schema

| Field | Meaning | Unit/type |
|---|---|---|
| timestamp | UTC timestamp supplied by the original release | ISO-8601 |
| powerPlantId | Opaque generating-unit identifier | integer |
| dispatchValueInMW | Recorded plant dispatch power; can be zero, negative or null | MW |

There are 2,902,337 raw rows, 44 plant identifiers across the whole period and 79,489 unique timestamps after deduplication. Local coverage is 1 January 2023 at 05:30 through 8 April 2025 at 05:30, Asia/Colombo. Plant membership varies: 33-42 plants are present at individual timestamps. This does not certify that all national generation is measured.

## Transformation and quality gates

1. Convert timestamps to Asia/Colombo before deriving dates.
2. Check duplicate plant/timestamp values for conflicts. There are no conflicts; remove 29,875 repeated keys, retaining the first identical record.
3. Sum recorded plant values per timestamp, then multiply by 0.25 hours to obtain interval MWh. Sum within each local day. Explicitly distinguish power (MW) from energy (MWh).
4. Require 96 distinct 15-minute timestamps per target day. Exclude the two partial boundary days (74 and 23 intervals).
5. Exclude 12 days with explicit null plant readings. No target interpolation, backward filling, or replacement by future data is performed. The remaining 815 dates have eligible targets; this does not imply perfect plant coverage.
6. Retain negative readings, because net station use or measurement conventions are not resolved by the source. Clipping negatives would add 549.25 MWh across the entire record and at most 39 MWh on one day; this is a sensitivity audit, not evidence that either interpretation is universally correct.
7. Retain 10 all-zero system intervals on 9 December 2023 and 9 February 2025. They may reflect interruptions or telemetry problems; neither explanation is inferred from the values alone. No difficult test outcomes were deleted.
8. Reindex on the full daily calendar before lagging. Build demand lags of 1, 2, 7 and 14 days and seven-day statistics over t-7 through t-1. Drop modelling rows whose required historical values are missing. This leaves 756 rows, with 659 development and 97 test days.

The published daily CSV equals the local-day sum of raw, undeduplicated MW readings exactly (maximum absolute discrepancy 0). It therefore fails the documented 0.25-hour conversion and includes repeated keys. The median published/reconstructed ratio is 4.041427. The project uses a reconstructed target instead of dividing the daily CSV by four, which would leave duplicate-record inflation.

An independent plausibility check uses PUCSL's 24 December 2024 report: reconstructed dispatch is 41.66825 GWh; the report lists 41.96 GWh excluding non-telemetered generation and 44.92 GWh including estimates. This supports the energy scale but is not proof of matching coverage for every day. See https://www.pucsl.gov.lk/wp-content/uploads/2024/12/Generation-Cost-24th-Dec_2024-R.pdf.

## Processed schema and intended use

`daily_energy_quality.csv` contains the raw integration, quality indicators, published comparison and eligible target. `modelling_table.csv` contains date, eleven predictors, target_MWh and development/test labels. `feature_eligibility.csv` retains ineligible dates for audit. The feature dictionary is documented in the report and code.

Target: recorded dispatched energy for local calendar day t, in MWh. Model outputs/plots may display GWh (1 GWh = 1,000 MWh). Predictors: historical dispatch and known target-date calendar values. Intended use: a retrospective one-day-ahead educational forecasting study. It assumes completed t-1 telemetry is available before t begins; publication latency was not established.

The historical test evaluates rolling observed inputs with fixed model parameters. It is not a forecast issued once for the whole test period. Model parameters are fitted through 31 December 2024; the test covers 1 January-7 April 2025. No test targets are used for model selection, scaling, fitting or post-test recalibration. An earlier test target can later become an observed lag for a subsequent test day, as required by the declared rolling-input task.

## Limits and exclusions

Recorded dispatch is not unconstrained consumer demand, household consumption, individual billing data, or a complete estimate of distributed solar. Supply restrictions, grid losses, changing reporting plant coverage and missing telemetry can alter its relationship with end-use demand. National aggregation cannot establish district or household fairness. The dataset has only a little over two years of history and the test ends before Sinhala and Tamil New Year 2025. Holiday flags and weather forecasts are omitted in the frozen study and should be evaluated on a fresh future holdout in subsequent work.

The original YAML files contain placeholder DOIs and inconsistent textual year ranges. Use the minted Zenodo record and measured timestamp coverage as the authoritative version/provenance evidence. Do not reproduce the placeholder DOI as a citation.
