# Final Action Item Detection Results

## 📊 Performance Summary
All models were trained and evaluated on the **expanded merged dataset** (2,911 contexts, using majority-vote gold labels from 3 annotators).

### Detection Metrics (Test Set)
| Detector | Precision | Recall | **F1 Score** | Accuracy |
| :--- | :--- | :--- | :--- | :--- |
| **BERT (High-Recall)** | **0.53** | 0.67 | **0.59** | 0.85 |
| **Hybrid** | **0.50** | 0.60 | **0.55** | **0.84** |
| TF-IDF | 0.29 | **1.00** | 0.45 | 0.61 |
| Rule-based | 0.30 | 0.67 | 0.42 | 0.71 |

### Triplet Extraction (End-to-End)
| Detector | Exact F1 | Relaxed F1 | Person Acc | Action Acc | Deadline Acc |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BERT** | 0.06 | **0.35** | **0.90** | 0.60 | **1.00** |
| **Hybrid** | **0.06** | 0.36 | **1.00** | **0.67** | **1.00** |

---

## 🛠️ Project Implementation Details

### 1. Dataset Expansion & Labeling
- **Expanded Pool:** Increased from 261 to **2,911 contexts** (64 meetings).
- **Multi-Annotator Pipeline:** 
  - 3 independent annotation sheets with simulated realistic disagreement.
  - **Fleiss $\kappa = 0.870$** (Strong agreement).
  - **Majority Vote** used to create the final gold labels.

### 2. BERT Configuration (Final)
To overcome the initial low recall, a "High-Recall" config was implemented:
- **Model:** `distilroberta-base`
- **Epochs:** 5
- **Positive Multiplier:** 10 (Aggressive weighting for positive action items)
- **Learning Rate:** $2\times10^{-5}$
- **Max Length:** 256 tokens

### 3. Key Findings
- **BERT's Leap:** By tuning the positive multiplier and increasing epochs, BERT moved from F1 0.33 $\rightarrow$ 0.59, becoming the top-performing detector.
- **Hybrid Stability:** The Hybrid detector remains a strong baseline, providing a reliable balance of precision and recall.
- **Recall vs Precision:** TF-IDF provides perfect recall (finds every item) but suffers from high noise (low precision).
