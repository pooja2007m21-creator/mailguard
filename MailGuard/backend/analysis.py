import re
from urllib.parse import urlparse
from ml.preprocess import URL_RE
from ml import predict

SHORT = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly", "rebrand.ly", "cutt.ly"}
BRANDS = ["paypal", "amazon", "microsoft", "apple", "google", "netflix", "facebook", "instagram", "dhl", "fedex"]
ODD_TLD = (".xyz", ".top", ".click", ".buzz", ".tk", ".gq", ".work", ".loan", ".zip")

def check_links(text):
    out = []
    for u in dict.fromkeys(URL_RE.findall(text)):
        u = u.rstrip(".,;:!?)")
        p = urlparse(u if "://" in u else "http://" + u)
        host, why = (p.hostname or "").lower(), []
        if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host): why.append("Uses an IP address instead of a domain name")
        if host in SHORT: why.append("URL shortener hides the real destination")
        if "@" in p.netloc: why.append("Contains '@', which can disguise the real host")
        if p.scheme == "http": why.append("Not encrypted (HTTP)")
        if host.startswith("xn--") or ".xn--" in host: why.append("Punycode domain (possible look-alike characters)")
        if host.count(".") >= 4: why.append("Unusually many subdomains")
        if host.endswith(ODD_TLD): why.append("Top-level domain often abused")
        if host.count("-") >= 2: why.append("Many hyphens in the domain")
        b = [x for x in BRANDS if x in host]
        if b and not any(host == x + ".com" or host.endswith("." + x + ".com") for x in b):
            why.append(f"Mentions '{b[0]}' but may not be the official domain")
        out.append({"url": u, "suspicious": bool(why), "reasons": why})
    return out

def stats(text):
    words = re.findall(r"\S+", text)
    letters = [c for c in text if c.isalpha()]
    return {"words": len(words), "characters": len(text),
            "sentences": len([s for s in re.split(r"[.!?]+", text) if s.strip()]),
            "links": len(URL_RE.findall(text)), "exclamation_marks": text.count("!"),
            "uppercase_percent": round(100 * sum(c.isupper() for c in letters) / len(letters)) if letters else 0}

def run(subject, message):
    res = predict.classify(subject, message)
    res["links"] = check_links(subject + " " + message)
    res["stats"] = stats(subject + " " + message)
    res["low_confidence"] = res["confidence"] < 60
    return res
