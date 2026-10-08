"""One command: split data -> predict with every detector -> score each -> print comparison.
python run_all.py                       (uses data/annotated.jsonl and the test meetings below)
python run_all.py --test-meetings Bro018 Bmr007
python run_all.py --val-meetings Bmr029  (carve a validation split; threshold/C are chosen on IT,
                                          never on the test gold)
python run_all.py --skip-split           (reuse existing data/train + data/test + data/val)
python run_all.py --with-bert            (fine-tune RoBERTa first, then add it to the table)
"""

import subprocess, sys, argparse, re, glob, os

ap = argparse.ArgumentParser()
ap.add_argument("--annotated", default="data/annotated.jsonl")
ap.add_argument("--test-meetings", nargs="+", default=["Bro018", "Bmr007"])
ap.add_argument("--val-meetings", nargs="+", default=[])
ap.add_argument("--skip-split", action="store_true")
ap.add_argument(
    "--with-bert", action="store_true", help="train the RoBERTa detector first"
)
ap.add_argument("--bert-model", default="roberta-base")
a = ap.parse_args()

# the validation split is used only when this run creates it (--val-meetings) or when the user
# explicitly says to reuse the existing splits; a stale data/val is never used silently.
have_val = bool(a.val_meetings) or (
    a.skip_split and os.path.exists("data/val/gold.jsonl")
)

run = lambda *c, show=False: subprocess.run(
    [sys.executable, *c],
    check=True,
    stdout=None if show else subprocess.DEVNULL,
)

# 1. split FIRST, so train_bert.py (below) can already see the validation files
if not a.skip_split:
    cmd = [
        "make_dataset.py",
        "--annotated",
        a.annotated,
        "--test-meetings",
        *a.test_meetings,
    ]
    if a.val_meetings:
        cmd += ["--val-meetings", *a.val_meetings]
    run(*cmd, show=True)
elif os.path.exists("data/val/gold.jsonl") and not have_val:
    print(
        "note: data/val exists but was not requested this run -> ignoring it "
        "(pass --val-meetings to use it, or --skip-split to reuse the existing splits)"
    )

# 2. train the transformer arm if asked to (or reuse a previously trained model)
if a.with_bert and not os.path.isdir("outputs/bert_model"):
    subprocess.run(
        [sys.executable, "train_bert.py", "--model", a.bert_model]
        + (
            ["--val-input", "data/val/input.jsonl", "--val-gold", "data/val/gold.jsonl"]
            if have_val
            else []
        ),
        check=True,
    )
detectors = ["rule", "tfidf", "hybrid"]
if a.with_bert or os.path.isdir("outputs/bert_model"):
    detectors.append("bert")

# 3. predict + score
os.makedirs("outputs", exist_ok=True)
for d in detectors:
    cmd = [
        "predict.py",
        "--input",
        "data/test/input.jsonl",
        "--out",
        f"outputs/pred_{d}.jsonl",
        "--detector",
        d,
    ]
    if d in ("tfidf", "hybrid"):
        cmd += [
            "--train-input",
            "data/train/input.jsonl",
            "--train-gold",
            "data/train/gold.jsonl",
        ]
        if have_val:
            cmd += [
                "--val-input",
                "data/val/input.jsonl",
                "--val-gold",
                "data/val/gold.jsonl",
            ]
    run(*cmd, show=True)
    run(
        "score.py",
        "--pred",
        f"outputs/pred_{d}.jsonl",
        "--gold",
        "data/test/gold.jsonl",
        "--name",
        d,
    )

# 4. comparison table
print(
    f"\n{'detector':8} | det P    R    F1  | person action deadline | triplet exact F1 | relaxed P    R    F1"
)
for d in detectors:
    path = f"outputs/{d}_report.md"
    if not os.path.exists(path):
        print(f"{d:8} | (no report)")
        continue
    t = open(path).read()
    g = lambda pat: [float(x) for x in re.search(pat, t).groups()]
    P, R, F = (
        float(re.search(rf"\| {k} \| ([\d.]+) \|", t).group(1))
        for k in ("Precision", "Recall", "F1")
    )
    pe, ac, dl = g(
        r"Person \(exact speaker id match\) \| ([\d.]+) \|\n\| Action .*? \| ([\d.]+) \|\n\| Deadline .*? \| ([\d.]+) \|"
    )
    exF = float(
        re.search(r"\| Exact .*? \| [\d.]+ \| [\d.]+ \| ([\d.]+) \|", t).group(1)
    )
    rP, rR, rF = g(r"\| Relaxed .*? \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \|")
    print(
        f"{d:8} | {P:.2f} {R:.2f} {F:.2f} | {pe:.2f}   {ac:.2f}   {dl:.2f}    | {exF:.2f}             | {rP:.2f} {rR:.2f} {rF:.2f}"
    )
print(
    "\nFull reports: outputs/<detector>_report.md   Per-example mistakes: outputs/<detector>_errors.csv"
)
print(
    "Sections 4-5 of each report separate component P/R/F1 and extraction vs cross-turn linking."
)
