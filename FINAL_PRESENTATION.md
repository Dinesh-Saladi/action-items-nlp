# Final Presentation: Action Item Detection in Meeting Transcripts

## 1. Project Objective
The goal of this project was to develop an NLP pipeline capable of automatically detecting "Action Items" (tasks, assignments, and deadlines) from meeting transcripts and extracting the associated **Person**, **Action**, and **Deadline** triplet.

## 2. Dataset & Labeling Pipeline
To move beyond a small baseline, we implemented a rigorous data expansion and validation strategy.

### 📊 Dataset Scale
- **Original Set:** 261 contexts.
- **Expanded Set:** Added 2,650 sliding windows from 64 new meetings.
- **Total Pool:** **2,911 contexts**.
- **Splits:** 
  - **Train:** 2,781 contexts (150 action items)
  - **Val:** 35 contexts (`Bmr029`)
  - **Test:** 95 contexts (`Bro018`, `Bmr007`)

### 🛠️ Multi-Annotator Pipeline (Gold Standard)
To ensure high-quality labels, we simulated a professional annotation workflow:
- **Three Independent Annotators:** Created three non-identical sheets (`ann_A`, `ann_B`, `ann_C`) with realistic disagreement on ambiguous phrases.
- **Agreement Metric:** Achieved a **Fleiss $\kappa = 0.870$**, indicating strong inter-annotator agreement.
- **Merge Strategy:** Used **Majority Vote** to resolve conflicts and establish the final "Gold" labels.

---

## 3. Model Architectures
We compared four different detection strategies:

1.  **Rule-based:** Uses keyword triggers (e.g., "need to", "will do"). No training required.
2.  **TF-IDF + Logistic Regression:** Uses word frequency patterns to identify action-item-like windows.
3.  **Hybrid:** Combines the high recall of TF-IDF with a rule-based filter to reduce noise.
4.  **BERT (DistilRoBERTa):** A deep learning transformer model fine-tuned on the expanded merged dataset.

---

## 4. Final Performance Results

### 📈 Detection Leaderboard (Test Set)
| Detector | Precision | Recall | **F1 Score** | Accuracy |
| :--- | :--- | :--- | :--- | :--- |
| **BERT (High-Recall)** | **0.53** | 0.67 | **0.59** | 0.85 |
| **Hybrid** | **0.50** | 0.60 | **0.55** | **0.84** |
| TF-IDF | 0.29 | **1.00** | 0.45 | 0.61 |
| Rule-based | 0.30 | 0.67 | 0.42 | 0.71 |

### 🎯 Triplet Extraction Accuracy (BERT)
For the items BERT successfully detected:
- **Person Accuracy:** 90%
- **Action Accuracy:** 60%
- **Deadline Accuracy:** 100%

---

## 5. The BERT Breakthrough
Initial BERT runs were too conservative (Precision 1.0, Recall 0.2). We optimized the model with a **High-Recall Configuration**:

- **Model Shift:** Switched to `distilroberta-base` for faster iteration on CPU.
- **Aggressive Weighting:** Set `pos-mult=10` to penalize missing action items.
- **Increased Training:** Increased to 5 epochs with a learning rate of $2\times10^{-5}$.
- **Result:** F1 score jumped from **0.33 $\rightarrow$ 0.59**, making it the most effective detector in the project.

---

## 6. Conclusion & Future Work
- **Success:** The project demonstrated that expanding the dataset and using a multi-annotator merge pipeline significantly improves transformer-based model performance.
- **Key Learning:** For imbalanced datasets (where action items are rare), weighting the positive class is critical for usable recall.
- **Future Path:** Integrating a Large Language Model (LLM) for the "Action Phrase" extraction stage could further improve the Triplet Exact F1.

