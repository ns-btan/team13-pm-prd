"""
MkDocs macros for PRD catalog + status badges.

Scans docs/nplan-*/index.md for YAML frontmatter; used by docs/index.md
to render Active / Beta / Shipped / Shelved / Archived sections
automatically, and by per-PRD pages to render a status pill.
"""
import glob
import os
import re
import yaml
from collections import OrderedDict

STATUS_LABELS = {
    'active': 'Active',
    'beta': 'Beta',
    'ga': 'Shipped',
    'shelved': 'Shelved',
    'archived': 'Archived',
    'unknown': 'Unknown',
}

PRIORITY_LABELS = {'p0': 'P0', 'p1': 'P1', 'p2': 'P2', 'p3': 'P3'}


def _read_frontmatter(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except OSError:
        return {}
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def _collect_prds(docs_dir):
    prds = []
    for index_path in sorted(glob.glob(os.path.join(docs_dir, 'nplan-*', 'index.md'))):
        meta = _read_frontmatter(index_path)
        if not meta.get('nplan'):
            continue
        slug = os.path.basename(os.path.dirname(index_path))
        meta['slug'] = slug
        meta['url'] = slug + '/'
        meta['status'] = (meta.get('status') or 'unknown').lower()
        meta['domain'] = meta.get('domain') or 'Uncategorized'
        meta['subdomain'] = meta.get('subdomain') or ''
        meta['priority'] = (meta.get('priority') or '').lower()
        prds.append(meta)
    return prds


def define_env(env):
    """Hook required by mkdocs-macros-plugin."""

    @env.macro
    def all_prds():
        docs_dir = os.path.join(env.project_dir, 'docs')
        return _collect_prds(docs_dir)

    @env.macro
    def prds_by_status(status):
        status = status.lower()
        return [p for p in all_prds() if p['status'] == status]

    @env.macro
    def prds_grouped_by_domain(status):
        """Return OrderedDict {domain: [prds]} for a given status, sorted
        alphabetically by domain, NPLAN ascending within each."""
        prds = prds_by_status(status)
        groups = {}
        for p in prds:
            groups.setdefault(p['domain'], []).append(p)
        ordered = OrderedDict()
        for domain in sorted(groups.keys()):
            ordered[domain] = sorted(groups[domain], key=lambda p: int(p.get('nplan') or 0))
        return ordered

    @env.macro
    def status_label(status):
        return STATUS_LABELS.get((status or 'unknown').lower(), status)

    @env.macro
    def status_badge(status):
        s = (status or 'unknown').lower()
        label = STATUS_LABELS.get(s, s)
        return '<span class="status-badge status-' + s + '">' + label + '</span>'

    @env.macro
    def priority_badge(priority):
        p = (priority or '').lower()
        if p not in PRIORITY_LABELS:
            return ''
        return '<span class="priority-badge priority-' + p + '">' + PRIORITY_LABELS[p] + '</span>'

    def _row(prd):
        """One markdown table row for a PRD."""
        n = prd.get('nplan', '?')
        title = prd.get('title', 'Untitled')
        subdomain = prd.get('subdomain') or ''
        owner = prd.get('owner') or ''
        priority = prd.get('priority') or ''
        phase = prd.get('phase') or ''
        updated = prd.get('updated') or ''

        title_cell = '[**NPLAN-' + str(n) + '** — ' + title + '](' + prd['url'] + ')'
        if subdomain:
            title_cell += ' <span class="subdomain-tag">' + subdomain + '</span>'
        pri_cell = ''
        if priority and priority.lower() in PRIORITY_LABELS:
            pri_cell = (
                '<span class="priority-badge priority-' + priority.lower() + '">'
                + PRIORITY_LABELS[priority.lower()] + '</span>'
            )
        owner_cell = '[@' + owner + '](https://github.com/' + owner + ')' if owner else ''
        return '| ' + ' | '.join([
            title_cell, pri_cell, phase, owner_cell, str(updated)
        ]) + ' |'

    @env.macro
    def prd_status_table(prds):
        """Render a full markdown table (header + all rows) as a single string
        so Jinja loop whitespace doesn't break table continuity."""
        if not prds:
            return '_No PRDs in this group._'
        lines = [
            '| PRD | Priority | Phase | Owner | Updated |',
            '|-----|----------|-------|-------|---------|',
        ]
        lines.extend(_row(p) for p in prds)
        return '\n'.join(lines)

    @env.macro
    def prd_count(status):
        return len(prds_by_status(status))
