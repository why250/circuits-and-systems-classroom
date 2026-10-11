# Implementation reference for this classroom

This is a project adaptation guide. Linked files are authoritative for numerical values and implementation details. Read relevant code before making changes instead of duplicating models or complete operating instructions.

## Project conventions and locations

- [web/README.md](../../../../web/README.md): authoritative architecture, development commands, topic creation, public catalog, numerical verification, and visitor analytics requirements.
- [package.json](../../../../web/package.json): current commands and dependencies. The `/dev/null` redirection in `pnpm check` does not work in the default Windows command interpreter. Run its existing checks individually when necessary and keep failures visible. Never report failed checks as passed.
- [Base.astro](../../../../web/src/layouts/Base.astro): shared theme, navigation, and footer. Astro routes mount each topic's interactive Svelte components.
- `web/src/illustrations/<topic>/`: pure computational models and topic components. `web/src/components/ui/` and `chart/`: shared controls and plots.
- `web/python/` and `web/tests/`: reference models and numerical tests. Follow the README's Python reference conventions for new scientific models. Reuse sufficiently validated models directly; add checks for new teaching conclusions or uncovered conditions.

## The user's own free static hosting

- [CLOUDFLARE-PAGES.md](../../../../web/CLOUDFLARE-PAGES.md) is the authoritative independent deployment guide. The default project is `why250-circuits-classroom`, with production origin `https://why250-circuits-classroom.pages.dev`.
- When the user requests publication, run `node scripts/deploy-pages.mjs` in `web/` after the relevant checks pass. The script sets its own `SITE_URL`, builds, and uploads from an isolated static directory. Confirm the signed-in user account and existing project first to avoid duplicate creation.
- [deploy-pages.mjs](../../../../web/scripts/deploy-pages.mjs) and [pages-assets.mjs](../../../../web/scripts/pages-assets.mjs) handle builds, static asset preparation, and uploads. They do not run upstream domain binding or analytics Worker deployment. Keep visitor placeholders when no independent analytics service is configured.
- Verify the live lesson's HTTP response, actual interactions, and canonical origin. If the lesson is already live and satisfies the current request, verify and deliver it without uploading an identical deployment.

## Implemented introductory example: time-interleaved ADCs

The entry point is `/adc/time-interleaved-adcs/`. Learners know ordinary ADCs and spectra but are new to time interleaving.

- [lesson.ts](../../../../web/src/illustrations/timeinterleave/lesson.ts): objectives, predictions, operations, explanations, and transfer checks. Use its field organization as a reference without forcing every lesson into the same pattern.
- [GuidedInterleaving.svelte](../../../../web/src/illustrations/timeinterleave/GuidedInterleaving.svelte): progressively available controls, prediction baselines, error switches, parameter restoration, expandable explanations, and comprehension checks.
- [TimeInterleaveLesson.svelte](../../../../web/src/illustrations/timeinterleave/TimeInterleaveLesson.svelte): switches between guided mode and the original full workbench. Components remain mounted to preserve session state. Progress currently does not survive a refresh.
- [model.ts](../../../../web/src/illustrations/timeinterleave/model.ts): existing time-interleaving model. Output spurs from `read()` already use the FFT power convention through `outputSpurs()`. Do not add another 3 dB to Nyquist spurs.
- [timeinterleave-lesson.test.ts](../../../../web/tests/timeinterleave-lesson.test.ts): independently projects sampled data to verify offset spur locations, gain amplitudes, the frequency-times-timing-error relationship, and total error power from random jitter.

The lesson moves from two ideal channels to four, then examines offset, gain, fixed skew, and independent random jitter separately. Introductory experiments hold the total sampling rate at 2 GS/s, use 14-bit quantization and a shared analog bandwidth, and enable only the current mechanism. Inputs near 125/250 MHz are adjusted to coherent bins; use actual input frequencies when evaluating doubling relationships.

Transferable lessons:

- Separate questions that hold the total sampling rate fixed from those that hold each channel's rate fixed. Transfer checks test whether learners notice the fixed condition.
- Hold error values fixed when comparing gain and skew; sweep input frequency to distinguish amplitude relationships. Their image locations can coincide.
- Say "jitter produces a noise floor" only for this experiment's independent random jitter model. Periodic jitter can also create sidebands; do not generalize a model-specific result into a universal rule.
- Explain channel rate, total rate, and analog bandwidth separately. The reused sinusoidal foreground calibration has a limited scope. Introductory lessons do not run calibration; having a calibration function in the model does not mean calibration has been taught.
- Provide anchor links between controls and plots on narrow screens. Match channel timing-table colors to waveform colors and use the actual frequency axis for both analytical locations and measured spectrum lines.

This example has passed programmatic and browser verification. Educational effectiveness still requires learner feedback. Later topics should test whether the workflow transfers successfully.