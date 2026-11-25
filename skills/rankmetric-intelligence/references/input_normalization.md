# Ingestion and normalization protocol

Build an input manifest: file, source institution/system, export date, covered dates, encoding, worksheet/CSV structure, row count, unique-source key, missing columns, status, and owner where appropriate. Treat upload timestamps and publication dates separately.

Normalize character encoding, extraneous spaces, safe case-folding and DOI URL prefixes. Retain the original fields and a `normalized_*` series. Never assume author separators or departments. Maintain a mapping sheet for renamed organizational units only with user authorization and effective dates. Map years from an explicit publication-year field, not an upload or export timestamp.

Distinguish `0` (measured none), `NA` (not applicable), blank (unspecified), `NIL` (potential no entry; verify with source rules), and `under press`/`accepted` (publication not necessarily assigned to a calendar year). Validate publication types, double-included online-first works, retractions/corrections and same DOI in multiple sources.

Export row-level data + transformation log + row count diagnostics. Every derived record requires a `source_file` and `source_row` or equivalent locator.

