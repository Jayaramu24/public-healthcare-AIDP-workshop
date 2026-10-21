# Optional DIY: connect the dimensional model

Optional · 0 minutes · Optional; outside the 180-minute core

After completing the core program, use the existing AILH connection to build a separate multi-table dataset from the fact and dimensions. This is independent practice; the core workshop continues to use the flattened MPHA_OAC_STAR_CLAIMS view.

1. Create a new dataset from the pre-existing MaxicareWorkshop connection. Select the claims fact plus district, program, claim classification and date dimensions shown in the foundation reference below.
2. Use a unique name such as MPHA_Claims_Dim_Pxx. Inspect the actual PK/FK names and join cardinalities before joining; do not assume two similar labels are equivalent keys.
3. Join fact foreign keys to each dimension’s unique key, retaining the fact grain. Check unmatched keys and duplicates. The district/program/category/month dimensions must not multiply claims.
4. Reconcile all five counts/paid totals to the flattened source before using the model. Describe the benefit of reusable dimensions and the additional join/grain responsibility.
5. The optional inline foundation below shows the earlier multi-table dataset and profiling screens. Reuse the supplied AILH connection. The legacy name MPHAClaimAnalysis denotes that separate dimensional dataset.
