# Codex Workshop Instruction Template

Use this template when you want Codex to create a workshop asset package similar to the Public Healthcare AIDP Workshop, but for another domain such as finance, banking, insurance, manufacturing, telecom, retail, or public sector.

This template is designed for workshop builds that may include:

- Oracle AI Data Platform medallion architecture
- Autonomous AI Lakehouse Gold serving layer
- Oracle Analytics Cloud dashboards
- optional machine learning labs
- optional AI agent labs
- HTML workshop page
- Markdown workshop guide
- downloadable PDF guide
- diagrams, notebooks, datasets, and workshop screenshots

## How to Use This Template

1. Fill in the input sections below with domain-specific details.
2. Keep the constraints explicit, especially around data volume, schema style, and workshop flow.
3. Provide screenshots, links, or reference assets whenever look and feel matters.
4. Paste the completed input section into the master prompt at the end of this file.
5. Ask Codex to propose first if you want to review the workshop structure before it starts updating assets.

## Part 1 - Core Inputs to Provide

### A. Workshop Identity

Provide:

- exact workshop title
- domain name
- target audience
- workshop duration
- delivery mode: instructor-led, self-paced, or hybrid
- whether the output is customer-facing, internal execution-facing, or both

Example:

- Workshop title: `Corporate Banking AIDP Workshop`
- Audience: `solution engineers, data architects, analytics leads`
- Delivery mode: `hybrid`

### B. Business Use-Case Scope

Provide:

- the primary business scenario
- 3 to 6 sub-use-cases to reflect in the data
- the main business questions the workshop should answer
- whether there should be one guided use-case or multiple use-case lanes
- whether one use-case should be instructor-led and another DIY

Examples of sub-use-case categories:

- finance: close process, spend controls, planning variance, procurement, treasury
- banking: onboarding, deposits, lending, collections, fraud, branch operations
- manufacturing: production, quality, maintenance, supplier risk, inventory, plant throughput

### C. Technology Scope

State clearly:

- use Oracle AI Data Platform: yes or no
- use Autonomous AI Lakehouse: yes or no
- use Oracle Analytics Cloud: yes or no
- include ML lab: yes or no
- include AI agent lab: yes or no
- include real-time or streaming lab: yes or no
- services to explicitly exclude

### D. Data Inputs to Synthesize

Provide:

- maximum number of CSV datasets
- whether to include one JSON dataset
- whether to include one spatial dataset
- whether to include one document dataset
- minimum document size, for example 10 or more pages
- date range for the synthetic data
- operating footprint, for example regions, branches, plants, facilities, or business units

Recommended pattern when you want a compact workshop:

- max 5 CSV datasets
- 1 JSON dataset
- 1 spatial dataset
- 1 document dataset

### E. Data Modeling Expectations

Define:

- what Bronze should contain
- what Silver should contain
- what Gold should contain
- whether Gold must be a star schema or snowflake schema
- whether Gold should contain one fact table with dimensions or multiple stars
- whether one Gold star should be instructor-led and another should be DIY

Recommended phrasing:

- Bronze should preserve raw structure and add ingestion metadata only
- Silver should type, validate, conform, and derive operational fields
- Gold should publish business-serving star schema objects for OAC

### F. Dashboard Requirements

Provide:

- number of dashboards or canvases
- required dashboard topics
- whether dashboard titles should appear as horizontal tabs
- whether working filters are required
- whether spatial insight should use a map
- whether an AI assistant side panel pattern is needed
- screenshot or wireframe references for desired OAC look and feel

### G. Lab Design Requirements

Define:

- which setup steps are `Admin step`
- which hands-on steps are `Participant step`
- whether setup should be folded into lab execution steps
- whether Codex should provide OCI UI step-by-step guidance
- whether screenshots are required for AIDP, AI Lakehouse, OAC, ML, and Agents

Recommended rule:

- do not keep setup as a disconnected preamble
- fold setup into the labs
- label each step as `Admin step` or `Participant step`

### H. Output Assets Required

Choose what you want Codex to produce:

- HTML workshop page
- Markdown workshop guide
- downloadable PDF guide
- medallion architecture diagrams
- Bronze to Silver transformation diagrams
- Silver to Gold flow diagrams
- Gold star schema diagrams
- Bronze notebook
- Silver notebook
- Gold notebook
- ML notebook or `.py` file
- optional lab markdowns
- screenshots or mock visuals

### I. Style and Presentation Preferences

Provide:

- preferred tone: professional, workshop-demo, customer-facing, internal execution
- whether to align wording to official Oracle documentation
- whether generic workshop names should be avoided
- whether diagrams should be executive-style, technical, or hybrid
- whether visuals should use swimlanes, block diagrams, RDBMS-style layouts, or star-schema diagrams

### J. Reference Material to Align To

Provide:

- Oracle documentation links
- Oracle blog links
- LiveLabs links
- screenshots or mockups
- existing HTML pages
- PowerPoint or deck references
- any prior workshop assets that should be mirrored

## Part 2 - Constraints You Should State Explicitly

These constraints help Codex produce a clean workshop package without overbuilding or drifting:

- use synthetic data only
- keep raw datasets limited and intentional
- use medallion architecture in AIDP
- define Bronze to Silver logic clearly
- define Silver to Gold logic clearly
- use a Gold star schema unless another schema style is explicitly requested
- use OAC on the instructor-led Gold flow unless otherwise specified
- use map-based spatial insight if spatial data is included
- use the document dataset for vectorization and grounded chat if a document is included
- add ML and AI agent labs only if requested
- label all setup steps as `Admin step` or `Participant step`
- fold environment setup into the labs
- generate HTML and PDF outputs if the workshop is intended for sharing
- use separate notebooks for Bronze, Silver, Gold, and ML when relevant
- align AIDP, AI Lakehouse, OAC, ML, and Agent guidance to the provided Oracle docs and blogs
- when major structural changes are requested, propose first if the user asks for review before updating

## Part 3 - Fill-In Template

Copy the block below and fill in the values.

```text
Create a domain workshop asset similar to the public healthcare AIDP workshop.

Workshop title:
[Exact title]

Domain:
[Finance / Banking / Manufacturing / Insurance / etc.]

Audience:
[Who will attend]

Duration:
[Example: 3 hours core + optional labs]

Delivery mode:
[Instructor-led / hybrid / self-paced]

Output type:
[Customer-facing / internal execution guide / both]

Primary business scenario:
[Describe in 3 to 5 lines]

Sub-use-cases to reflect in the datasets:
1. [...]
2. [...]
3. [...]
4. [...]

Key business questions the workshop should answer:
1. [...]
2. [...]
3. [...]
4. [...]

Technology scope:
- Use Oracle AI Data Platform: yes/no
- Use Autonomous AI Lakehouse: yes/no
- Use OAC: yes/no
- Include ML lab: yes/no
- Include AI agent lab: yes/no
- Include streaming or real-time labs: yes/no
- Exclude these services: [...]

Raw data constraints:
- Max CSV files: [...]
- Include JSON: yes/no
- Include spatial: yes/no
- Include document: yes/no
- Document should be at least [x] pages
- Data date range: [...]
- Geography / branch / plant / region footprint: [...]

Medallion expectations:
- Bronze should include: [...]
- Silver should include: [...]
- Gold should be: [star schema / snowflake schema]
- Gold stars needed: [...]
- Instructor-led flow: [...]
- DIY flow: [...]

Dashboard requirements:
- Number of dashboard tabs/canvases: [...]
- Required dashboard topics: [...]
- Horizontal tabs: yes/no
- Working filters: yes/no
- Map visualization: yes/no
- AI assistant side panel style: yes/no
- Use this screenshot or wireframe as reference: [...]

Lab structure requirements:
- Fold setup into labs: yes/no
- Label steps as Admin step / Participant step: yes/no
- Need OCI UI step-by-step instructions: yes/no
- Need screenshots for AIDP / AI Lakehouse / OAC / ML / Agents: yes/no

Output assets required:
- HTML workshop page: yes/no
- PDF workshop guide: yes/no
- Markdown workshop guide: yes/no
- Architecture diagrams: yes/no
- Star schema diagrams: yes/no
- Bronze notebook: yes/no
- Silver notebook: yes/no
- Gold notebook: yes/no
- ML notebook or py file: yes/no
- Optional lab markdowns: yes/no

Presentation style:
[Professional / customer-facing / internal execution guide / highly visual / minimalist]

Reference sources to align to:
- Workshop inspiration links: [...]
- Oracle docs: [...]
- Oracle blogs: [...]
- Screenshots / deck / HTML references: [...]

Additional must-have instructions:
- [...]
- [...]
- [...]
```

## Part 4 - Master Prompt to Give Codex

Once you fill in the template, use the prompt below.

```text
Using the inputs below, create a complete workshop asset package.

Requirements:
1. Build the workshop as a professional HTML page and a downloadable PDF guide if those outputs are requested.
2. Use synthetic data only.
3. Use a medallion architecture in Oracle AI Data Platform with clear Bronze, Silver, and Gold steps.
4. Clearly define Bronze to Silver transformations and derived columns.
5. Clearly define Silver to Gold transformations and business metrics.
6. Use a Gold star schema unless I specify otherwise.
7. If multiple business flows are required, separate instructor-led and DIY flows clearly.
8. Use OAC only for the guided Gold star schema flow unless I specify otherwise.
9. Make the OAC section interactive in HTML and aligned to the provided visual reference if dashboard HTML is requested.
10. Use map-based spatial insight if spatial data is included.
11. Use the document dataset for vectorization and a chat-with-data-and-documents use-case if document input is included.
12. Add ML and AI agent optional labs only if requested.
13. For AIDP, AI Lakehouse, OAC, ML, and Agent sections, provide step-by-step OCI UI instructions where relevant.
14. Mark each workshop action clearly as Admin step or Participant step.
15. Fold environment setup into the labs instead of keeping it as a disconnected setup section.
16. If I provide reference blogs or docs, align the instructions to them carefully.
17. If I provide screenshots, HTML files, or deck references, align the visual design and layout to them.
18. Create clean supporting assets such as diagrams, notebooks, optional lab markdowns, screenshots, and PDF output as needed.
19. Before making major structural changes, propose the approach first when I explicitly ask for review before update.
20. Keep naming exact and domain-specific; avoid generic workshop titles.

Here are the inputs:
[Paste the completed template here]
```

## Part 5 - Recommended Minimum Input Set

If you want a strong result without over-specifying, provide at least:

- exact workshop title
- domain and target audience
- primary scenario plus 3 to 6 sub-use-cases
- raw data constraints
- Gold schema choice
- instructor-led and DIY split, if any
- dashboard reference screenshot
- which labs are admin versus participant
- Oracle docs and blogs to align to
- required output assets

## Part 6 - Optional Review-First Prompt

Use this if you want Codex to propose the structure before editing files:

```text
Before updating any workshop assets, first propose:
1. the business-use-case framing
2. the dataset plan
3. the Bronze to Silver flow
4. the Silver to Gold flow
5. the Gold star schema design
6. the lab structure
7. the admin versus participant step split
8. the dashboard plan
9. the optional ML and AI agent labs

Wait for my approval before updating the workshop content.
```

## Part 7 - Notes for Best Results

- Provide exact names when naming matters.
- Attach screenshots whenever look and feel matters.
- Constrain the raw data early to avoid unnecessary dataset sprawl.
- Decide early whether the workshop is primarily technical, business-facing, or demo-oriented.
- Decide early whether the agent experience should use official OCI flows, representative workshop visuals, or both.
- For customer workshops, ask Codex to keep diagrams intuitive and presentation-ready, not only technically correct.
