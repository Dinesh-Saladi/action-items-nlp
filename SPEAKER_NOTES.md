# Speaker Notes: Action Item Detection Presentation (Expanded)

## Slide 1: Project Objective
- **Key Point:** Automated action item extraction.
- **Talking Points:**
  - "Good morning/afternoon. My project focuses on solving a common problem in corporate environments: the 'after-meeting void' where action items are discussed but forgotten."
  - "The goal was to build an NLP pipeline that doesn't just find the sentence where a task is mentioned, but extracts a complete triplet: Who is doing it, What is the task, and When is it due."

## Slide 2: The Data Journey: Scaling and Acquisition
- **Key Point:** Moving from a tiny baseline to a professional-grade dataset.
- **Talking Points:**
  - "We started with a very small set of 261 contexts. To make a deep learning model work, we needed more data."
  - "We expanded this to over 2,900 contexts across 64 meetings using a sliding window approach."
  - "We carefully split the data: maximizing training size while locking the validation and test sets to ensure our results are honest and reproducible."

## Slide 3: The Labeling Pipeline: Ensuring Gold Quality
- **Key Point:** Avoiding "garbage in, garbage out."
- **Talking Points:**
  - "Data quantity is nothing without quality. We didn't just trust AI labels."
  - "We implemented a pipeline: AI Bootstrap $\rightarrow$ Three Independent Human Reviewers $\rightarrow$ Majority Vote."
  - "Using Fleiss' Kappa, we measured the agreement at 0.87, which is a very strong score. This means our 'Gold' labels are an accurate reflection of human judgment."

## Slide 4: Model Architectures: The Hierarchy
- **Key Point:** Comparing simple vs. complex approaches.
- **Talking Points:**
  - "We used a tiered approach. Rule-based is our zero-shot baseline—fast but rigid."
  - "TF-IDF looks at word frequency. It's great at finding *something* (high recall) but often flags irrelevant sentences (low precision)."
  - "The Hybrid model combines both: TF-IDF's reach filtered by Rule-based constraints."
  - "Finally, we used BERT (DistilRoBERTa) to capture the actual semantic meaning and intent of the conversation."

## Slide 5: Final Performance Results (Detection)
- **Key Point:** BERT is the winner.
- **Talking Points:**
  - "Looking at the leaderboard, BERT achieved the highest F1 score of 0.59."
  - "What's most impressive is the balance. While TF-IDF has 100% recall, its precision is too low to be useful. BERT provides a high-confidence detection rate while still catching most actual items."

## Slide 6: Final Performance Results (Extraction)
- **Key Point:** Extraction is harder than detection.
- **Talking Points:**
  - "Once we find the sentence, we have to extract the details. We found that Person and Deadline are highly predictable."
  - "However, Action Accuracy is only 60%. This is the 'hard part' of the project because action phrases vary wildly in length and wording across different meetings."

## Slide 7: Ablation Study: The BERT Breakthrough
- **Key Point:** Solving the "Conservative Model" problem.
- **Talking Points:**
  - "BERT didn't start as the winner. Initially, it was too conservative—100% precision but almost no recall."
  - "We realized the model was defaulting to 'No Action Item' to maximize accuracy on an imbalanced dataset."
  - "By implementing a Positive Multiplier of 10, we told the model that missing a task is 10x worse than a false alarm. This pushed the F1 from 0.33 up to 0.59."

## Slide 8: Technical Deep Dive: DistilRoBERTa
- **Key Point:** Efficiency for CPU environments.
- **Talking Points:**
  - "Because we were working on CPU, we chose DistilRoBERTa. It has 6 layers instead of 12."
  - "It's 2x faster to train and run, but retains about 97% of the performance of the larger RoBERTa model."
  - "We also used a max length of 256 tokens, ensuring that we didn't truncate the context of long meeting turns."

## Slide 9: Error Analysis: False Positives
- **Key Point:** Distinguishing suggestion from commitment.
- **Talking Points:**
  - "We analyzed the failures. A common False Positive is the 'Suggestion.' For example: 'We should probably think about the budget.'"
  - "The model sees 'should' and 'budget' and flags it, but it misses the nuance that this is a vague suggestion, not a concrete task assignment."

## Slide 10: Error Analysis: False Negatives
- **Key Point:** The challenge of implicit intent.
- **Talking Points:**
  - "False Negatives often occur with implicit references. For example: 'I'll take care of that.'"
  - "The model knows 'I'll take care of it' is a task, but it doesn't know what 'that' refers to because the object was mentioned several turns earlier. This is a limitation of our current window-based approach."

## Slide 11: Post-Processing & NER
- **Key Point:** Using spaCy as a refinement layer.
- **Talking Points:**
  - "We didn't rely on BERT for everything. We used spaCy for post-processing."
  - "First, we used it for 'Action Trimming' to remove linguistic fluff like 'Um' or 'Actually' from the results."
  - "Second, we used PERSON NER to extract a list of all people mentioned in the context. This provides a verification layer for the assigned owner."

## Slide 12: Conclusion & Future Work
- **Key Point:** Data quality and class imbalance are the main drivers of success.
- **Talking Points:**
  - "The biggest takeaway: data quality beats model size. The multi-annotator pipeline was the foundation for the BERT success."
  - "Moving forward, we could integrate an LLM for the 'Action' phrase extraction to boost that 60% accuracy."
  - "We could also implement a memory buffer to solve the 'Hidden Action Item' problem seen in our error analysis."
