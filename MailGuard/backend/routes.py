import sqlite3
from flask import Blueprint, jsonify, request
from ml import predict
from .analysis import run
from .database import conn

api = Blueprint("api", __name__, url_prefix="/api")
err = lambda m, c=400: (jsonify(error=m), c)

@api.errorhandler(sqlite3.Error)
def db_error(e):
    return err("Database error. Please try again.", 500)

@api.get("/health")
def health():
    return jsonify(status="ok")

@api.post("/analyze")
def analyze():
    d = request.get_json(silent=True)
    if not isinstance(d, dict): return err("Invalid JSON body.")
    subject, message = d.get("subject", ""), d.get("message")
    if not isinstance(subject, str) or len(subject) > 300: return err("Subject must be text up to 300 characters.")
    if not isinstance(message, str) or len(message.strip()) < 10: return err("Please enter an email message of at least 10 characters.")
    if len(message) > 20000: return err("Message is too long (max 20,000 characters).")
    res = run(subject.strip(), message.strip())
    if d.get("save") is True:
        with conn() as c:
            res["id"] = c.execute("INSERT INTO analyses(subject,message,label,confidence,link_count,suspicious_links) VALUES(?,?,?,?,?,?)",
                (subject.strip(), message.strip(), res["label"], res["confidence"], len(res["links"]),
                 sum(l["suspicious"] for l in res["links"]))).lastrowid
    return jsonify(res)

@api.get("/history")
def history():
    with conn() as c:
        rows = c.execute("SELECT * FROM analyses ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@api.get("/history/<int:aid>")
def one(aid):
    with conn() as c:
        r = c.execute("SELECT * FROM analyses WHERE id=?", (aid,)).fetchone()
    if not r: return err("Analysis not found.", 404)
    d = dict(r); d["result"] = run(d["subject"] or "", d["message"])
    return jsonify(d)

@api.delete("/history/<int:aid>")
def delete(aid):
    with conn() as c:
        n = c.execute("DELETE FROM analyses WHERE id=?", (aid,)).rowcount
    return jsonify(deleted=n) if n else err("Analysis not found.", 404)

@api.delete("/history")
def clear():
    with conn() as c:
        c.execute("DELETE FROM analyses")
    return jsonify(deleted="all")

@api.get("/analytics")
def analytics():
    with conn() as c:
        by = {r[0]: r[1] for r in c.execute("SELECT label, COUNT(*) FROM analyses GROUP BY label")}
        tot = c.execute("SELECT COUNT(*), COALESCE(ROUND(AVG(confidence),1),0), COALESCE(SUM(suspicious_links),0) FROM analyses").fetchone()
        days = [dict(r) for r in c.execute("SELECT date(created_at) AS day, COUNT(*) AS n FROM analyses WHERE created_at >= date('now','-6 days') GROUP BY day ORDER BY day")]
    return jsonify(total=tot[0], avg_confidence=tot[1], suspicious_links=tot[2], by_label=by, per_day=days, model=predict.metrics())
