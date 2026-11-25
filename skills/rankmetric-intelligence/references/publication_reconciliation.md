# Publication reconciliation and indexing

Uniqueness signals in conservative priority: normalized DOI; exact trusted database identifier (e.g., EID) when DOI is absent; normalized full title plus the same publication year when both identifiers are missing, subject to manual assessment. DOI normalization may strip `doi:` or official DOI URL prefixes and surrounding punctuation; never manufacture a DOI.

- Same DOI across multiple source files: normally one work, many source occurrences; flag conflicting title, year or publication type.
- Same title and year but different DOIs: do not merge automatically; place in exception log.
- Same title/year with one DOI missing: permit an automatic link only when one unique positive identifier candidate exists and metadata is consistent; retain both original rows.
- Same title across years: check online-first/journal issue date and official counting convention; do not arbitrarily force into a reporting year.
- Source row duplicates: log raw rows, unique works, duplicates and manual review queue separately.
- Journal-versus-conference or extended versions: do not collapse on topical similarity; require bibliographic review.

Indexing classification: source-provided Scopus, WoS, Google Scholar, Other, Unindexed, Unspecified are not automatically equivalent to independently verified coverage. WoS/Scopus overlap is possible; treat separately unless a mutually exclusive partition is explicitly needed and documented. Membership can be title-level, issue-level or date-constrained. Annotate database, evidence URL, indexing date/issue relevance and `verification_status`.

Per-file expected row counts; per-year unique counts; by-year and type counts; duplicate pair provenance; and unresolved identifiers are mandatory where relevant.

