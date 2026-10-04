import json, os
import joblib
from .preprocess import tokens
from .train import MODEL, METRICS, train

_pipe = None

def load():
    global _pipe
    if _pipe is None:
        if not os.path.exists(MODEL):
            train()
        _pipe = joblib.load(MODEL)
    return _pipe

def metrics():
    load()
    with open(METRICS) as f:
        return json.load(f)

def classify(subject, message):
    pipe = load()
    text = f"{subject} . {message}"
    proba = pipe.predict_proba([text])[0]
    classes = list(pipe.classes_)
    i = int(proba.argmax())
    vec, clf = pipe.named_steps["tfidf"], pipe.named_steps["clf"]
    X = vec.transform([text]).tocoo()
    names = vec.get_feature_names_out()
    orig = {s: w for w, s in tokens(text)}
    bad = [k for k, c in enumerate(classes) if c != "safe"]
    kws = {}
    for j, v in zip(X.col, X.data):
        if names[j] in ("urltoken", "moneytoken"):
            continue
        k = max(bad, key=lambda k: v * clf.coef_[k][j])
        score = float(v * clf.coef_[k][j])
        if score > 0:
            kws[orig.get(names[j], names[j])] = (score, classes[k])
    top = sorted(kws.items(), key=lambda kv: -kv[1][0])[:8]
    return {"label": classes[i], "confidence": round(float(proba[i]) * 100, 1),
            "probabilities": {c: round(float(p) * 100, 1) for c, p in zip(classes, proba)},
            "keywords": [{"word": w, "signal": s[1], "weight": round(s[0], 3)} for w, s in top]}
