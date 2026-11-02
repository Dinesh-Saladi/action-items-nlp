# Project Results Presentation (Updated Nov 2026)

## 🚀 Final Performance Leaderboard
Trained on expanded merged dataset (**2,911 contexts**, 150 train positives).

| Detector | Precision | Recall | **F1 Score** | Accuracy |
| :--- | :--- | :--- | :--- | :--- |
| **BERT (High-Recall)** | 0.53 | 0.67 | **0.59** | 0.85 |
| **Hybrid** | **0.50** | 0.60 | **0.55** | **0.84** |
| TF-IDF | 0.29 | **1.00** | 0.45 | 0.61 |
| Rule-based | 0.30 | 0.67 | 0.42 | 0.71 |

## 🔑 Key Takeaways

- **BERT Breakthrough:** After switching to `distilroberta-base` with a High-Recall config (Positive Mult=10, 5 Epochs), BERT became the top performer with an **F1 of 0.59**.
- **High Precision:** BERT maintains strong precision (0.53) while significantly increasing recall compared to previous runs.
- **Hybrid Stability:** The Hybrid detector remains the most stable baseline with an F1 of 0.55.
- **Perfect Recall:** TF-IDF continues to catch 100% of action items, though it introduces the most noise (false positives).
- **Data Impact:** Expanding the training set to nearly 3,000 contexts and using a multi-annotator merge pipeline provided the necessary signal for the BERT model to generalize.

## 🛠️ Technical Configuration (BERT)
- **Model:** `distilroberta-base` (Faster, 6-layer architecture)
- **Training:** 5 Epochs, Max Length 256
- **Weighting:** Aggressive positive class weighting (10x) to prioritize recall.
- **Validation:** Tuned on `Bmr029`, tested on `Bro018` + `Bmr007`.

Source: `FINAL_RESULTS.md`. Full detail: `outputs/*_report.md`.
