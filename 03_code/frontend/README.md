# Ocean Observatory frontend

The student selected the first displayed Product Design concept on 29 October 2026. This integrates that visual direction into the existing Flask/GPR application; it does not replace or retrain the model.

## Build

Use Node.js 24 and npm:

```sh
cd 03_code/frontend
npm ci
npm run build
npm run check
```

`src/app.template.html`, `src/style.css`, `src/main.js` and `src/chart-data.js` are the editable sources. The deterministic build writes `../app.html`, including compiled Tailwind/daisyUI styles, selected ECharts modules, Motion, Inter Latin variable font and the regular Phosphor icon font. No runtime CDN requests are required. Dependency versions and integrity hashes are pinned in `package-lock.json`; applicable notices are in `THIRD_PARTY_NOTICES.txt`.

The generated HTML is committed so Python-only local reproduction still works. GitHub Actions rebuilds it from the locked dependencies and rejects a mismatch before constructing the original explicit 15-file inference bundle. Node is used during the GitHub build, not at Azure application startup.

## Preview with the real model

From the project root after installing the existing Python dependencies:

```sh
python -m flask --app 10_deployment/wsgi.py run --host 127.0.0.1 --port 8773
```

Open the local address in a browser. Production continues to use the existing Gunicorn startup command and Azure Free F1 plan.

## Behaviour and scope

- Inputs and API payloads retain their original meaning; displayed GWh is converted to MWh for inference.
- The uncertainty chart maps the actual returned values to a numeric axis, includes outlying actuals, and omits unavailable actuals. The recorded 42.07 GWh lies left of the 42.33 GWh forecast.
- Inputs changed after a successful run immediately label the displayed estimate as stale. Invalid requests preserve a clearly labelled last valid result.
- Busy controls, visible errors, input labels, keyboard tabs, a skip link, chart text alternatives and reduced-motion handling support the core flow.
- The responsive chart recalculates its settings on resize. Phone inputs use 16px text and the mobile link jumps to the input panel.
- Original evaluation, provenance, extended task evidence and public deployment details remain available. Charts do not imply live-grid access or calibrated operational guarantees.

The design QA report and captured comparison evidence are in the project root and `11_design/`.
