"""Deterministic (no-LLM) checks for Java/Spring exam submissions.

run_static_checks() returns facts with file:line evidence. Feed them to the grader as ground truth
so the LLM cannot invent or forget constraint violations.
"""
import os
import re
import unicodedata

IGNORED_DIRS = {"target", "build", "out", ".idea", ".git", ".mvn", ".gradle", "node_modules", "__MACOSX"}
_KEYWORDS = {"return", "new", "else", "throw", "case", "assert"}

_ARGS = r'\((?:"(?:[^"\\]|\\.)*"|[^)"])*\)'          # (...) that may contain quoted strings with ')' inside
_ANN = r"@[\w.]+(?:" + _ARGS + r")?\s*"
_FIELD_RE = re.compile(
    r"(?P<ann>(?:" + _ANN + r")+)(?:(?:private|protected|public|final|static)\s+)*"
    r"(?P<type>[\w<>\[\],.?]+)\s+(?P<name>\w+)\s*(?:=[^;]*)?;"
)


# ----------------------------------------------------------------------------- loading
def _blank_comments(src: str) -> str:
    """Replace comments by spaces (keeps line numbers), so commented-out code never counts."""
    return re.sub(r"/\*.*?\*/|//[^\n]*", lambda m: re.sub(r"[^\n]", " ", m.group()), src, flags=re.S)


def load_sources(project_dir: str) -> dict:
    files = {}
    for root, dirs, names in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for n in names:
            if not n.endswith(".java"):
                continue
            full = os.path.join(root, n)
            rel = os.path.relpath(full, project_dir).replace("\\", "/")
            if "/src/test/" in "/" + rel:
                continue
            with open(full, encoding="utf-8", errors="ignore") as fh:
                files[rel] = _blank_comments(fh.read())
    return files


def _line(src: str, pos: int) -> int:
    return src.count("\n", 0, pos) + 1


def _fold(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))


def _check(cid, requirement, status, findings):
    return {"id": cid, "requirement": requirement, "status": status, "findings": findings}


# ----------------------------------------------------------------------------- checks
def check_signatures(sources: dict, required: list) -> list:
    out = []
    for sig in required:
        name = sig["name"]
        pat = re.compile(
            r"(?P<ret>[\w<>\[\],.?]+)\s+" + re.escape(name) + r"\s*\((?P<params>(?:\([^()]*\)|[^()])*)\)"
        )
        want_types = [" ".join(p.split()[:-1]) for p in sig["params"]]
        hits, found_any = [], []
        for rel, src in sources.items():
            for m in pat.finditer(src):
                if m.group("ret") in _KEYWORDS:
                    continue
                params = re.sub(_ANN, "", m.group("params"))
                got_types = [" ".join(p.replace("final ", "").split()[:-1]) for p in params.split(",") if p.strip()]
                where = f"{rel}:{_line(src, m.start())}"
                found_any.append(f"{where} {m.group('ret')} {name}({', '.join(got_types)})")
                if m.group("ret") == sig["return_type"] and got_types == want_types:
                    hits.append(where)
        want = f"{sig['return_type']} {name}({', '.join(want_types)})"
        if hits:
            out.append(_check(f"signature:{name}", want, "pass", hits))
        elif found_any:
            out.append(_check(f"signature:{name}", want, "fail", ["declared differently: " + s for s in found_any]))
        else:
            out.append(_check(f"signature:{name}", want, "fail", ["no method with this name in the project"]))
    return out


def _entity_fields(sources: dict):
    enums = set()
    for src in sources.values():
        enums.update(re.findall(r"\benum\s+(\w+)", src))
    for rel, src in sources.items():
        if "@Entity" not in src:
            continue
        cls = (re.search(r"\bclass\s+(\w+)", src) or [None, rel])[1]
        for m in _FIELD_RE.finditer(src):
            yield rel, src, cls, m, enums


def check_sequence_ids(sources: dict):
    findings, ok = [], True
    for rel, src, cls, m, _ in _entity_fields(sources):
        if "@Id" not in m.group("ann"):
            continue
        gv = re.search(r"@GeneratedValue\s*(" + _ARGS + r")?", m.group("ann"))
        args = (gv.group(1) or "") if gv else "<no @GeneratedValue>"
        good = "SEQUENCE" in args
        ok &= good
        findings.append(f"{rel}:{_line(src, m.start())} {cls}.{m.group('name')}: "
                        f"{'SEQUENCE' if good else 'not SEQUENCE -> ' + (args or 'AUTO (default)')}")
    if not findings:
        return _check("ids_use_sequence", "Ids auto-generated with a sequence", "fail", ["no @Id found in any @Entity"])
    return _check("ids_use_sequence", "Ids auto-generated with a sequence", "pass" if ok else "fail", findings)


def check_enum_as_string(sources: dict):
    findings, ok = [], True
    for rel, src, cls, m, enums in _entity_fields(sources):
        if m.group("type") not in enums:
            continue
        good = bool(re.search(r"@Enumerated\s*\([^)]*STRING", m.group("ann")))
        ok &= good
        findings.append(f"{rel}:{_line(src, m.start())} {cls}.{m.group('name')} ({m.group('type')}): "
                        f"{'STRING' if good else 'missing @Enumerated(STRING) -> stored as ORDINAL'}")
    if not findings:
        return _check("enum_as_string", "Enums stored as strings", "warn", ["no enum-typed entity field found"])
    return _check("enum_as_string", "Enums stored as strings", "pass" if ok else "fail", findings)


def check_scheduled(sources: dict):
    findings, enabled = [], any("@EnableScheduling" in s for s in sources.values())
    status = "pass"
    hits = [(rel, src, m) for rel, src in sources.items() for m in re.finditer(r"@Scheduled\s*(" + _ARGS + ")", src)]
    if not hits:
        return _check("scheduled_30s", "@Scheduled job every 30 seconds", "fail", ["no @Scheduled found"])
    for rel, src, m in hits:
        args, ok30 = m.group(1), None
        c = re.search(r'cron\s*=\s*"([^"]+)"', args)
        r = re.search(r"(?:fixedRate|fixedDelay)\s*=\s*(\d+)", args)
        if c:
            ok30 = c.group(1).split()[0] in ("*/30", "0/30", "0,30")
        elif r:
            ok30 = int(r.group(1)) == 30000
        findings.append(f"{rel}:{_line(src, m.start())} {args} -> "
                        f"{'30s OK' if ok30 else 'interval is not 30s' if ok30 is False else 'interval not recognised'}")
        if ok30 is not True:
            status = "warn" if ok30 is None else "fail"
    if not enabled:
        findings.append("@EnableScheduling not found: the job would never run")
        status = "fail"
    return _check("scheduled_30s", "@Scheduled job every 30 seconds", status, findings)


def check_aspect(sources: dict):
    findings, status = [], "fail"
    for rel, src in sources.items():
        if "@Aspect" not in src:
            continue
        for m in re.finditer(r'execution\s*\(([^"]*)\)', src):
            expr = m.group(1)
            good = "get*" in expr and "service" in expr.lower()
            findings.append(f"{rel}:{_line(src, m.start())} execution({expr}) -> {'matches get* in service package' if good else 'does not target get* in service'}")
            if good:
                status = "pass"
    return _check("aspect_get_service", "@Aspect logging date on get* methods of the service package", status,
                  findings or ["no @Aspect class found"])


def check_controller_layering(sources: dict):
    ctrl = {r: s for r, s in sources.items() if "@RestController" in s or "@Controller" in s}
    if not ctrl:
        return _check("rest_controller", "@RestController calling services", "fail", ["no @RestController found"])
    bad = [f"{r}: controller references a Repository directly" for r, s in ctrl.items() if re.search(r"\w+Repository\b", s)]
    return _check("rest_controller", "@RestController calling services (layered architecture)",
                  "fail" if bad else "pass", bad or [f"{r}: uses services only" for r in ctrl])


def check_jpql(sources: dict):
    hits = [f"{r}:{_line(s, m.start())}" for r, s in sources.items() if "interface" in s
            for m in re.finditer(r"@Query\s*\(", s)]
    return _check("jpql_query", "JPQL query in the repository", "pass" if hits else "fail",
                  hits or ["no @Query found in any repository"])


def check_keyword_precedence(sources: dict):
    """Generic trap: findByAOrBAndC is parsed by Spring Data as A OR (B AND C)."""
    findings = []
    for rel, src in sources.items():
        if "interface" not in src:
            continue
        for m in re.finditer(r"\b((?:find|get|read|query|count|exists)\w*By\w+)\s*\(", src):
            head = src[src.rfind(";", 0, m.start()) + 1:m.start()]
            name = m.group(1)
            if "@Query" in head:
                continue
            if re.search(r"[a-z0-9]Or[A-Z]", name) and re.search(r"[a-z0-9]And[A-Z]", name):
                findings.append(f"{rel}:{_line(src, m.start())} {name}: mixes Or and And -> parsed as A OR (B AND C); "
                                "the last condition only applies to the second branch")
    if findings:
        return _check("keyword_or_and_precedence", "Derived query with Or + And behaves as intended", "warn", findings)
    return None


# ----------------------------------------------------------------------------- orchestration
def run_static_checks(project_dir: str, instructions: str, required_signatures: list = None) -> dict:
    sources = load_sources(project_dir)
    text = _fold(instructions or "")
    checks = []
    if required_signatures:
        checks += check_signatures(sources, required_signatures)
    if "sequence" in text:
        checks.append(check_sequence_ids(sources))
    if "enum" in text and "chaine" in text:
        checks.append(check_enum_as_string(sources))
    if "scheduled" in text:
        checks.append(check_scheduled(sources))
    if "aspect" in text:
        checks.append(check_aspect(sources))
    if "restcontroller" in text:
        checks.append(check_controller_layering(sources))
    if "jpql" in text:
        checks.append(check_jpql(sources))
    trap = check_keyword_precedence(sources)
    if trap:
        checks.append(trap)
    summary = {s: sum(1 for c in checks if c["status"] == s) for s in ("pass", "fail", "warn")}
    return {"checks": checks, "summary": summary, "files_scanned": len(sources)}


def build_evaluation_evidence(static_results: dict = None, test_results: list = None, extraction_status: str = "ok") -> dict:
    """Fields to add to the /evaluate-exam response so the grade states what it rests on."""
    executed = any(not r.get("infra_error") for r in (test_results or []))
    basis = (["static_analysis"] if static_results and static_results.get("checks") else []) + ["llm_code_review"]
    if executed:
        basis.append("execution")
    return {
        "evaluation_basis": basis,
        "tests_available": executed,
        "grade_status": "validated" if executed else "provisional",
        "grade_confidence": "high" if executed else "low",
        "needs_teacher_review": (not executed) or extraction_status != "ok",
        "extraction_status": extraction_status,
    }


def render_evidence_for_prompt(static_results: dict) -> str:
    """Prepend to the grading prompt. Makes deterministic facts binding on the LLM."""
    lines = ["VERIFIED FACTS FROM AUTOMATED STATIC ANALYSIS (ground truth; do not contradict, do not omit):"]
    for c in static_results["checks"]:
        lines.append(f"- [{c['status'].upper()}] {c['requirement']}")
        lines += [f"    * {f}" for f in c["findings"][:6]]
    lines += ["",
              "RULES: Report a violation only if it is listed above or you can quote the exact code that shows it. "
              "Label anything else as UNVERIFIED. No tests were executed unless stated. "
              "Do not recommend changes that contradict the exam's class diagram."]
    return "\n".join(lines)
