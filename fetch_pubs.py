import requests, yaml

ORCID = "0000-0001-6092-8298"

r = requests.get(
    f"https://pub.orcid.org/v3.0/{ORCID}/works",
    headers={"Accept": "application/json"},
)
dois = set()
for group in r.json()["group"]:
    for ext in group["external-ids"]["external-id"]:
        if ext["external-id-type"] == "doi":
            dois.add(ext["external-id-value"].lower())

# dois.discard("10.26434/chemrxiv-xxxx")  # manually exclude an entry if needed


def fmt(a):
    name = f"{a.get('given','')} {a.get('family','')}".strip()
    if a.get("family", "").lower() == "malone" and a.get("given", "").lower().startswith("i"):
        return f"<strong>{name}</strong>"
    return name


def venue(w):
    if w.get("type") == "posted-content":
        return "Preprint"
    if w.get("container-title"):
        return w["container-title"][0]
    return w.get("publisher", "")

items = []
for doi in sorted(dois):
    w = requests.get(f"https://api.crossref.org/works/{doi}").json()["message"]
    if w.get("type") == "posted-content" and w.get("relation", {}).get("is-preprint-of"):
        continue
    authors = ", ".join(fmt(a) for a in w.get("author", []))
    parts = w["issued"]["date-parts"][0] + [1, 1]
    items.append({
        "title": (w.get("title") or ["(untitled)"])[0],
        "author": authors,
        "date": f"{parts[0]}-{parts[1]:02d}-{parts[2]:02d}",
        "description": venue(w),
        "path": f"https://doi.org/{doi}",
    })

yaml.safe_dump(items, open("publications.yml", "w"), sort_keys=False)