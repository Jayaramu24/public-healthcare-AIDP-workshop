# Lab 1 Full Image Manifest

This manifest lists each screenshot reference visible in the public LiveLabs flow for:

- `Lab 1: Set Up OCI Resources`

It is organized task by task so we can decide later which images should be reused, adapted, or ignored for the Public Healthcare AIDP Workshop.

## Notes

- This manifest is based on the accessible LiveLabs Lab 1 page structure and the screenshot labels visible in that flow.
- Some image labels repeat multiple times inside the same task.
- Repeated image labels are kept because they often represent distinct moments in the step flow even when the alt text is the same.

## Status key

- `keep candidate`: likely useful for our workshop
- `review carefully`: may be useful, but depends on whether the screen is too source-specific
- `probably skip`: likely not needed in our final version

---

## Task 1: Create Compartment

### Images present

1. `Compartments`
   - Appears to show:
     OCI compartments landing page / navigation view
   - Suggested status:
     `review carefully`
   - Why:
     Useful only if we keep compartment creation in the workshop

2. `Compartments`
   - Appears to show:
     Create compartment action / compartment create dialog or page
   - Suggested status:
     `review carefully`

3. `Compartments`
   - Appears to show:
     New compartment creation form
   - Suggested status:
     `review carefully`

4. `Compartments`
   - Appears to show:
     Created compartment confirmation / resulting compartment page
   - Suggested status:
     `review carefully`

---

## Task 2: Provision ATP Instance

### Images present

1. `Navigate to AI Database`
   - Appears to show:
     OCI navigation path to Autonomous AI Database
   - Suggested status:
     `review carefully`

2. `ATP Setup`
   - Appears to show:
     Create Autonomous Database page with Transaction Processing workload
   - Suggested status:
     `review carefully`

3. `ATP Storage`
   - Appears to show:
     Storage sizing or capacity settings during ATP creation
   - Suggested status:
     `probably skip`
   - Why:
     Too detailed unless we want cost-sizing guidance

4. `ATP Password`
   - Appears to show:
     Password and network access setup during ATP creation
   - Suggested status:
     `review carefully`

---

## Task 3: Create Source_XX Schema

### Images present

1. `ATP SQL`
   - Appears to show:
     Database Actions / SQL entry point for the ATP instance
   - Suggested status:
     `review carefully`

---

## Task 4: Add REST capabilities to Source_XX Schema

### Images present

1. `Database Users`
   - Appears to show:
     Database users screen in Database Actions
   - Suggested status:
     `review carefully`

2. `Enable REST`
   - Appears to show:
     Enable REST menu or action for the Source schema user
   - Suggested status:
     `review carefully`

3. `Enable REST`
   - Appears to show:
     REST enablement confirmation or next step
   - Suggested status:
     `review carefully`

4. `Set Quota`
   - Appears to show:
     User quota setting page for the Source schema
   - Suggested status:
     `review carefully`

5. `Set Quota`
   - Appears to show:
     Quota confirmation / apply changes state
   - Suggested status:
     `review carefully`

---

## Task 5: Log in to SQL Developer as Source_XX Schema

### Images present

1. `Sign in Source_XX Schema`
   - Appears to show:
     SQL Developer / Database Actions sign-in screen for the Source schema
   - Suggested status:
     `review carefully`

2. `Access REST Source_XX`
   - Appears to show:
     Alternate REST or schema access page / fallback access route
   - Suggested status:
     `probably skip`
   - Why:
     Better as a troubleshooting note than a core screenshot

---

## Task 6: Provision Autonomous AI Lakehouse

### Images present

1. `AI Database`
   - Appears to show:
     OCI navigation path to Autonomous AI Database
   - Suggested status:
     `keep candidate`

2. `Create AI Database`
   - Appears to show:
     Autonomous AI Database creation screen with Lakehouse workload
   - Suggested status:
     `keep candidate`

3. `Create AI Database`
   - Appears to show:
     Password / access type section during AI Lakehouse creation
   - Suggested status:
     `keep candidate`

4. `SQL Developer`
   - Appears to show:
     Database Actions / SQL entry point after AI Lakehouse provisioning
   - Suggested status:
     `keep candidate`

---

## Task 7: Create Gold_XX Schema

### Images present

1. No separate screenshot label explicitly listed in the accessible task body beyond SQL creation flow context
   - Suggested status:
     `n/a`

---

## Task 8: Add REST capabilities to GOLD_XX Schema

### Images present

1. `Enable REST`
   - Appears to show:
     Database users screen or enable REST entry point for Gold schema
   - Suggested status:
     `review carefully`

2. `Enable REST`
   - Appears to show:
     Enable REST selection for Gold schema user
   - Suggested status:
     `review carefully`

3. `Enable REST`
   - Appears to show:
     REST enable confirmation for Gold schema user
   - Suggested status:
     `review carefully`

4. `Enable REST`
   - Appears to show:
     Edit Gold user screen after REST enablement
   - Suggested status:
     `review carefully`

5. `Enable REST`
   - Appears to show:
     Quota setting / apply changes for Gold schema user
   - Suggested status:
     `review carefully`

---

## Task 9: Log in to SQL Developer as GOLD_XX Schema

### Images present

1. `Sign in Gold_XX Schema`
   - Appears to show:
     Database Actions / SQL sign-in path for Gold schema
   - Suggested status:
     `review carefully`

2. `Sign in Gold_XX Schema`
   - Appears to show:
     Sign-out and switch-user flow
   - Suggested status:
     `review carefully`

3. `Sign in Gold_XX Schema`
   - Appears to show:
     Gold schema login form
   - Suggested status:
     `review carefully`

4. `Access REST Gold_XX`
   - Appears to show:
     Alternate access / fallback REST route for Gold schema
   - Suggested status:
     `probably skip`

---

## Task 10: Provision AI Data Platform Instance

### Images present

1. `AI Data Platform`
   - Appears to show:
     OCI navigation path to AI Data Platform
   - Suggested status:
     `keep candidate`

2. `Create AIDP`
   - Appears to show:
     Create AI Data Platform instance screen
   - Suggested status:
     `keep candidate`

3. `Add Standard Policies`
   - Appears to show:
     Standard policy selection or policy add step during AIDP creation
   - Suggested status:
     `keep candidate`

4. `Add Standard Policies`
   - Appears to show:
     Additional standard policy setup state
   - Suggested status:
     `keep candidate`

5. `Add Standard Policies`
   - Appears to show:
     Standard policies added / confirmation state
   - Suggested status:
     `keep candidate`

6. `Add Optional Policies`
   - Appears to show:
     Optional policy selection during AIDP creation
   - Suggested status:
     `review carefully`

7. `Add Optional Policies`
   - Appears to show:
     Optional policy details / confirmation state
   - Suggested status:
     `review carefully`

---

## Task 11: Set Up Object Storage

### Images present

1. `Create OS Bucket`
   - Appears to show:
     Navigation to Object Storage / Buckets
   - Suggested status:
     `keep candidate`

2. `Create OS Bucket`
   - Appears to show:
     Create bucket action
   - Suggested status:
     `keep candidate`

3. `Create OS Bucket`
   - Appears to show:
     Bucket creation form
   - Suggested status:
     `keep candidate`

4. `Create OS Bucket`
   - Appears to show:
     Open created bucket
   - Suggested status:
     `keep candidate`

5. `Create OS Bucket`
   - Appears to show:
     Bucket details page showing namespace
   - Suggested status:
     `keep candidate`

6. `Create OS Bucket`
   - Appears to show:
     Objects / actions / create new folder path
   - Suggested status:
     `keep candidate`

7. `Create OS Bucket`
   - Appears to show:
     Folder creation form or confirmation
   - Suggested status:
     `keep candidate`

---

## Task 12: Provision Analytics Cloud Instance

### Images present

1. `Analytics Cloud`
   - Appears to show:
     OCI navigation path to Analytics Cloud
   - Suggested status:
     `keep candidate`

2. `Create OAC`
   - Appears to show:
     Analytics Cloud instance creation form
   - Suggested status:
     `keep candidate`

---

## Summary by image label

Below is the deduplicated list of all image labels visible across Lab 1:

1. `Compartments`
2. `Navigate to AI Database`
3. `ATP Setup`
4. `ATP Storage`
5. `ATP Password`
6. `ATP SQL`
7. `Database Users`
8. `Enable REST`
9. `Set Quota`
10. `Sign in Source_XX Schema`
11. `Access REST Source_XX`
12. `AI Database`
13. `Create AI Database`
14. `SQL Developer`
15. `Sign in Gold_XX Schema`
16. `Access REST Gold_XX`
17. `AI Data Platform`
18. `Create AIDP`
19. `Add Standard Policies`
20. `Add Optional Policies`
21. `Create OS Bucket`
22. `Analytics Cloud`
23. `Create OAC`

---

## Best immediate candidates for our healthcare workshop

If we later shortlist from this complete manifest, the strongest setup-image candidates are:

1. `AI Data Platform`
2. `Create AIDP`
3. `Add Standard Policies`
4. `AI Database`
5. `Create AI Database`
6. `SQL Developer`
7. `Create OS Bucket`
8. `Analytics Cloud`
9. `Create OAC`

These are the most directly reusable for the Public Healthcare AIDP Workshop setup path.
