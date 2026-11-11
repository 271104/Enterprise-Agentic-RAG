# Evaluation

`evals/app.py` provides a Streamlit evaluation UI. Start the API first, then run `streamlit run evals/app.py`.

The live pipeline reads `evals/golden_dataset.json` and calls the API. RAGAS metrics call a judge model and may incur cost and rate limits. Tool correctness and guardrail evaluation use the repository’s existing evaluation logic. Results are meaningful only for the exact model configuration, document index, dataset revision, and run parameters; record those alongside any reported scores.

The checked-in datasets are test inputs, not benchmark results. This repository makes no performance or quality claims. Evaluation requests and documents may leave the local machine for configured model providers.
