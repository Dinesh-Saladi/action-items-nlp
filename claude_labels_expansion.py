"""Provisional labels written by Claude after reading each 330-window expansion candidate.

REVIEW THESE: they are one annotator's judgement, not independent human annotation.

id -> (person, action, deadline). Every expansion candidate NOT listed here is labeled
"not an action item". person = ICSI speaker id of whoever takes/gets the task (NULL if
nobody/everyone); deadline = time expression or NULL.

These labels are the AI pre-annotation/bootstrap copied into data/ann_A.jsonl,
ann_B.jsonl and ann_C.jsonl; the three sheets are NOT independent annotations, so
kappa across them is 1.0 by construction (see data/ANNOTATION_PROVENANCE.md).
"""

N = "NULL"

LABELS = {
    # ---- Bdb001
    "Bdb001_n418": ("me011", "look at the ATLAS format and let us know what you think", "NULL"),
    "Bdb001_t222": ("me011", "take a closer look at the ATLAS format", "NULL"),
    "Bdb001_t326": ("me011", "look at the ATLAS format again", "NULL"),
    "Bdb001_t424": ("me011", "look at the ATLAS format", "NULL"),
    "Bdb001_t433": ("NULL", "look at the ATLAS format", "NULL"),
    "Bdb001_t488": ("me011", "look at the ATLAS format again", "NULL"),
    "Bdb001_t622": ("fe016", "read the digits", "NULL"),
    # ---- Bed003
    "Bed003_t130": ("me003", "switch to the JavaBayes program and talk about the belief net", "NULL"),
    "Bed003_t17": ("fe016", "come back up and check if you're still meeting", "in about an hour"),
    "Bed003_t256": ("me003", "set a few nodes and find their probabilities", "NULL"),
    "Bed003_t405": ("me003", "add a 'has door' property", "NULL"),
    "Bed003_t51": ("me003", "maximize the window", "NULL"),
    "Bed003_t56": ("me003", "maximize the window", "NULL"),
    "Bed003_t574": ("me003", "put the net up again", "NULL"),
    "Bed003_t6": ("NULL", "put your name on the sign-in sheet", "NULL"),
    "Bed003_t63": ("me003", "get rid of the 'Click to add notes' box", "NULL"),
    "Bed003_t761": ("NULL", "have a trial run with Fey", "Friday afternoon"),
    # ---- Bed016
    "Bed016_t131": ("mn015", "show the draft talk and get input on it", "NULL"),
    "Bed016_t184": ("mn015", "present a talk at EML", "NULL"),
    "Bed016_t259": ("fe004", "email the updated slides", "NULL"),
    "Bed016_t312": ("fe004", "give comments on the presentation separately", "NULL"),
    "Bed016_t321": ("mn015", "add the scalability point about constructions and construal to the proposal", "NULL"),
    # ---- Bmr010
    "Bmr010_t16": ("fe008", "give an update on the transcription effort and raise the microphone cleanliness issue", "NULL"),
    "Bmr010_t205": ("me013", "ping them about the format", "NULL"),
    "Bmr010_t273": ("me011", "contact Brian", "NULL"),
    "Bmr010_t327": ("me011", "dig through the DragonDictate documentation to find the form", "NULL"),
    "Bmr010_t465": ("mn017", "hand over the digit form", "NULL"),
    # ---- Bmr026
    "Bmr026_t321": ("me013", "put together a list of what we've done for the annual report", "NULL"),
    "Bmr026_t331": ("me013", "put together a list of what we've done", "NULL"),
    "Bmr026_t335": ("me013", "have the discussion with Mari about what we've done", "the next day"),
    "Bmr026_t460": ("me018", "convert the alignments into label files and train a new net", "NULL"),
    "Bmr026_t51": ("mn017", "ask Jane about her people transcribing the SmartKom data", "NULL"),
    "Bmr026_t57": ("me018", "mail the web page status out to the list", "NULL"),
    "Bmr026_t589": ("me013", "think about the net size (2000 vs 4000 hidden units)", "NULL"),
    "Bmr026_t61": ("me011", "add his meeting status information to the web page", "NULL"),
    "Bmr026_t610": ("me018", "start off with two thousand hidden units", "NULL"),
    "Bmr026_t65": ("me011", "send the transcripts to the participants and bleep them out", "NULL"),
    "Bmr026_t79": ("me011", "work on the back-end with Don", "NULL"),
    # ---- Bns003
    "Bns003_n104": ("mn021", "read through the web page text and check it", "NULL"),
    "Bns003_t134": ("mn021", "look at the web page and give feedback", "NULL"),
    "Bns003_t17": ("mn082", "set up the second PC in his spare time", "NULL"),
    "Bns003_t36": ("mn021", "build and set up a computer (with FreeBSD)", "NULL"),
    "Bns003_t396": ("mn082", "write on the proposal and distribute a list of interested people", "NULL"),
    "Bns003_t5": ("mn082", "call Adam when ready", "in about one hour"),
    "Bns003_t75": ("mn081", "write about his Multicast project on the web page", "NULL"),
    "Bns003_t9": ("mn035", "close the door", "NULL"),
    # ---- Bro010
    "Bro010_n52": ("mn007", "add a low-pass filter at 25 Hz", "NULL"),
    "Bro010_t32": ("mn007", "talk with Sunil about what they're doing", "NULL"),
    "Bro010_t36": ("mn007", "send Sunil an email about what they are doing", "NULL"),
    # ---- Bro024
    "Bro024_t164": ("me006", "do dry runs for the qualifier talk", "NULL"),
    "Bro024_t24": ("me026", "make the plots and put them on his web page", "NULL"),
    "Bro024_t59": ("me026", "look at the choice of the analysis window length", "NULL"),
    "Bro024_t721": ("mn052", "try the clean LDA filter", "NULL"),
    "Bro024_t803": ("NULL", "leave the mike on top of the digit form", "NULL"),
}
