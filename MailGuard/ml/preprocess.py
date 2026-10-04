"""Text cleaning for the classifier: lowercase, replace URLs/money, tokenize, remove stop words (NLTK), stem (NLTK)."""
import re
from nltk.stem import PorterStemmer

URL_RE = re.compile(r"(?:https?://|www\.)[^\s<>\"')]+", re.I)
_stem = PorterStemmer().stem

def _load_stopwords():
    try:
        from nltk.corpus import stopwords
        return set(stopwords.words("english"))
    except Exception:
        try:
            import nltk
            if nltk.download("stopwords", quiet=True):
                from nltk.corpus import stopwords
                return set(stopwords.words("english"))
        except Exception:
            pass
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS  # offline fallback
    return set(ENGLISH_STOP_WORDS)

STOP = _load_stopwords()

def tokens(text):
    """Return [(original_word, stem)] after cleaning."""
    t = URL_RE.sub(" urltoken ", text.lower())
    t = re.sub(r"[$€£₹]|\b\d+\s?%", " moneytoken ", t)
    return [(w, _stem(w)) for w in re.findall(r"[a-z]{2,}", t) if w not in STOP]

def analyzer(text):
    return [s for _, s in tokens(text)]
