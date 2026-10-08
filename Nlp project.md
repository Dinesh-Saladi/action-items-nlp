# Hybrid NLP Pipeline for Explicit Action-Item Triplet Extraction from Multi-Turn Meeting Conversations

## 1. Project Title

**Hybrid NLP Pipeline for Explicit Action-Item Triplet Extraction from Multi-Turn Meeting Conversations**

## 2. Introduction and Motivation

Meetings contain important decisions, tasks, responsibilities, and deadlines, but this information is often embedded in informal and multi-turn conversations.

For example:

> **Alice:** We need to update the documentation.  
> **Bob:** I'll take care of it.  
> **Alice:** Okay, have it done by Friday.

A human can infer:

**(Bob, update documentation, Friday)**

but automatically extracting this information requires understanding speaker identity, conversational context, actions, and temporal expressions.

The motivation of this project is to develop a practical NLP system that converts unstructured meeting conversations into **structured action items**, which can support meeting assistants, task-management systems, and automatic meeting summaries.

The project focuses specifically on **explicit or strongly inferable action items**, rather than attempting complete understanding of an entire meeting.

## 3. Problem Statement

Develop a hybrid NLP pipeline that identifies **explicit action-item utterances or short conversational contexts** from multi-party meeting transcripts and extracts structured:

**(Person, Action, Deadline)**

triplets.

The system will combine **rule-based linguistic techniques, traditional machine learning, and transformer-based models**. Since the three components of an action item may occur across nearby conversational turns, the system will use a limited local context window for responsibility and deadline linking.

Highly ambiguous action items, unresolved references, and long-range conversational reasoning will be outside the primary scope.

## 4. Dataset Available

### ICSI Meeting Corpus

The **ICSI Meeting Corpus** will be the primary dataset.

It contains natural, multi-party meeting conversations with speaker and utterance information, making it suitable for studying action-item extraction from realistic dialogue.

ICSI does not directly provide the exact **(Person, Action, Deadline)** annotations required for this project. Therefore, a task-specific annotation layer will be created for a manageable subset of the corpus.

### Proposed Annotation

A manageable subset of approximately **500–1,000 utterances/action-item contexts**, depending on the availability of relevant examples, will be manually annotated.

An action-item context may contain multiple neighboring turns when information about the person, action, or deadline is distributed across turns.

Each selected context will be annotated with:

- Action-item / Non-action
- Responsible person
- Action/task
- Deadline
- Complete **(Person, Action, Deadline)** triplet

The data should be split **by meeting**, rather than randomly by utterance, to reduce the possibility of similar conversational patterns appearing in both training and testing.

## 5. Proposed Methodology

The proposed system follows a modular NLP pipeline that converts multi-party meeting transcripts from the ICSI Meeting Corpus into structured **(Person, Action, Deadline)** triplets. Instead of trying to solve the entire problem with a single model, the task is divided into smaller stages, allowing each component to be developed and evaluated separately.

### Dataset Preparation and Annotation

A manageable subset of ICSI meeting transcripts will be selected for the project. Since the original ICSI annotations do not directly provide the exact **(Person, Action, Deadline)** structure required for this project, a task-specific annotation layer will be created manually.

Each selected utterance or action-item context will be annotated with:

- **Action-item / Non-action**
- **Person** responsible for the task
- **Action** being performed
- **Deadline**, if one is explicitly available

For example:

> **Bob:** We need to update the documentation.  
> **Sarah:** I'll take care of it.  
> **Bob:** Have it ready by Friday.

will be annotated as:

**(Sarah, update the documentation, Friday)**

If there is no identifiable deadline, the value will be recorded as `NULL`.

These annotations will provide the **ground truth** against which the models' predictions can be compared. The annotated data will be divided into training, validation, and test sets, preferably by meeting rather than by individual utterance.

### Preprocessing

The raw ICSI transcripts will be cleaned and normalized before being given to the NLP models. This includes handling transcription artifacts, unnecessary formatting, whitespace, and other noise.

However, important conversational information such as **speaker identity, utterance boundaries, and task-related expressions** will be preserved because they are essential for determining who is responsible for an action.

### Utterance Segmentation

The existing speaker and turn structure provided by ICSI will be used to divide each meeting into individual utterances.

For example:

> **Bob:** We need to update the documentation.  
> **Sarah:** I'll take care of it.  
> **Bob:** Have it ready by Friday.

will be represented as separate speaker turns while maintaining their original order.

This is important because later stages need to understand both **what was said and who said it**.

### Action-Item Detection

The first prediction task is to determine whether an utterance or short conversational context represents an **action item**.

Two approaches will be compared:

- **TF-IDF + Logistic Regression/SVM** as traditional and interpretable baselines
- **BERT/RoBERTa** as transformer-based approaches

For example:

> "I'll prepare the report tomorrow."

→ **Action-item**

while:

> "What do you think about the new interface?"

→ **Non-action**

The manually created annotations will be used as the ground truth for training and evaluating these models.

The comparison will help determine whether contextual transformer models provide an advantage over simpler lexical approaches for informal meeting language.

### Entity and Temporal Extraction

Once an action item is detected, the system needs to identify the pieces required to construct the final triplet.

**Person** will primarily be determined from the **speaker information provided by ICSI**. SpaCy NER can additionally be used to identify explicitly mentioned person names when the responsible person is stated within the dialogue.

**Action** will be extracted as the task or activity being performed using linguistic information such as POS tags and dependency relationships.

**Temporal expressions** such as *Friday*, *tomorrow*, *next week*, or *by Monday* will be identified using pretrained NER and rule-based patterns.

For example:

> "Sarah will prepare the report by Friday."

will produce:

**Person → Sarah**

**Action → prepare the report**

**Time → Friday**

At this stage, **Friday is only a temporal candidate**. The system still has to determine whether it is actually the deadline for the action.

### Responsibility Linking

This stage determines **who is responsible for which action**.

This becomes important when the person and action are distributed across multiple turns.

For example:

> **Bob:** Someone needs to update the documentation.  
> **Sarah:** I'll take care of it.

The system needs to infer:

**Sarah → responsible for → update documentation**

To keep the problem achievable, the system will only consider a limited local context, such as **3–5 neighboring turns**, rather than attempting to understand the entire meeting.

Rules and a lightweight classifier can use information such as:

- speaker identity
- pronouns such as *I*, *you*, and *it*
- commitment expressions such as *I'll*, *I can*, and *I'll handle it*
- dependency relationships
- distance between the action and the person's utterance

### Deadline Linking

This stage determines whether a temporal expression is actually a **deadline** and connects it to the appropriate action.

For example:

> "I'll prepare the report by Friday."

should produce:

**prepare the report → deadline → Friday**

This distinction is important because simply identifying `Friday` as a DATE does not mean that Friday is a deadline.

For example:

> "Our next meeting is on Friday."

contains a date but does not necessarily specify a task deadline.

Only deadlines that can be reasonably resolved within the defined local context will be considered. If an action has no identifiable deadline, the system will output `NULL`.

### Structured Action-Item Generation

After responsibility and deadline linking, the extracted information will be combined into the final structured representation:

**(Person, Action, Deadline)**

For example:

**(Sarah, update the documentation, Friday)**

or, when no deadline is available:

**(Sarah, update the documentation, NULL)**

This structured representation is the final output of the pipeline and can potentially be used by task-management or meeting-assistant applications.

### Evaluation

Each component will be evaluated separately using **Precision, Recall, and F1-score**.

The main evaluation tasks will be:

- **Action-item detection**
- **Person extraction**
- **Action extraction**
- **Deadline extraction**
- **Responsibility linking**
- **Deadline linking**

Finally, the complete pipeline will be evaluated using **exact triplet Precision, Recall, and F1-score**.

For example, if the ground truth is:

**(Sarah, update documentation, Friday)**

then a prediction of:

**(Sarah, update documentation, Friday)**

is completely correct.

But:

**(Sarah, update documentation, Monday)**

is considered incorrect because the complete triplet does not match.

The component-level metrics will show where individual stages succeed or fail, while the exact triplet metric will show how effectively the complete pipeline converts realistic multi-turn meeting conversations into **correct, structured action items**.
# Entire project is basically this

                 ICSI meetings

                      │

                      ▼

             Select some meetings

                      │

             ┌────────┴─────────┐

             │                  │

             ▼                  ▼

       YOU ANNOTATE        MODEL INPUT

       the correct             │

       answers                 │

             │                 ▼

             │              BERT/ML

             │                 │

             │                 ▼

             │             Prediction

             │                 │

             └────────┬────────┘

                      ▼

                  COMPARE

                      │

                      ▼

             How accurate is it?


Use only these ICSI layers:

1. **Transcript / utterance text** — your main input.
2. **Speaker information** — to identify the person responsible for an action.
3. **Dialogue-act annotations** — optionally as supporting information/features for action-item detection, **not as your ground truth**.
4. **Your own task-specific annotation layer** — `(Action-item, Person, Action, Deadline)` for training/evaluation.

You **do not need** the topic, summarization, or other annotation layers for the main pipeline.

So the core is:

**ICSI Transcript + Speaker Info → Your Annotation → NLP Pipeline → (Person, Action, Deadline)**.

