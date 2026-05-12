---
title: Home
---

# PRD Team 13 - NPLAN-7304 - Artifactory support for Event Streaming Client

Auto-generated catalog of PRDs in [ns-btan/team13-pm-prd](https://github.com/ns-btan/team13-pm-prd). Authored collaboratively by the Netskope PM team. PRDs are grouped by lifecycle status — active work stays expanded; older statuses are collapsed.

<div class="prd-catalog" markdown>

## 🚧 Active ({{ prd_count('active') }})

{% set active_groups = prds_grouped_by_domain('active') %}
{% if active_groups %}
{% for domain, prds in active_groups.items() %}
### {{ domain }}

{{ prd_status_table(prds) }}

{% endfor %}
{% else %}
_No active PRDs._
{% endif %}

<details class="status-fold" markdown>
<summary>🟡 Beta / Limited Availability ({{ prd_count('beta') }})</summary>

{% set beta_groups = prds_grouped_by_domain('beta') %}
{% if beta_groups %}
{% for domain, prds in beta_groups.items() %}
#### {{ domain }}

{{ prd_status_table(prds) }}

{% endfor %}
{% else %}
_None in beta._
{% endif %}

</details>

<details class="status-fold" markdown>
<summary>🟢 Shipped — Generally Available ({{ prd_count('ga') }})</summary>

{% set ga_groups = prds_grouped_by_domain('ga') %}
{% if ga_groups %}
{% for domain, prds in ga_groups.items() %}
#### {{ domain }}

{{ prd_status_table(prds) }}

{% endfor %}
{% else %}
_None shipped yet._
{% endif %}

</details>

<details class="status-fold" markdown>
<summary>📦 Shelved / Archived ({{ prd_count('shelved') + prd_count('archived') }})</summary>

{% set shelved_groups = prds_grouped_by_domain('shelved') %}
{% set archived_groups = prds_grouped_by_domain('archived') %}
{% if shelved_groups or archived_groups %}
{% for domain, prds in shelved_groups.items() %}
#### {{ domain }} _(shelved)_

{{ prd_status_table(prds) }}

{% endfor %}
{% for domain, prds in archived_groups.items() %}
#### {{ domain }} _(archived)_

{{ prd_status_table(prds) }}

{% endfor %}
{% else %}
_Nothing archived._
{% endif %}

</details>

</div>

---

## Authoring a new PRD

See [Process & Metadata Schema](process.md) for the canonical frontmatter schema every per-PRD `index.md` must include, plus the steps for adding a PRD or promoting one through the lifecycle.
