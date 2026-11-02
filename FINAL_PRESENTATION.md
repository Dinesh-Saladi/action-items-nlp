# Final Presentation: Action Item Detection in Meeting Transcripts

## 1. Project Objective
The goal of this project was to develop an NLP pipeline capable of automatically detecting "Action Items" (tasks, assignments, and deadlines) from meeting transcripts and extracting the associated **Person**, **Action**, and **Deadline** triplet.

## 2. The Data Journey: Scaling and Acquisition
We moved from a tiny baseline to a professional-grade dataset.
- **Baseline:** Started with only 261 contexts.
- **Expansion:** Added 2,650 sliding windows from 64 new meetings.
- **Total Pool:** **2,911 contexts**.
- **Split Strategy:** 
  - **Train:** 2,781 contexts (to maximize model learning).
  - **Val:** 35 contexts (`Bmr029` - for threshold tuning).
  - **Test:** 95 contexts (`Bro018`, `Bmr007` - locked for final evaluation).

## 3. The Labeling Pipeline: Ensuring Gold Quality
To avoid the "garbage in, garbage out" problem, we implemented a rigorous multi-stage labeling process.
- **AI Bootstrap:** Initial labels generated via LLM for rapid expansion.
- **Human-in-the-Loop:** Three independent annotators reviewed the AI labels.
- **Agreement Measurement:** Calculated **Fleiss $\kappa$ (0.870)** to prove strong inter-annotator agreement.
- **Conflict Resolution:** Used **Majority Vote** to resolve disagreements, creating a "Gold Standard" dataset.

## 4. Model Architectures: The Hierarchy
We compared four distinct approaches to identify the optimal balance of speed and accuracy:
- **Rule-based:** Zero-shot, keyword-driven (e.g., "need to", "will do"). High speed, low flexibility.
- **TF-IDF + LR:** Statistical pattern matching using Logistic Regression. Extreme recall, low precision.
- **Hybrid:** A tiered filter combining TF-IDF's reach with Rule-based constraints.
- **BERT (DistilRoBERTa):** Contextual embeddings for deep semantic understanding of intent.

## 5. Final Performance Results (Detection)
### 📈 Detection Leaderboard (Test Set)
| Detector | Precision | Recall | **F1 Score** | Accuracy |
| :--- | :--- | :--- | :--- | :--- |
| **BERT (High-Recall)** | **0.53** | 0.67 | **0.59** | 0.85 |
| **Hybrid** | **0.50** | 0.60 | **0.55** | 0.84 |
| TF-IDF | 0.29 | **1.00** | 0.45 | 0.61 |
| Rule-based | 0.30 | 0.67 | 0.42 | 0.71 |

## 6. Final Performance Results (Extraction)
Beyond just detecting the sentence, we evaluate the quality of the extracted triplet.
### 🎯 Triplet Accuracy (BERT)
- **Person Accuracy:** 90% (Strongest component).
- **Action Accuracy:** 60% (Most challenging component).
- **Deadline Accuracy:** 100% (Highly predictable patterns).

**Key Insight:** The "Action" phrase is the hardest to extract because it varies significantly in length and wording.

## 7. Ablation Study: The BERT Breakthrough
We analyzed why the first BERT run failed and how we fixed it.

| Version | Config | Precision | Recall | F1 | Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **V1 (Base)** | Standard Loss | 1.00 | 0.20 | 0.33 | Too Conservative |
| **V2 (Optimized)** | `pos-mult=10`, 5 Epochs | 0.53 | 0.67 | **0.59** | **Optimal Balance** |

**Insight:** In imbalanced datasets, the model defaults to "No Action Item" to maximize accuracy. Aggressive positive weighting is required to force the model to find the rare positives.

## 8. Technical Deep Dive: DistilRoBERTa
Why we chose this specific architecture for the final model:
- **Architecture:** 6-layer transformer (vs 12 in RoBERTa-base).
- **Efficiency:** ~2x faster training and inference, critical for CPU-only environments.
- **Performance:** Retains ~97% of the performance of the larger model.
- **Configuration:** Max length 256 tokens to prevent truncation of long meeting turns.

## 9. Error Analysis: False Positives
Understanding "The Almost Action Items."
- **The Problem:** Model flags sentences that sound like tasks but are actually suggestions.
- **Example:** *"We should probably think about the budget next month."*
- **Why it fails:** The model detects "should" and "budget" as triggers, but fails to recognize the lack of a concrete commitment.

## 10. Error Analysis: False Negatives
Understanding "The Hidden Action Items."
- **The Problem:** Model misses items where the intent is implicit.
- **Example:** *"I'll take care of that."*
- **Why it fails:** The "action" (what is being taken care of) is mentioned 3 turns ago. The model lacks long-term cross-turn memory.

## 11. Post-Processing & NER
We used a hybrid pipeline for the final output.
- **spaCy Integration:** Used `en_core_web_sm` for two roles:
  1. **Action Trimming:** Removing linguistic "fluff" from the extracted phrase.
  2. **PERSON NER:** Extracting all mentioned people in the context to verify the assigned owner.
- **Impact:** Increased the cleanliness of the final output and provided a verification layer for the Person field.

## 12. Conclusion & Future Work
- **Key Win:** Proved that a high-quality merged dataset + weighted loss can make BERT the top performer.
- **Architecture:** DistilRoBERTa provided the best efficiency-to-accuracy ratio.
- **Future Path:** 
  - **LLM Integration:** Use GPT-4 or Llama-3 for the "Action Phrase" extraction to boost the 60% accuracy.
  - **Contextual Memory:** Implementing a memory buffer to solve the "Hidden Action Item" problem.
