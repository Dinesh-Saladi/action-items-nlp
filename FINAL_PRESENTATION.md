# Final Presentation: Action Item Detection in Meeting Transcripts

## 1. Project Objective
The goal of this project was to develop an NLP pipeline capable of automatically detecting "Action Items" (tasks, assignments, and deadlines) from meeting transcripts and extracting the associated **Person**, **Action**, and **Deadline** triplet.

## 2. The Data Journey (Expansion & Quality)
We moved from a tiny baseline to a professional-grade dataset.
- **Scale Up:** Expanded from 261 to **2,911 contexts** using sliding windows across 64 meetings.
- **The Labeling Pipeline:**
  - **Bootstrap:** Initial labels generated via AI.
  - **Human-in-the-loop:** Three independent annotators reviewed the data.
  - **Disagreement Handling:** Used **Fleiss $\kappa$ (0.870)** to measure agreement.
  - **Gold Standard:** Final labels were determined by **Majority Vote**, removing individual annotator bias.

## 3. Model Architectures
We compared four distinct approaches to identify the optimal balance of speed and accuracy:
- **Rule-based:** Zero-shot, keyword-driven. High speed, low flexibility.
- **TF-IDF + LR:** Statistical pattern matching. Extreme recall, low precision.
- **Hybrid:** A tiered filter combining the above. Stable, reliable baseline.
- **BERT (DistilRoBERTa):** Contextual embeddings. Deep semantic understanding.

## 4. Final Performance Results
### 📈 Detection Leaderboard (Test Set)
| Detector | Precision | Recall | **F1 Score** | Accuracy |
| :--- | :--- | :--- | :--- | :--- |
| **BERT (High-Recall)** | **0.53** | 0.67 | **0.59** | 0.85 |
| **Hybrid** | **0.50** | 0.60 | **0.55** | 0.84 |
| TF-IDF | 0.29 | **1.00** | 0.45 | 0.61 |
| Rule-based | 0.30 | 0.67 | 0.42 | 0.71 |

### 🎯 Triplet Extraction (BERT)
- **Person:** 90% Accuracy
- **Action:** 60% Accuracy
- **Deadline:** 100% Accuracy

## 5. Ablation Study: The BERT Breakthrough
We analyzed why the first BERT run failed and how we fixed it.

| Version | Config | Precision | Recall | F1 | Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **V1 (Base)** | Standard Loss | 1.00 | 0.20 | 0.33 | Too Conservative |
| **V2 (Optimized)** | `pos-mult=10`, 5 Epochs | 0.53 | 0.67 | **0.59** | **Optimal Balance** |

**Insight:** In imbalanced datasets, the model defaults to "No Action Item" to maximize accuracy. Aggressive positive weighting is required to force the model to find the rare positives.

## 6. Error Analysis (Learning from Mistakes)
Understanding where the model fails is key to future improvement.

- **False Positives (The "Almost" Action Items):** 
  - *Example:* "We should probably think about the budget next month."
  - *Issue:* The model detects "should" and "budget" but misses that it's a suggestion, not a commitment.
- **False Negatives (The "Hidden" Action Items):**
  - *Example:* "I'll take care of that." (Reference to a task mentioned 3 turns ago).
  - *Issue:* The model lacks long-term memory across the entire meeting.

## 7. Conclusion & Future Work
- **Key Win:** Proved that a high-quality merged dataset + weighted loss can make BERT the top performer.
- **Architecture:** DistilRoBERTa provided the best efficiency-to-accuracy ratio for CPU environments.
- **Future Path:** Moving toward **LLM-based extraction** for the "Action" phrase to improve the 60% accuracy in that field.
