from flask import Flask, request, Response
import json
import os

app = Flask(__name__)

SQL_FILE = "70kpapara.sql"


# -----------------------------
# UTF-8 + güvenli loader
# -----------------------------
def load_data():
    import re

    data = []

    if not os.path.exists(SQL_FILE):
        print("SQL dosyası yok!")
        return data

    with open(SQL_FILE, "r", encoding="utf-8", errors="ignore") as f:
        sql = f.read()

    match = re.search(r"INSERT INTO.*?VALUES\s*(.*?);", sql, re.S)
    if not match:
        return data

    values = match.group(1)

    rows = re.findall(r"\((.*?)\)", values, re.S)

    for r in rows:
        cols = []
        current = ""
        in_q = False

        for ch in r:
            if ch == "'" and not in_q:
                in_q = True
            elif ch == "'" and in_q:
                in_q = False

            if ch == "," and not in_q:
                cols.append(current.strip().strip("'"))
                current = ""
            else:
                current += ch

        cols.append(current.strip().strip("'"))

        if len(cols) >= 3:
            data.append({
                "id": cols[0],
                "paparano": cols[1],
                "adsoyad": cols[2]
            })

    return data


DB = load_data()
print(f"Yüklendi: {len(DB)} kayıt")


# -----------------------------
# HOME
# -----------------------------
@app.route("/")
def home():
    return Response(
        json.dumps({"status": "ok", "count": len(DB)}, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )


# -----------------------------
# PAPARA API
# -----------------------------
@app.route("/papara", methods=["GET"])
def papara():

    no = request.args.get("no")
    ad = request.args.get("ad")
    soyad = request.args.get("soyad")
    adsoyad = request.args.get("adsoyad")

    result = DB

    if no:
        result = [x for x in result if no in str(x["paparano"])]

    if ad:
        result = [x for x in result if ad.lower() in x["adsoyad"].lower()]

    if soyad:
        result = [x for x in result if soyad.lower() in x["adsoyad"].lower()]

    if adsoyad:
        result = [x for x in result if adsoyad.lower() in x["adsoyad"].lower()]

    return Response(
        json.dumps({
            "count": len(result),
            "data": result[:100]
        }, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )


# -----------------------------
# RENDER ENTRY
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
