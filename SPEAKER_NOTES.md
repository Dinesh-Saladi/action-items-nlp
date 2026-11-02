# Speaker Notes: Action Item Detection Presentation

## Slide 1: Project Objective
- **Key Point:** Automated action item extraction.
- **Talking Points:**
  - "Good morning/afternoon. My project focuses on solving a common problem in corporate environments: the 'after-meeting void' where action items are discussed but forgotten."
  - "The goal was to build an NLP pipeline that doesn't just find the sentence where a task is mentioned, but extracts a complete triplet: Who is doing it, What is the task, and When is it due."
  - "We aren't just looking for keywords; we are looking for intent and commitment."

## Slide 2: Dataset & Labeling Pipeline
- **Key Point:** Scaling from a tiny baseline to a robust dataset.
- **Talking Points:**
  - "We started with a very small set of 261 contexts. To make a deep learning model work, we needed more data."
  - "We expanded this to over 2,900 contexts across 64 meetings using a sliding window approach."
  - "But more data is useless if the labels are wrong. We implemented a professional labeling pipeline with three independent annotators."
  - "Using Fleiss' Kappa, we measured the agreement at 0.87, which is considered 'strong' agreement. We then used majority voting to create a 'Gold Standard' dataset that we could trust for training."

## Slide 3: Model Architectures
- **Key Point:** Comparing simple vs. complex approaches.
- **Talking Points:**
  - "We didn't just jump to BERT; we established a hierarchy of models."
  - "The **Rule-based** model is our 'zero-effort' baseline—fast but rigid."
  - "**TF-IDF** looks at the statistical uniqueness of words. It's great at finding *something* (high recall) but often flags irrelevant sentences (low precision)."
  - "The **Hybrid** model tries to get the best of both: TF-IDF's reach filtered by Rule-based constraints."
  - "Finally, we used **BERT**, specifically DistilRoBERTa, to capture the actual semantic meaning of the conversation."

## Slide 4: Final Performance Results
- **Key Point:** BERT is the winner.
- **Talking Points:**
  - "Looking at the leaderboard, we see a clear winner. BERT achieved an F1 score of 0.59."
  - "What's most impressive here is the balance. While TF-IDF has 100% recall, its precision is abysmal. BERT provides a high-confidence detection rate while still catching the majority of actual action items."
  - "In terms of extraction, BERT is nearly perfect at identifying the 'Person' and 'Deadline' once it has correctly flagged the sentence as an action item."

## Slide 5: The BERT Breakthrough
- **Key Point:** Overcoming the "Conservative Model" problem.
- **Talking Points:**
  - "It's important to note that BERT didn't start this way. Initially, it was too conservative—it had 100% precision but almost no recall."
  - "To fix this, we applied three specific changes: First, we moved to DistilRoBERTa for faster CPU training. Second, we increased the epochs to 5 to let the model converge better."
  - "Most importantly, we implemented a 'Positive Multiplier' of 10. This essentially tells the model: 'It is 10 times worse to miss a real action item than to accidentally flag a wrong one.' This shift pushed our F1 from 0.33 to 0.59."

## Slide 6: Conclusion & Future Work
- **Key Point:** Data quality and class imbalance are the main drivers of success.
- **Talking Points:**
  - "The biggest takeaway from this project is that data quality beats model size. The multi-annotator pipeline was the foundation for the BERT success."
  - "We also learned that for imbalanced tasks—where only a few sentences in a whole meeting are action items—standard loss functions aren't enough; you must weight the positive class."
  - "Moving forward, I believe integrating an LLM for the final 'Action Phrase' extraction could push the triplet accuracy even higher, as the current model sometimes struggles with the exact wording of the task."
