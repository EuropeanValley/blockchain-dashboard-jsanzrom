[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/N3kLi3ZO)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=23640751&assignment_repo_type=AssignmentRepo)
# Blockchain Dashboard Project

Use this repository to build your blockchain dashboard project.
Update this README every week.

# Blockchain Dashboard Project

Use this repository to build your blockchain dashboard project.
Update this README every week.

## Student Information

| Field | Value |
|---|---|
| Student Name | Jorge Sanz Romera |
| GitHub Username | jsanzrom |
| Project Title | CryptoChain Analyzer Dashboard |
| Chosen AI Approach | M4: Z-score anomaly detection on block inter-arrival times / M7: Quantile-based classification of inter-arrival times |

## Project Overview

This project is a real-time Bitcoin dashboard built in Python with Streamlit.
It connects to public blockchain APIs and displays live cryptographic and blockchain-related metrics from the Bitcoin network.

The dashboard includes:
- Proof of Work monitoring
- Block header verification
- Difficulty adjustment history
- AI-based anomaly detection
- Merkle proof validation
- Security estimation for 51% attacks
- A second AI approach for comparative analysis

## Main API

- Mempool.space API

## Dashboard Framework

- Streamlit

## Module Tracking

Use one of these values: `Not started`, `In progress`, `Done`

| Module | What it should include | Status |
|---|---|---|
| M1 | Proof of Work Monitor | Done |
| M2 | Block Header Analyzer | Done |
| M3 | Difficulty History | Done |
| M4 | AI Component | Done |
| M5 | Merkle Proof Verifier | Done |
| M6 | Security Score | Done |
| M7 | Second AI Approach | Done |

## Current Progress

- Connected the dashboard to the Mempool.space API and successfully retrieved live Bitcoin data.
- Implemented M1 with live PoW metrics and recent block timing analysis.
- Implemented M2 with local block header serialization, double SHA-256, target decoding, and Proof-of-Work verification.
- Implemented M3 with difficulty adjustment periods, historical evolution, and comparison against the 600-second target.
- Implemented M4 and M7 as two different AI-based approaches for analyzing block inter-arrival times.
- Implemented M5 to verify Bitcoin Merkle proofs step by step.
- Implemented M6 to estimate the economic cost of a 51% attack and visualize confirmation-based security.

## Next Step

- Final polish of the dashboard and preparation of the final report PDF.

## Main Problem or Blocker

- No major blocker at the moment. The remaining work is final polishing, reviewing, and documenting the project clearly.

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py

blockchain-dashboard-jsanzrom/
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- app.py
|-- test_api.py
|-- api/
|   |-- __init__.py
|   `-- blockchain_client.py
`-- modules/
    |-- m1_pow_monitor.py
    |-- m2_block_header.py
    |-- m3_difficulty_history.py
    |-- m4_ai_component.py
    |-- m5_merkle_proof.py
    |-- m6_security_score.py
    `-- m7_second_ai.py

<!-- student-repo-auditor:teacher-feedback:start -->
## Teacher Feedback

### Kick-off Review

Review time: 2026-04-29 20:31 CEST
Status: Green

Strength:
- I can see the dashboard structure integrating the checkpoint modules.

Improve now:
- The checkpoint evidence is strong: the dashboard and core modules are visibly progressing.

Next step:
- Keep building on this checkpoint and prepare the final AI integration.
<!-- student-repo-auditor:teacher-feedback:end -->
