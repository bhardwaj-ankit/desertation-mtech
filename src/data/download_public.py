"""
Downloader for the real public datasets named in the abstract / research report.

Unlike a stub catalogue, this module performs the actual fetches against the
working public endpoints discovered for each source, writing real data under
``data/raw/<source>/`` and recording provenance in ``SOURCE.md`` +
``public_sources_status.json``. Every fetch degrades gracefully: if the network
or a source is unavailable the synthetic schema-compatible stand-ins remain in
place so the rest of the pipeline never blocks.

Real sources wired here:
  * NASA C-MAPSS  - PHM turbofan run-to-failure ZIP (S3 mirror)
  * FAA SDR       - per-year Service Difficulty Report CSVs (FAA APIC endpoint)
  * NASA ASRS     - de-identified maintenance report-set PDFs
  * FAA AD        - Airworthiness Directives via the Federal Register API
                    (metadata JSONL + a sample of full-text rules)

Run standalone:  python -m src.data.download_public
"""
import html
import json
import os
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
import zipfile

_UA = {"User-Agent": "Mozilla/5.0 (techlog-data-prep)"}

# Recent SDR years to pull by default (each ~33 MB / ~66k rows).
SDR_YEARS = [2023, 2024, 2025]
# ASRS curated report sets most relevant to maintenance / techlog narratives.
ASRS_SETS = ["mechanic", "fuel", "cabin_fumes"]
# How many Federal-Register AD rules to fetch, and how many to pull full text for.
AD_PAGES = 5          # 100 per page
AD_FULLTEXT = 50

CMAPSS_URL = ("https://phm-datasets.s3.amazonaws.com/NASA/"
              "6.+Turbofan+Engine+Degradation+Simulation+Data+Set.zip")
SDR_URL = "https://external.apic4e.faa.gov/sdrs/retrieve/SDR-{year}.csv"
ASRS_URL = "https://asrs.arc.nasa.gov/docs/rpsts/{name}.pdf"
FR_API = "https://www.federalregister.gov/api/v1/documents.json"


def _get(url, dest, timeout, binary=True):
    try:
        req = urllib.request.Request(url, headers=_UA)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        with open(dest, "wb" if binary else "w") as f:
            f.write(data if binary else data.decode("utf-8", "replace"))
        return True, len(data)
    except (urllib.error.URLError, socket.timeout, OSError, ValueError) as e:
        return False, f"{e.__class__.__name__}"


# --------------------------------------------------------------------------- #
def _has(path):
    return os.path.exists(path) and (os.path.isdir(path) or os.path.getsize(path) > 0)


def _fetch_cmapss(sdir, timeout):
    if _has(os.path.join(sdir, "CMAPSSData", "train_FD001.txt")):
        return "ok", "cached (already downloaded)"
    zpath = os.path.join(sdir, "CMAPSSData.zip")
    ok, info = _get(CMAPSS_URL, zpath, timeout)
    if not ok:
        return "fallback_synthetic", f"download failed ({info})"
    try:
        with zipfile.ZipFile(zpath) as z:
            z.extractall(sdir)
        # archive nests a second zip; extract it too, then flatten *.txt
        for root, _, files in os.walk(sdir):
            for fn in files:
                if fn.endswith(".zip") and fn != "CMAPSSData.zip":
                    with zipfile.ZipFile(os.path.join(root, fn)) as z2:
                        z2.extractall(os.path.join(sdir, "CMAPSSData"))
        n_txt = sum(1 for r, _, fs in os.walk(sdir) for f in fs if f.endswith(".txt"))
        return "ok", f"{info} bytes, {n_txt} data files extracted"
    except zipfile.BadZipFile:
        return "fallback_synthetic", "downloaded file was not a valid zip"


def _fetch_sdr(sdir, timeout):
    real = os.path.join(sdir, "real")
    os.makedirs(real, exist_ok=True)
    if all(_has(os.path.join(real, f"SDR-{y}.csv")) for y in SDR_YEARS):
        return "ok", f"cached (years {SDR_YEARS[0]}-{SDR_YEARS[-1]})"
    got = []
    for y in SDR_YEARS:
        ok, info = _get(SDR_URL.format(year=y), os.path.join(real, f"SDR-{y}.csv"), timeout)
        if ok:
            got.append(f"{y}:{info}B")
    if not got:
        return "fallback_synthetic", "no SDR years downloaded"
    return "ok", f"years {', '.join(got)}"


def _fetch_asrs(sdir, timeout):
    rs = os.path.join(sdir, "report_sets")
    os.makedirs(rs, exist_ok=True)
    if all(_has(os.path.join(rs, f"{n}.pdf")) for n in ASRS_SETS):
        return "ok", f"cached (report sets: {', '.join(ASRS_SETS)})"
    got = []
    for name in ASRS_SETS:
        ok, info = _get(ASRS_URL.format(name=name), os.path.join(rs, f"{name}.pdf"), timeout)
        if ok:
            got.append(name)
    if not got:
        return "fallback_synthetic", "no ASRS report sets downloaded"
    return "ok", f"report sets: {', '.join(got)}"


def _fetch_ad(sdir, timeout):
    real = os.path.join(sdir, "real")
    os.makedirs(real, exist_ok=True)
    if _has(os.path.join(real, "faa_ads_federal_register.jsonl")):
        return "ok", "cached (Federal Register AD rules)"
    params = {
        "per_page": "100", "order": "newest",
        "conditions[agencies][]": "federal-aviation-administration",
        "conditions[term]": "airworthiness directive",
        "conditions[type][]": "RULE",
    }
    fields = ["document_number", "title", "publication_date", "abstract",
              "html_url", "raw_text_url", "effective_on", "citation"]
    qs = urllib.parse.urlencode(params, doseq=True) + "".join(
        f"&fields[]={urllib.parse.quote(f)}" for f in fields)
    recs = []
    for page in range(1, AD_PAGES + 1):
        try:
            req = urllib.request.Request(f"{FR_API}?{qs}&page={page}", headers=_UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                res = json.load(r).get("results", [])
        except (urllib.error.URLError, socket.timeout, OSError, ValueError):
            break
        if not res:
            break
        recs.extend(res)
    if not recs:
        return "fallback_synthetic", "Federal Register API unavailable"
    with open(os.path.join(real, "faa_ads_federal_register.jsonl"), "w") as f:
        for d in recs:
            f.write(json.dumps(d) + "\n")
    # Full text from govinfo.gov (the official GPO repository) - NOT blocked,
    # unlike federalregister.gov's raw_text_url which serves an access page.
    ft = os.path.join(real, "full_text")
    os.makedirs(ft, exist_ok=True)
    n_ft = 0
    for d in recs[:AD_FULLTEXT]:
        docnum = d.get("document_number")
        pub = d.get("publication_date")        # YYYY-MM-DD
        if not (docnum and pub):
            continue
        url = f"https://www.govinfo.gov/content/pkg/FR-{pub}/html/{docnum}.htm"
        try:
            req = urllib.request.Request(url, headers=_UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read().decode("utf-8", "replace")
        except (urllib.error.URLError, socket.timeout, OSError):
            continue
        m = re.search(r"<pre>(.*?)</pre>", raw, re.S | re.I)
        if not m:
            continue
        text = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
        if text:
            with open(os.path.join(ft, f"{docnum}.txt"), "w") as fp:
                fp.write(text)
            n_ft += 1
    return "ok", f"{len(recs)} AD rules (metadata), {n_ft} with real full text (govinfo)"


# --------------------------------------------------------------------------- #
SOURCES = {
    "nasa_cmapss": {
        "name": "NASA C-MAPSS Turbofan Degradation Simulation",
        "url": "https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/",
        "license": "Public (NASA PCoE)", "fetch": _fetch_cmapss,
        "notes": "Run-to-failure multivariate time series (3 op settings + 21 sensors), FD001-FD004.",
    },
    "faa_sdr": {
        "name": "FAA Service Difficulty Reports (SDR)",
        "url": "https://www.faa.gov/av-info/download_SDR",
        "license": "US Government public record", "fetch": _fetch_sdr,
        "notes": "Per-year SDR CSV exports (structured malfunction/defect reports).",
    },
    "nasa_asrs": {
        "name": "NASA Aviation Safety Reporting System (ASRS)",
        "url": "https://asrs.arc.nasa.gov/search/database.html",
        "license": "Public, de-identified", "fetch": _fetch_asrs,
        "notes": "Curated de-identified report-set PDFs (maintenance/fuel/cabin-fumes narratives).",
    },
    "faa_ad": {
        "name": "FAA Airworthiness Directives",
        "url": "https://www.federalregister.gov/agencies/federal-aviation-administration",
        "license": "US Government public record", "fetch": _fetch_ad,
        "notes": "AD final rules with abstract + full text via the Federal Register API.",
    },
}


def generate(out_dir="data/raw", timeout=240):
    report = {}
    for key, src in SOURCES.items():
        sdir = os.path.join(out_dir, key)
        os.makedirs(sdir, exist_ok=True)
        status, detail = src["fetch"](sdir, timeout)
        with open(os.path.join(sdir, "SOURCE.md"), "w") as f:
            f.write(f"# {src['name']}\n\n")
            f.write(f"- **Official source:** {src['url']}\n")
            f.write(f"- **Licence:** {src['license']}\n")
            f.write(f"- **Fetch status:** {status} - {detail}\n\n{src['notes']}\n")
        report[key] = {"name": src["name"], "url": src["url"],
                       "license": src["license"], "fetch": status,
                       "detail": detail, "notes": src["notes"]}
        print(f"    {key}: {status} - {detail}")

    with open(os.path.join(out_dir, "public_sources_status.json"), "w") as f:
        json.dump(report, f, indent=2)
    ok = sum(1 for s in report.values() if s["fetch"] == "ok")
    print(f"  public_sources: {len(report)} sources, {ok} fetched live "
          f"(synthetic fallback for any that failed)")
    return report


if __name__ == "__main__":
    generate()
