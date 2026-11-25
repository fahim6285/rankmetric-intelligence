# SDG and multi-label attribution

One publication may belong to SDG 3 and SDG 9 simultaneously: a unique-work count across the union is 1, while summed SDG incidences is 2. The correct counts depend on the question; display both only with clear labels.

Store membership as `unique_work_id,sdg_id,evidence_source,source_row,period,verification_status`. Validate SDG numbers are integers 1 through 17. Do not infer SDG mappings from titles unless explicitly asked for a transparently labelled exploratory classification, never equivalent to official database mappings.

For each year, publish `unique_works_in_union`, `source_rows`, `sdg_membership_incidence`, and a 1-to-17 SDG table. If a source lacks explicit SDG but its filename maps reliably to an SDG number, record that provenance. Never sum year-specific rows across cross-year revisions without documenting the year definition.

