# Verified corrections from BIS Standards Navigator (SIH26107)

This directory is a contribution from a sibling project in the same
`BIS-Standards-AI-Assistant` org — **BIS Standards Navigator**
(Next.js/Postgres app, separate from this repo's ChromaDB pipeline) —
which independently fact-checked entries from
`dataset/real_bis_standards.json` against real sources (official BIS
product manuals, archive.org mirrors, or a clearly-labeled secondary
source where no primary source was found) before using this data in a
production-facing tool.

**This does not modify `dataset/real_bis_standards.json`.** It is added
alongside it so this repo's maintainers can review and reconcile at
their own pace, without a schema-breaking overwrite (the Navigator's
schema — `is_number`, `verification_status`, `verification_note`,
`source_url` — differs from this repo's `standard_number`/`part`/
`section`/`year` fields, and this repo's own `scripts/
ingest_to_vectorstore.py` ChromaDB pipeline may depend on the current
field shape).

## `navigator-verified-standards.json`

48 entries: the original 22 from `real_bis_standards.json`, each
individually checked (14 `verified_accurate` unchanged, 8 `corrected`
with a `verification_note` explaining exactly what was wrong), plus 26
new entries added from this repo's 2026-08-30 50-entry update — those
26 are marked `needs_review` (not independently verified yet), each
noting which of this repo's claims (supersession, amendments,
notification numbers) are unverified.

## Two specific fabrications found — please check these

Both were present in the original 22-entry dataset and are **still
present, unfixed, and still self-labeled `verified_accurate`** in the
2026-08-30 50-entry update (`BIS-STD-009` and `BIS-STD-001`/
`BIS-STD-014` in the current file):

1. **`IS 302 (Part 2/Sec 26):2014` labeled "Safety of Induction
   Cookers"** (`BIS-STD-009`). Section 26 of IS 302 Part 2 is clocks, a
   completely different product. The real induction-cooker standard is
   `IS 302 (Part 2/Section 6):2009`.
2. **A fabricated "2024/2020 edition" pattern**, seen twice:
   - `BIS-STD-001` (`IS 14543`) claims `year: "2024"` and
     `supersedes: "IS 14543:2016"`. No 2024 edition of IS 14543 exists —
     the current specification is `IS 14543:2016` (Third Revision); a
     QCO guideline amendment was issued 2024-11-05, which appears to be
     what got conflated into an edition year.
   - `BIS-STD-014` (`IS 4151`) claims `year: "2020"` and
     `supersedes: "IS 4151:2015"`. No 2020 edition exists — the
     regulatory *order* mandating helmet certification is dated 2020,
     but it requires compliance with `IS 4151:2015`.

Since the same conflation pattern (a regulatory/QCO date mistaken for
an edition year) recurred across two entries and two dataset versions,
we'd suggest treating every `year`/`supersedes` field in
`real_bis_standards.json` as needing a source-URL check before
downstream consumers rely on it — not just these two.

## Full detail

Every entry's exact verification note (what was checked, what was
wrong, what the correct value is) is in
`navigator-verified-standards.json` itself, in each entry's
`verification_note` field.
