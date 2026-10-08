"""Gold labels written by Claude after reading each candidate window (REVIEW THESE: they are one annotator's judgement).
id -> (person, action, deadline). Every candidate NOT listed here is labeled 'not an action item'.
person = ICSI speaker id of whoever takes/gets the task (NULL if nobody/everyone); deadline = time expression or NULL.
"""

N = "NULL"
LABELS = {
    # ---- Bed010
    "Bed010_t51": ("me010", "walk you through it", N),
    "Bed010_t69": (N, "get the demos they need", N),
    "Bed010_t109": ("mn015", "show an internal demo", N),
    "Bed010_t113": ("mn015", "walk through the information", N),
    "Bed010_t171": ("me003", "go back and look at the ones on the list", N),
    "Bed010_t183": ("mn015", "send a pointer to a Java applet", N),
    "Bed010_t187": ("mn015", "give the input in terms of the internal structure", N),
    "Bed010_t229": ("mn015", "send the transcribed English and German data", N),
    "Bed010_t316": ("mn015", "send that link", N),
    "Bed010_t332": ("me010", "dig up this reference", N),
    "Bed010_t336": ("me010", "do this test on you guys", N),
    "Bed010_t478": ("mn036", "send you email", N),
    "Bed010_t522": ("me010", "make a note to do that", N),
    # ---- Bed017
    "Bed017_t218": ("mn059", "go to the Semantic Web Workshop", "in two weeks"),
    "Bed017_t230": ("mn015", "take you to his office", N),
    "Bed017_t259": (
        "mn015",
        "write up the stuff we discussed at our daily meetings",
        N,
    ),
    "Bed017_t263": ("mn015", "revise the original construal proposal", N),
    # ---- Bmr029
    "Bmr029_t45": ("mn017", "look up the size of the small training set", N),
    "Bmr029_t174": ("mn017", "get started on the one that already has a cross", N),
    "Bmr029_t247": ("mn017", "ask Don which is easier to process", N),
    "Bmr029_t274": ("mn017", "talk to Don", N),
    "Bmr029_t278": ("me018", "give you those files to process", N),
    "Bmr029_t287": ("me018", "ask David about the disks", N),
    "Bmr029_t300": ("me018", "check with David about that", N),
    "Bmr029_t310": ("mn017", "give you a list of the short version", N),
    "Bmr029_t330": ("me026", "get that subset processed", N),
    "Bmr029_t376": ("me026", "give me a list of the files that you throw out", N),
    "Bmr029_t391": ("me026", "have the information for the rest", "tomorrow"),
    # ---- Bro018
    "Bro018_t112": ("fn002", "try adding together the probabilities", N),
    "Bro018_t120": ("fn002", "add up the probabilities", N),
    "Bro018_t151": ("fn002", "study the France Telecom proposal", N),
    "Bro018_t178": ("fn002", "try moving this parameter in their code", N),
    # ---- Bmr007
    "Bmr007_t12": (N, "sign the consent form", N),
    "Bmr007_t34": ("me013", "go through that list", N),
    "Bmr007_t38": ("me013", "chat about that off-line", N),
    "Bmr007_t143": ("mn005", "average the duration of the overlaps", N),
    "Bmr007_t471": ("me011", "put the seat number on the next set of forms", N),
    "Bmr007_t490": (
        "me011",
        "put little labels with the seat number on all the chairs",
        N,
    ),
    "Bmr007_t743": (N, "work on the human subjects form", N),
    "Bmr007_t761": (
        "me011",
        "send you a sentence that doesn't just say a bunch of stuff",
        N,
    ),
    "Bmr007_t767": ("me011", "phrase it in passive voice", N),
    "Bmr007_t845": (N, "send me thoughts for an agenda", N),
    "Bmr007_t879": ("fe008", "take a look at the backchannels", N),
    # ---- Bns002
    "Bns002_t7": ("mn040", "give a very short introduction", N),
    "Bns002_t15": (
        "mn082",
        "give you all a few slides concerning the project proposal",
        N,
    ),
    "Bns002_t387": ("mn021", "provide you some of the proposals", N),
}
