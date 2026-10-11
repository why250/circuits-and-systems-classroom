---
name: guided-circuit-lessons
description: Create or improve runnable guided circuit and system lessons in the Circuits & Systems Classroom project. Use for requests to build a teaching page, learn a topic interactively, or predict before experimenting. General knowledge questions, technical note organization, and appearance-only changes are outside this workflow.
---

# Guided circuit lessons

Turn a topic into experiments in which learners predict, operate, observe, explain, and transfer their understanding. Use the project's existing components and validated models. Model correctness, working interactions, and effective learning require separate verification.

## Establish the starting point

- Read applicable project instructions and the [project reference](references/classroom.md) to locate existing pages, models, and validation commands for the topic.
- Choose an entry point from the user's goal and confirmed background. If missing information affects the lesson, ask about their background or learning objective while inspecting existing material. Do not ask again for information already provided.
- Use English for teaching pages and project content. Add a Chinese version only when explicitly requested, keeping English as the default. Communicate with the user in Chinese and use guided experiments. New user instructions take precedence.
- Give each experiment an observable learning outcome, such as identifying gain and timing mismatch by changing input frequency. Build intuition from the smallest mechanism before adding channels, errors, or constraints. Let the topic determine the number of experiments.

## Design experiments rather than collections of controls

Organize the following cycle for each learning objective, adapting it to the topic:

1. **Predict:** Ask a concrete question that the experiment can distinguish. Include plausible misconceptions and an "I'm not sure yet; let's experiment" option. Prediction should not block learning.
2. **Experiment:** Provide a reproducible baseline, an operation, and a comparison. Emphasize one mechanism at a time and hold other parameters constant; state what remains fixed. Every visible control should help answer the current question.
3. **Observe:** Show the actual input, key units, and readings. Synchronize related plots and provide a way to disable the current error or restore the step's parameters. Label analytical predictions and simulation measurements by source.
4. **Explain:** Let the learner expand the explanation. Connect observations to the mechanism, then give concise equations, symbols, and approximation conditions. Do not force a quiz when the user wants to read the derivation directly.
5. **Check transfer:** Change a condition to test the same mechanism, with reasoning and feedback for misconceptions. Feedback applies to that question; it does not certify mastery of an entire course.

When distinguishing adjacent experiments, state whether a parameter change should affect **position, amplitude, noise floor, or a metric**. Explain conventions for frequency, amplitude, RMS, peak values, power, and one-sided spectra wherever they affect interpretation.

## Implement and verify

- Reuse existing models and plots for the topic first. Separate teaching content, stage state, and simulation calculations. Add a learning mode or entry point when established functionality needs to remain available.
- Clearly label the prediction baseline and update plots after operations. Keep explanation expansion independent of quiz answers. Preserve experiment state across mode switches where practical and make stage resets explicit.
- State model inputs, units, assumptions, valid range, and unimplemented mechanisms. Show the actual value when coherent frequency bins, quantization, or boundary handling alter the requested input. Use reproducible seeds for random experiments; do not present one random waveform as a deterministic law.
- Verify numerical values that affect teaching conclusions using independent analytical relationships, dimensional checks, limiting cases, independent time/frequency-domain calculations, or Python references. Do not use the page's prediction function as the sole evidence of its correctness. Pure layout or wording changes do not need tests that merely mirror the implementation.
- Run the project's required type checks, tests, and build. In a browser, exercise prediction, controls, comparisons, explanations, incorrect-answer feedback, and stage/mode switching. Check narrow-screen plot readability and keyboard operation. Report tool limitations and unverified areas accurately.
- Preserve the site's shell, theme, navigation, and visitor analytics conventions. Decide whether a new route belongs in the public catalog using project publication standards and the user's request. Follow existing authorization for deployment, commits, and publication.
- The hosting target is the user's own free static Cloudflare Pages site. When the user requests publication, follow the independent deployment procedure in the [project reference](references/classroom.md), deploy to the existing `why250-circuits-classroom` project, and verify the live lesson URL before delivery. Do not use the upstream author's account, custom domain, or analytics Worker.

## Deliver and iterate

Deliver a directly accessible page: a local URL for local work, or the user's Cloudflare Pages URL after requested deployment has been verified. State the learning entry point, scope, and validation results. Adjust experiment order, explanation depth, and interactions using actual learner feedback; passing tests alone does not prove educational effectiveness. Add validated general lessons from new topics to this skill, while keeping topic-specific physical models and derivations in their own modules.

Example:

> Use $guided-circuit-lessons to teach me PLL loop bandwidth and phase noise. I understand feedback and spectra. Start with experiments that change one variable at a time, then explain the equations and create a teaching page in this project.