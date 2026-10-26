"""Provisional labels written by Claude after reading each candidate in the expansion batches.

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
    # ---- Bed002
    "Bed002_t19": ("me011", "read the digit strings first", "NULL"),
    "Bed002_t234": ("me010", "go back to the previous slide", "NULL"),
    "Bed002_t443": ("mn015", "show the state of the system", "next Monday"),
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
    # ---- Bed004
    "Bed004_t138": ("mn015", "ask Lila about how to put Fey on the payroll", "NULL"),
    "Bed004_t324": ("mn015", "come up with code for a 'cognitive dispatcher' module", "NULL"),
    "Bed004_t9": ("me012", "hit the black square when done (don't hit record)", "NULL"),
    # ---- Bed005
    "Bed005_n441": ("me010", "ask Bhaskara how much of this JavaBayes supports", "NULL"),
    "Bed005_t17": ("NULL", "check out social infrastructures for possible subjects", "NULL"),
    "Bed005_t22": ("mn015", "make a first draft of the write-up note and send it", "NULL"),
    "Bed005_t318": ("me010", "come up with a general story about construction grammar", "NULL"),
    "Bed005_t374": ("mn015", "get a first draft of that (with Johno)", "NULL"),
    "Bed005_t384": ("me010", "dig up some more stuff from Dekai", "NULL"),
    "Bed005_t435": ("me012", "take a look at it (the paper)", "NULL"),
    "Bed005_t499": ("NULL", "write up a flat file", "NULL"),
    "Bed005_t523": ("mn015", "show examples from the ontology", "next Monday"),
    "Bed005_t577": ("mn015", "think through getting EVA vectors dynamically out of ontologies", "NULL"),
    "Bed005_t66": ("mn015", "show the templates", "NULL"),
    # ---- Bed006
    "Bed006_n737": ("me003", "get the binding point with a nice example", "NULL"),
    "Bed006_t104": ("fe046", "send it", "NULL"),
    "Bed006_t114": ("NULL", "tell interested people to write a mail to mn015 or Jerry", "NULL"),
    "Bed006_t139": ("mn015", "scrape together [the plan]", "NULL"),
    # ---- Bed008
    "Bed008_t213": ("mn015", "move those up about halfway", "NULL"),
    "Bed008_t293": ("mn015", "copy it somewhere else", "NULL"),
    "Bed008_t764": ("me003", "bring up the function thing", "NULL"),
    # ---- Bed009
    "Bed009_t193": ("mn048", "put a message into the right place to ask that question", "NULL"),
    "Bed009_t203": ("mn015", "talk to Michael", "NULL"),
    "Bed009_t241": ("mn048", "go check (about changing the word)", "NULL"),
    "Bed009_t34": ("NULL", "look over Tilman's shoulder while he changes the grammars to English", "NULL"),
    # ---- Bed011
    "Bed011_t0": ("fe046", "give me the remote", "NULL"),
    "Bed011_t129": ("me045", "start diving into the data", "NULL"),
    "Bed011_t146": ("fe046", "schedule ten people", "NULL"),
    "Bed011_t153": ("fe046", "pick out some stuff (not transcribe all)", "NULL"),
    "Bed011_t160": ("fe046", "make notes pointing to interesting things", "NULL"),
    "Bed011_t466": ("mn015", "tell you the German tourist data", "NULL"),
    "Bed011_t481": ("mn015", "try to expand the ontology node", "NULL"),
    # ---- Bed012
    "Bed012_n328": ("NULL", "do this the upcoming days", "NULL"),
    "Bed012_t323": ("mn015", "worry about the ontology interface", "NULL"),
    "Bed012_t358": ("mn015", "get it in here", "NULL"),
    "Bed012_t405": ("mn015", "send an email with a time suggestion", "NULL"),
    "Bed012_t59": ("me003", "do this in Perl", "NULL"),
    # ---- Bed013
    "Bed013_t126": ("mn015", "ask Eva about the EBayes", "NULL"),
    "Bed013_t149": ("me003", "work on the SmartKom stuff and help with that tomorrow", "NULL"),
    "Bed013_t288": ("NULL", "look at the web page", "NULL"),
    "Bed013_t385": ("NULL", "sketch out the details", "NULL"),
    "Bed013_t675": ("me045", "look more into that data", "NULL"),
    # ---- Bed014
    "Bed014_t596": ("mn015", "write it up", "NULL"),
    "Bed014_t90": ("NULL", "send me the note", "NULL"),
    # ---- Bed015
    "Bed015_t18": ("fe004", "start on number two on the notation", "NULL"),
    "Bed015_t694": ("me010", "make a proposal on how to proceed", "NULL"),
    # ---- Bed016
    "Bed016_t131": ("mn015", "show the draft talk and get input on it", "NULL"),
    "Bed016_t184": ("mn015", "present a talk at EML", "NULL"),
    "Bed016_t259": ("fe004", "email the updated slides", "NULL"),
    "Bed016_t312": ("fe004", "give comments on the presentation separately", "NULL"),
    "Bed016_t321": ("mn015", "add the scalability point about constructions and construal to the proposal", "NULL"),
    # ---- Bmr001
    "Bmr001_t301": ("me011", "send mail to speech local", "NULL"),
    # ---- Bmr002
    "Bmr002_t222": ("fe008", "provide word-level transcripts", "NULL"),
    "Bmr002_t645": ("me011", "check it and try to download it", "NULL"),
    "Bmr002_t858": ("me011", "go download 'Transcriber' and look at it", "NULL"),
    "Bmr002_t868": ("me011", "try to get those as well", "NULL"),
    # ---- Bmr003
    "Bmr003_t1080": ("me011", "put it together", "NULL"),
    "Bmr003_t1219": ("me028", "build a cabinet", "NULL"),
    "Bmr003_t1415": ("me011", "remember to bring M_ and M_'s next time", "NULL"),
    "Bmr003_t470": ("NULL", "get it so that it detects volume and inserts a marker", "NULL"),
    "Bmr003_t498": ("fe008", "do that tomorrow", "NULL"),
    "Bmr003_t851": ("me011", "rewrite the mix tool", "NULL"),
    # ---- Bmr005
    "Bmr005_t186": ("mn005", "label the different acoustic", "NULL"),
    "Bmr005_t7": ("me011", "collect the digit forms and write it down", "NULL"),
    # ---- Bmr006
    "Bmr006_t1099": ("fe008", "give you the short version", "NULL"),
    "Bmr006_t1128": ("fe008", "report on next time", "NULL"),
    "Bmr006_t1157": ("me013", "make a brief comment about what we're covering", "NULL"),
    "Bmr006_t162": ("fe016", "go up there and record the meeting", "NULL"),
    "Bmr006_t383": ("me011", "archive it and delete the files", "NULL"),
    "Bmr006_t682": ("mn005", "include the differential derivatives", "NULL"),
    "Bmr006_t687": ("me013", "take just a few features", "NULL"),
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
