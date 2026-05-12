# Event Streaming Client — Artifactory Support — Product Requirements Document

| Field | Value |
|-------|-------|
| **Document Version** | 1.8 |
| **Last Updated** | 2026-05-12 |
| **Status** | Draft (Business PRD, Concept phase) |
| **NPLAN** | NPLAN-7304 |
| **Domain** | Event Streaming Client / Deployment |

---

## 1. Overview [NPI Phase: Concept]

### 1.1 Problem Statement

Security-focused customers require that all Docker images be scanned for vulnerabilities before deployment. These customers operate environments where direct internet access is not permitted, and Artifactory serves as the only approved Docker image repository. Currently, Event Streaming Client does not support Artifactory as an image source, blocking these customers from deploying or upgrading the product within their security policies.

This affects two key actors:
- **Customer Admin:** Cannot deploy or maintain Event Streaming Client without violating corporate policy.
- **Security Team:** Cannot approve deployments that pull images directly from public registries or unapproved sources.

### 1.2 System Overview

This feature enables Event Streaming Client to be installed and upgraded by pulling Docker images through a customer-managed Artifactory repository, rather than directly from Docker Hub.

- Customers configure Artifactory as the Docker image source during installer setup.
- **Two Docker images** must be mirrored into Artifactory: `netskope/nsstreamingclient:stable` (the main streaming container) and `netskope/nswatcher:stable` (the watcher container that performs automatic weekly upgrades).
- Install and upgrade workflows pull both images from Artifactory instead of `hub.docker.com`.
- Images served from Artifactory may be pre-scanned for vulnerabilities per customer policy.
- The installer Python script (`netskope_event_streamingclient_installer.py`) is not downloaded via Artifactory — only Docker image pulls are in scope.
- Kubernetes and Helm deployment models are out of scope for this iteration.

### 1.3 Key Design Principles

1. **Policy compliance by default:** The feature must work within air-gapped and restricted-network environments where no direct internet access to public registries is available.
2. **No workflow divergence:** Artifactory-based installs and upgrades must follow the same operational steps as standard installs — no parallel or bespoke procedure.
3. **Customer-controlled image lifecycle:** Netskope does not manage the customer's Artifactory instance; customers are responsible for mirroring, scanning, and promoting images.
4. **Minimal configuration surface:** The only required change from the customer side should be specifying the Artifactory registry URL; all other behavior should be unchanged.
5. **Image authenticity (P2):** Because Artifactory is customer-managed, it introduces a risk that a non-Netskope or tampered image could be deployed. Netskope should provide a mechanism for the installer to verify that pulled images were genuinely issued by Netskope (e.g., image signature verification). This is not required for initial delivery but must be investigated and scoped by Engineering.

---

## 2. Market Landscape & Strategic Relevance [NPI Phase: Concept]

### 2.1 Market

Enterprise security requirements increasingly mandate that all software artifacts pass through an internal repository with vulnerability scanning before deployment. Tools like JFrog Artifactory are widely adopted as the enforcement point for this policy. Customers in regulated industries (financial services, healthcare, government) frequently prohibit direct pulls from Docker Hub or other public registries entirely.

This is not a single-customer ask — it is a common procurement blocker for security-sensitive accounts.

### 2.2 Relevance to Netskope

Supporting Artifactory removes a deployment blocker for security-conscious enterprise customers. Without this capability, Event Streaming Client cannot be adopted in environments with strict registry policies, limiting Netskope's ability to close or expand in regulated verticals. This is a table-stakes integration for enterprise deployments.

**Competitive landscape — event streaming and log forwarding:**

Research into competing SASE/SSE vendors reveals that **no direct competitor offers a containerized log-forwarding client equivalent to Event Streaming Client**. This is a structural differentiator, not just a feature gap:

| Vendor | Product | Deployment model | Custom registry support |
|--------|---------|-----------------|------------------------|
| Zscaler | Nanolog Streaming Service (NSS) | VM appliance (vSphere, AWS, Azure, GCP) | N/A — not container-based |
| Palo Alto Networks | Strata Logging Service / Cortex Data Lake | Cloud-hosted service | N/A — no customer-deployed container |
| Skyhigh Security | Cloud Connector | Appliance-based | N/A — not container-based |
| Broadcom / Symantec | No dedicated component | Cloud/sidecar (limited) | Not documented |
| Cisco Umbrella | No syslog forwarder | S3-based export only | N/A |
| Akamai (ETP) | Unified Log Streamer | Cloud-hosted | N/A |
| **Netskope** | **Event Streaming Client** | **Container (Docker/Podman) on customer infrastructure** | **Gap: Docker Hub only today — this feature closes it** |

**Key finding:** Zscaler NSS and PANW Strata are the closest functional equivalents for SIEM log forwarding, but both are VM appliances or cloud services — not containerized components deployed on customer infrastructure. Neither requires or offers registry configuration because they do not pull Docker images. Netskope's containerized model is architecturally distinct and gives customers more deployment flexibility, but it also means Netskope alone faces the Docker registry compliance requirement that this PRD addresses.

Closing the Artifactory gap strengthens Netskope's position in air-gapped and regulated-industry accounts where competitors currently cannot deploy a comparable streaming client at all.

### 2.3 Customer Voice

| Customer | Ask | Workaround Today | Status |
|----------|-----|-----------------|--------|
| SIX Group | Deploy Event Streaming Client via Artifactory to comply with internal vulnerability scanning policy; no direct internet registry access permitted | None — feature is not currently supported | Blocked / not supported |
| US Cellular Corporation | Deploy Event Streaming Client via Artifactory; same registry compliance requirement as SIX Group | None — feature is not currently supported | Blocked / not supported |

Both customers have no interim workaround and cannot deploy Event Streaming Client under their current security policies without this capability. Two independent enterprise customers with the same blocker confirms this is a segment-level requirement, not an isolated ask.

---

## 3. Definitions, Glossary & Naming [NPI Phase: Concept]

### 3.1 Glossary of Terms

| Term | Definition |
|------|------------|
| Event Streaming Client | Netskope's client component that streams transaction events to a customer's SIEM or other event consumer. Deployed as a Docker/Podman container managed by the Python installer script. |
| Installer | The Python script `netskope_event_streamingclient_installer.py`, used to install, reinstall, uninstall, and update the Event Streaming Client container. Versioned with the `I.` prefix (e.g., `I.2025.11.1`). |
| Streaming container | The main Docker image `netskope/nsstreamingclient:stable` that performs event streaming to the SIEM. |
| Watcher container | The Docker image `netskope/nswatcher:stable` that monitors the main container and performs automatic weekly upgrades. Must also be pulled from Artifactory when Artifactory mode is configured. |
| Artifactory | JFrog's artifact repository manager, used by enterprises as a proxy and cache for Docker images, with built-in vulnerability scanning. |
| Docker Hub | The default public registry at `hub.docker.com` from which Netskope images are currently pulled. Requires direct internet access — the key blocker for air-gapped customers. |
| Docker Image | A packaged, executable container image. Event Streaming Client uses two: the streaming container and the watcher container. |
| Air-gapped environment | A network environment with no direct outbound internet access; all external content must be brought in through approved proxies or repositories. |
| Image registry | A service that stores and distributes Docker images. Can be public (Docker Hub) or private (Artifactory, ECR, etc.). |
| Vulnerability scan | An automated inspection of a container image for known CVEs and security issues, typically enforced by corporate policy before deployment. |
| Podman | The default rootless container runtime on Red Hat Enterprise Linux. The Event Streaming Client installer detects and supports Podman as an alternative to Docker. |

### 3.2 Naming Conventions

| Use This | Not This | Rationale |
|----------|----------|-----------|
| Artifactory | JFrog | Customers refer to it as "Artifactory"; "JFrog" is the company name |
| Event Streaming Client | ESC (in customer-facing docs) | Avoid ambiguous acronyms in external-facing content |
| Docker image registry | Container registry (unless broadening scope) | Scope is Docker-specific for this iteration |

---

## 4. Personas [NPI Phase: Concept]

| Persona | Role | Interaction with Feature |
|---------|------|--------------------------|
| Customer Admin | Customer administrator configuring the Netskope platform via the Cloud Management Console. Responsible for deploying and maintaining Netskope components on the customer's infrastructure. | Configures Artifactory as the Docker image source during installer setup; runs install and upgrade commands; monitors ESC health via Management Console alerts (P2). |
| End User | Customer end user protected by the Netskope platform. | No direct interaction with this feature. Indirectly benefits from uninterrupted log streaming (maintained by the Customer Admin) that enables accurate policy enforcement and threat detection. |
| Security / Platform Team | Internal customer team that governs software supply chain policy. | Mirrors and vulnerability-scans Netskope images in Artifactory before the Customer Admin can deploy. Enforces the corporate policy that blocks direct Docker Hub pulls. |
| Netskope Support / PS | Assists customers with deployment and troubleshooting. | Must understand Artifactory-based deployment paths and the retry behavior to guide customers through connectivity failures and upgrade issues. |

---

## 5. Assumptions [NPI Phase: Concept]

| # | Assumption | Impact if Wrong |
|---|------------|-----------------|
| A1 | The customer has already mirrored **both** Netskope Docker images (`netskope/nsstreamingclient:stable` and `netskope/nswatcher:stable`) into their Artifactory instance before install/upgrade. | If only one image is mirrored, install may succeed but auto-upgrade will fail when the watcher tries to pull its image. |
| A2 | Artifactory is reachable from the host where Event Streaming Client is being installed (the same host that currently needs access to `hub.docker.com`). | If not, a network path/proxy solution is outside this scope. |
| A3 | The customer's Artifactory instance supports Docker registry protocol (v2). | If a non-standard version is used, additional compatibility work may be needed. |
| A4 | Authentication to Artifactory (credentials, tokens) is managed and provided by the customer. | If Netskope needs to provision or rotate credentials, scope expands significantly. |
| A5 | Kubernetes and Helm are not deployment targets for this feature iteration. | If customers require K8s/Helm support, a separate feature track is needed. |
| A6 | The installer Python script itself is downloaded from the Netskope API (`/api/v2/streamingclient/installer`) — this flow is unchanged; only Docker image pulls are in scope. | If installer binaries also need to transit Artifactory, scope expands. |
| A7 | On RHEL hosts using Podman (rootless), the Artifactory registry configuration mechanism differs from Docker. Engineering must handle both container runtimes. | If only Docker is supported, RHEL/Podman users cannot use this feature — defeating the RHEL-first priority. |
| A8 | The `stable` image tag is used for both images. Artifactory-mirrored images must preserve this tag. | If customers mirror with different tags, the installer's image reference logic must be updated. |
| A9 | The customer's Artifactory instance is accessible over HTTPS (TLS). Docker and Podman both enforce HTTPS for any registry using credentials. | If a customer's Artifactory is HTTP-only, TLS would need to be added on their side; insecure-registry workarounds must not be used (see §8.6). |

---

## 6. Detailed Use Cases & User Journeys [NPI Phase: Concept]

### 6.1 User Journeys

#### Journey 1: Initial Deployment via Artifactory

**Persona:** Customer Admin
**Goal:** Deploy Event Streaming Client in an environment where only Artifactory is an approved Docker registry.
**Entry Point:** Event Streaming Client installation documentation / installer CLI.

**Flow:**
1. Security team mirrors the Event Streaming Client Docker image from Netskope's registry into the customer's Artifactory instance and scans it for vulnerabilities.
2. Security team approves the image and promotes it to the release repository in Artifactory.
3. Customer Admin receives the Artifactory registry URL and image path from the security team.
4. Customer Admin runs the Event Streaming Client install command, specifying the Artifactory registry URL as the image source.
5. Installer pulls the Docker image from Artifactory instead of the public registry.
6. Event Streaming Client starts successfully and begins streaming events.

#### Journey 2: Configure Artifactory Source During Installation

**Persona:** Customer Admin
**Goal:** Set up Artifactory as the image source during initial install, including authentication credentials.
**Entry Point:** Event Streaming Client installer CLI.

**Flow:**
1. Admin launches the installer.
2. Installer prompts: choose image source — Docker Hub (default) or custom Artifactory repository.
3. Admin selects Artifactory and provides the registry URL.
4. Installer prompts for authentication credentials (username + token/password).
5. Installer validates connectivity and authentication against the registry.
6. Installer pulls the image from Artifactory and completes the installation.
7. Configuration (URL, auth, mode) is persisted for future upgrades.

#### Journey 3: Upgrade via Artifactory (Automatic or Manual)

**Persona:** Customer Admin
**Goal:** Upgrade Event Streaming Client to a new version without breaking the Artifactory-only policy, via either automatic or manual upgrade.
**Entry Point:** Event Streaming Client upgrade command or auto-upgrade trigger.

**Flow:**
1. Netskope releases a new version of the Event Streaming Client Docker image.
2. Security team mirrors the new image into Artifactory, scans it, and promotes it.
3. Upgrade is triggered (manually by admin, or automatically by the client).
4. Installer reads the persisted Artifactory configuration and credentials.
5. Installer pulls the new image version from Artifactory.
6. Event Streaming Client upgrades and restarts with the new version.

#### Journey 4: View and Edit Current Image Source Configuration

**Persona:** Customer Admin
**Goal:** Inspect the current image source mode and configuration, and update it if needed.
**Entry Point:** Event Streaming Client CLI management command.

**Flow:**
1. Admin runs the source inspection command (e.g., `esc config show`).
2. CLI displays: current mode (Docker Hub or Artifactory), registry URL, and authentication username. Secret credentials are masked.
3. Admin optionally runs the edit command (e.g., `esc config set`) to update the registry URL or credentials.
4. Changes are persisted and applied on the next install or upgrade.

### 6.2 Detailed Use Cases (Prioritized)

**Core (P0 — Need to Have):**

> As a customer admin, I want to choose between Docker Hub and a custom Artifactory repository as my image source during installation, so that I can comply with my organization's registry policy from the start.

> As a customer admin, I want to provide authentication credentials for my Artifactory repository during setup, so that the installer can pull images from a private registry.

> As a customer admin, I want to install Event Streaming Client by pulling its Docker image from my corporate Artifactory repository, so that I comply with my organization's policy of scanning all images before deployment.

> As a customer admin, I want to upgrade Event Streaming Client (both automatically and manually) using my configured Artifactory source, so that upgrading does not require me to bypass or reconfigure my security controls.

> As a customer admin, I want to view the current image source configuration (mode and non-sensitive settings) and edit it when needed, so that I can maintain and update the Artifactory setup over time without reinstalling.

**Auxiliary (P1 — Nice to Have):**

> As a customer admin, I want the installer to validate connectivity and authentication against Artifactory before attempting to pull, so that I receive actionable errors immediately if configuration is wrong.

> As a customer admin, I want all Artifactory-related errors to produce clear, actionable messages in the Event Streaming Client logs, so that I can diagnose and resolve issues without engaging Netskope support.

> As a customer admin, I want failed image pulls due to Artifactory issues to be surfaced as alerts in the Netskope Management Console, so that I am made aware of upgrade failures without monitoring the host directly.

> As a customer admin, I want the installer and watcher to automatically retry failed image pulls on a regular schedule (at least once per day), so that a temporary Artifactory outage does not permanently block upgrades without manual intervention.

**Deferred (P2 — Deliver after initial release):**

> As a customer admin, I want the installer to verify that the Docker images pulled from Artifactory were genuinely issued and signed by Netskope, so that I am protected against accidentally deploying a tampered or non-Netskope image from my Artifactory repository.

> As a customer admin, I want to configure a Docker-compatible registry other than Artifactory (e.g., AWS ECR, Azure Container Registry, Harbor, Nexus) as my image source, so that I can comply with my organization's registry policy regardless of which registry product is in use — provided Netskope formally supports it.

**Out of Scope:**
- Kubernetes and Helm-based deployments — separate feature track required.
- Installer binary download/updates via Artifactory — not in this iteration.
- Netskope managing or provisioning the customer's Artifactory instance.
- Automatic image mirroring from Netskope registry to customer Artifactory.
- Support for non-Docker artifact types (Helm charts, RPMs) via Artifactory.

### 6.3 Use Case Priority Summary

| Priority | Requirement Summary | Target Phase | Notes |
|----------|---------------------|--------------|-------|
| P0 | Installer prompts to choose Docker Hub or Artifactory as image source | GA | Core setup flow |
| P0 | Authentication credentials (username + token/password) configurable for Artifactory | GA | Mandatory — Artifactory is private |
| P0 | Install via Artifactory with persisted configuration | GA | Blocking requirement for SIX Group and similar customers |
| P0 | Automatic and manual upgrades work with Artifactory source configured | GA | Artifactory must not degrade upgrade capability |
| P0 | View current source mode + config (secrets masked); edit via CLI command | GA | Required for ongoing administration |
| P1 | Pre-pull connectivity and auth validation with clear error messaging | GA | Improves operator experience |
| P1 | Clear error messages in ESC logs for all Artifactory-related failures | GA | Required for operator self-service diagnosis |
| P1 | Artifactory failure alerts collected internally (ENG-only access) — no customer UI in this iteration | GA | Internal telemetry pipeline enables Support to assist on escalations; no customer-facing UI required for initial release. See BR-016. |
| P2 | Customer-visible Management Console UI: upgrade history, repository failure status, Warning indicator cleared on recovery | Post-GA | UX design required; ENG UI/backend review required; see §9.0 |
| P1 | Automatic retry of failed image pulls (at least once per day; no overloading Artifactory); retry behavior documented in online help | GA | Prevents permanent upgrade blocks from transient Artifactory outages |
| P1 | Audit log entry when admin selects a custom image source | GA | Traceability requirement per analytics/reporting spec |
| P2 | Netskope image signature verification — installer validates image was issued by Netskope | Post-GA | Can ship without for initial release; Engineering must investigate and ballpark scope before GA |
| P2 | Full custom source — support Docker-compatible registries beyond Artifactory (e.g., ECR, ACR, Harbor, Nexus) | Post-GA | Engineering to evaluate supportable registry options; supportability model required before committing |

---

## 7. Product Behavior & Corner Cases [NPI Phase: Concept]

### 7.1 Expected Product Behavior

During installation, the admin is presented with a choice of image source: Docker Hub (default) or a custom Artifactory repository. If Artifactory is selected, the admin provides the registry URL and authentication credentials. The installer validates connectivity and credentials, then pulls the image and completes the install. The selected mode and configuration are persisted so that subsequent automatic and manual upgrades use the same source without requiring reconfiguration.

The admin can inspect the current configuration at any time via a CLI command. Sensitive values (passwords, tokens) are never shown in plaintext — only the mode, registry URL, and credential username are displayed. The admin can update the configuration via a separate edit command.

### 7.2 Happy Paths

| Use Case | Trigger | Expected Behavior | UI/CLI State |
|----------|---------|-------------------|--------------|
| Setup: choose Docker Hub | Admin selects Docker Hub during install | Installer uses default public registry; no credentials required | "Image source: Docker Hub (default)" confirmed |
| Setup: choose Artifactory | Admin selects Artifactory, provides URL + credentials | Installer validates and persists config; pulls image from Artifactory | "Image source: Artifactory — [URL]" confirmed; install proceeds |
| Install via Artifactory | Install with Artifactory configured | Image pulled from Artifactory; install completes | Success message with registry URL shown |
| Manual upgrade via Artifactory | Admin runs upgrade command | Persisted Artifactory config used automatically; new image pulled | Success message with new version and registry URL |
| Auto upgrade via Artifactory | Automatic upgrade triggered | Same as manual upgrade; no admin interaction required | Upgrade completes silently using Artifactory |
| View current source config | Admin runs `esc config show` | Displays: mode, registry URL, auth username. Secrets masked. | Output shows `password: ****` or `token: ****` |
| Edit source config | Admin runs `esc config set` | Admin updates URL or credentials; new values persisted | Confirmation of updated config shown |

### 7.3 Sad Paths & Error States

| Scenario | Error Type | User-Facing Message | Recovery Action |
|----------|------------|---------------------|-----------------|
| Artifactory URL unreachable | Expected (network/config) | "Unable to reach registry at [URL]. Verify network connectivity and registry URL." | Admin checks network path, firewall rules, and URL config |
| Authentication failure at setup | Expected (credentials) | "Authentication failed for registry at [URL]. Check username and token/password." | Admin re-enters credentials; rotates token if expired |
| Authentication failure at upgrade | Expected (credentials) | "Upgrade failed: authentication failed for registry at [URL]. Run `esc config set` to update credentials." | Admin updates credentials via config edit command |
| Image not found in Artifactory | Expected (mirroring gap) | "Image [image:tag] not found in registry at [URL]. Ensure the image has been mirrored to your Artifactory instance." | Admin mirrors the image into Artifactory |
| Image pull denied (policy/scan block) | Expected (policy) | "Pull was denied by the registry. The image may not have passed your organization's vulnerability scan policy." | Security team approves the image in Artifactory |
| Artifactory returns unexpected error | Unexpected | "Registry returned an unexpected error [HTTP status]. Contact your Artifactory administrator." | Admin escalates to security/platform team |
| Auto upgrade fails due to Artifactory issue | Expected | Auto-upgrade aborts; error is written to ESC logs with the specific failure reason (HTTP status, DNS, timeout); alert is surfaced in the Management Console; retry is scheduled for the next retry window (minimum once per day) | Admin investigates Artifactory; retry fires automatically — manual intervention only needed if the issue persists beyond the retry window |
| Retry attempt succeeds after prior failure | Expected (recovery) | Upgrade completes using Artifactory; prior failure alert is cleared from Management Console | No admin action required |
| Retry attempts continue to fail (persistent Artifactory issue) | Expected (persistent) | Each failure is logged; Management Console alert remains active; retry continues on schedule without overloading Artifactory | Admin escalates to security/platform team to resolve Artifactory issue |

### 7.4 FAQ & Design Decisions

| Question | Answer | Rationale |
|----------|--------|-----------|
| Q: Does Netskope push images to the customer's Artifactory? | A: No. Customers mirror images themselves. | Netskope has no access to customer-internal infrastructure. |
| Q: Can customers use Artifactory as a pull-through proxy instead of a local mirror? | A: Yes, if configured on the Artifactory side. The installer only needs a valid registry URL. | Keeps Netskope's scope minimal — the installer is registry-agnostic as long as Docker v2 protocol is used. |
| Q: Does switching to Artifactory disable automatic upgrades? | A: No. Both automatic and manual upgrades must work with Artifactory configured. | Requirement explicitly stated — Artifactory must not degrade upgrade capability. |
| Q: Can the admin switch back from Artifactory to Docker Hub after initial setup? | A: Yes, via the config edit command. | The mode is a persistent but mutable configuration. |
| Q: What if the customer's Artifactory requires TLS with a custom CA? | A: The installer prompts for a CA certificate path when Artifactory mode is selected. The certificate is placed in the appropriate runtime path: `/etc/docker/certs.d/` (Docker), `/etc/containers/certs.d/` (Podman system), or `~/.config/containers/certs.d/` (Podman rootless). If the certificate is already in the OS trust store, the customer can skip this step. See §8.6. | TLS with custom CA is standard in enterprise Artifactory deployments; now specified in §8.6. |
| Q: Could a customer accidentally deploy a non-Netskope or tampered image via Artifactory? | A: Yes — this is a known risk of using a customer-managed registry. Image signature verification (P2) is identified to address this, but is not required for initial delivery. Customers are advised to control access to their Artifactory repository. | P2 feature deferred to post-GA to meet customer timeline. |

---

## 8. Detailed Product Specifications [NPI Phase: Concept/Design]

### 8.1 Registry Source Mode

The installer exposes a source mode setting with two values:

| Mode | Description |
|------|-------------|
| `dockerhub` | Default. Pulls images from the Netskope public Docker Hub registry. No credentials required. |
| `artifactory` | Pulls images from the configured Artifactory registry URL. Authentication credentials required. |

- **Mode is set interactively** during install and persisted in the installer configuration store.
- **Mode is mutable** — admin can switch modes post-install via the config edit command.

> **P2 — Full Custom Source:** Engineering should evaluate whether the `artifactory` mode can be generalized to support other Docker Registry API v2-compatible registries (e.g., AWS ECR, Azure Container Registry, Harbor, Nexus). If technically feasible, a future mode (e.g., `custom`) or a broadened `artifactory` mode could cover these. **Supportability is the key constraint:** Netskope must be able to realistically support the auth models, TLS configurations, and error surfaces of any registry it endorses. Engineering must propose a supportability model — potentially a tested/supported registry list — before this is committed. See OI-010.
- **Default mode:** `dockerhub` (no regression for existing deployments).

### 8.2 Registry Configuration (Artifactory Mode)

When mode is `artifactory`:

- **Registry URL** — required. Artifactory supports three URL patterns; the installer must accept all three:

  | Pattern | Format | Notes |
  |---------|--------|-------|
  | Repository path (recommended) | `artifactory.corp.example.com/artifactory/docker-repo` | Most common in enterprise; works without subdomain DNS setup |
  | Port-based | `artifactory.corp.example.com:8443` | Each repository gets a unique port; less common |
  | Subdomain | `docker-repo.artifactory.corp.example.com` | Requires DNS wildcard; repository names must not contain underscores |

- **Scope:** Applies to **all** Docker/Podman image pull operations during install and upgrade — both `netskope/nsstreamingclient:stable` and `netskope/nswatcher:stable`. Does not affect installer Python script download (via `/api/v2/streamingclient/installer`).

### 8.3 Authentication

Authentication is **mandatory** when mode is `artifactory`. The installer must not allow Artifactory mode to be saved without credentials.

Artifactory supports three credential types; the installer must accept all three:

| Credential Type | Format | Recommended for |
|----------------|--------|-----------------|
| Username + Password | Plain credentials | Development/test only; discouraged for production |
| Username + API Key | API Key from Artifactory user profile | Standard enterprise use |
| Username + Identity Token | Service account token (modern approach) | Preferred for automated/service deployments |

- **Implementation:** Credentials are passed to Docker/Podman via `docker login <registry-url>` (Ubuntu/Docker) or `podman login <registry-url>` (RHEL/Podman). The installer invokes the appropriate login command for the detected runtime; credentials are stored in the Docker/Podman credential store (`~/.docker/config.json` on Docker; `~/.config/containers/auth.json` on rootless Podman) rather than in a separate installer config file.
- **Storage:** Credentials reside in the runtime's native credential store. The installer must not write credentials to its own config files in plaintext.
- **Display rule:** Credentials are never shown in plaintext in any CLI output, logs, or diagnostic output. Username may be displayed; password/token must be masked (`****`).
- **Rotation:** Admin can update credentials at any time via the config edit command, which re-runs `docker login` / `podman login` with the new credentials without reinstalling.

### 8.4 Upgrade Compatibility

Configuring Artifactory as the image source must not restrict or disable any existing upgrade capability:

- **Manual upgrades** (run installer with `reinstall` option) must use the persisted Artifactory configuration automatically.
- **Automatic upgrades** (weekly, performed by the watcher container `netskope/nswatcher:stable`) must also use the Artifactory registry. The watcher container pulls the updated `netskope/nsstreamingclient:stable` image — this pull must use the configured Artifactory source, not Docker Hub.
- If an automatic upgrade fails due to an Artifactory error (e.g., image not yet mirrored), the failure must be surfaced via the existing upgrade failure notification mechanism (Docker/Podman logs).

### 8.5 Configuration View and Edit Commands

Two CLI operations are required:

**View (`esc config show` or equivalent):**
- Displays: current mode (`dockerhub` / `artifactory`), registry URL (if Artifactory), authentication username (if Artifactory).
- Secrets (password / token) are always masked.

**Edit (`esc config set` or equivalent):**
- Allows updating: mode, registry URL, authentication credentials.
- On save, validates connectivity and authentication if mode is `artifactory`.
- On validation failure, does not persist the new configuration and surfaces an error.

### 8.6 TLS / Certificate Handling

TLS is **required** for Artifactory authentication — Docker and Podman both enforce HTTPS for any registry that uses credentials. Enterprise deployments typically use a self-signed certificate or an internal CA that is not trusted by the OS by default.

The installer must handle both runtimes:

| Runtime | CA Certificate Path | Notes |
|---------|-------------------|-------|
| Docker (Ubuntu) | `/etc/docker/certs.d/<hostname>:<port>/ca.crt` | Per-registry directory; Docker reads automatically on pull |
| Podman — system (RHEL, root) | `/etc/containers/certs.d/<hostname>:<port>/ca.crt` | Same directory convention as Docker |
| Podman — rootless (RHEL, user) | `~/.config/containers/certs.d/<hostname>:<port>/ca.crt` | User-scoped path; must be used for rootless Podman installs |

**Requirements:**
- The installer must prompt the customer for the path to their CA certificate file if Artifactory mode is selected.
- The installer copies or references the CA certificate to the appropriate runtime path for the detected runtime and privilege level.
- If the customer's Artifactory uses a publicly trusted certificate (i.e., already in the OS trust store), no additional CA configuration is needed — the installer should offer this as an option ("Use system certificate store").
- The `--tls-verify=false` flag (Podman) and equivalent insecure-registry settings (Docker) must **not** be used; they defeat the security purpose of Artifactory in a controlled environment.

### 8.7 Platform Priority

RedHat Enterprise Linux support is a higher priority than Ubuntu for this feature. Engineering should target RHEL compatibility first.

### 8.8 Alternative Registry Landscape (P2 Scope Input)

Research finding for the P2 full custom source requirement (OI-010): all major enterprise private registries use the **OCI Distribution Specification** (the industry-standard successor to Docker Registry API v2). This means the authentication and pull protocol is structurally identical across registries — the primary variation is in credential type and TLS configuration.

| Registry | Deployment Model | Authentication | High-Security / FedRAMP Use |
|----------|-----------------|----------------|----------------------------|
| **JFrog Artifactory** | Self-hosted or cloud | Username + password, API key, identity token | Widely used in regulated enterprise; supports immutable repos and build promotion |
| **Harbor** (CNCF) | Self-hosted, open-source | LDAP/AD, OIDC (Azure AD, Okta, Keycloak) | Strong FedRAMP fit; built-in vulnerability scanning and image signing; Kubernetes-native |
| **Red Hat Quay** | Self-hosted or cloud | LDAP, OIDC | Preferred in RHEL/OpenShift environments; strong in regulated industries |
| **Sonatype Nexus** | Self-hosted | Username/password, LDAP/AD, token | Common in enterprises that manage multiple artifact types (Maven, npm, Docker); requires Docker Bearer Token Realm |
| **AWS ECR** | Cloud (AWS-hosted) | AWS IAM credentials (AWS CLI `ecr get-login-password`) | FedRAMP-authorized; dominant in AWS-native air-gapped environments (GovCloud) |
| **Azure Container Registry (ACR)** | Cloud (Azure-hosted) | Azure AD / service principal | FedRAMP-authorized; dominant in Azure Gov environments |

**Key finding for P2 scoping:** Harbor is the most relevant alternative for high-security customers who do not use Artifactory. It is open-source, CNCF-backed, and architecturally designed for regulated environments. ECR and ACR are dominant in cloud-native government deployments. Nexus and Quay serve customers who already standardized on those vendors for other artifact types.

**Supportability constraint (from OI-010):** All six registries above use OCI Distribution Spec over HTTPS — the pull protocol is identical. The differentiation is in **how credentials are obtained** (static token vs. short-lived AWS/Azure IAM token). ECR and ACR require runtime credential refresh (tokens expire), which adds complexity the installer must handle. Artifactory, Harbor, Nexus, and Quay all use long-lived tokens compatible with `docker login` / `podman login`. Engineering should propose a supportability model based on this distinction.

---

## 9. UI Screens & Workflows [NPI Phase: Concept]

### 9.0 Admin Console UI — Current State and P2 Target

**P1 — No UI (current state):** Event Streaming Client currently has no Admin Console UI. This feature is CLI/configuration-driven via the existing Python installer script (`netskope_event_streamingclient_installer.py`). There is no Admin Console UI surface for this iteration.

**P2 — Alerts & Monitoring UI (target state):** When customer-visible alerting and monitoring is delivered (post-GA), the Admin Console UI must surface the following for each ESC deployment:

| UI Element | Behavior |
|-----------|---------|
| Upgrade history | Display when the last upgrade occurred (timestamp and version) |
| Repository access failures | Display if there has been a failure to access the configured repository, and when the failure occurred |
| ESC status indicator | Status changes to **Warning** when there is an active repository access failure; Warning is cleared automatically once repository access is restored and a successful pull is confirmed |

> Note: The UX team must design this surface. PM has provided the behavioral requirements above as input. ENG UI/backend must review and approve the final UX design. Reference: Google Drive Document (linked in Jira).

### 9.1 Installer: Image Source Setup During Install

**Purpose:** Allow the admin to choose and configure the image source (Docker Hub or Artifactory) as part of the existing interactive install flow.

**Entry point:** `python3 netskope_event_streamingclient_installer.py` → option `1. install`

The image source prompt fits into the existing install flow after the system checks pass and before image pull begins:

```
python3 netskope_event_streamingclient_installer.py
NETSKOPE LOG STREAM CLIENT INSTALLER I.2026.x.x

Please specify an option:
1. install           - Set up and configure the container
2. reinstall         - Remove and recreate the container
3. uninstall         - Remove the container and cleanup
4. update_client_key - Update client key and restart container
5. show_config       - Display current image source configuration
6. update_registry   - Update image source URL or credentials

Enter option (install/reinstall/uninstall/update_client_key): 1

INSTALLATION
>>> Checking if operating system is supported...
SUCCESS: Check for operating system passed.
>>> Checking if Docker/Podman is installed and running...
SUCCESS: All system checks passed.

>>> Configuring image source...
Select image source:
  1. Docker Hub (default — requires internet access to hub.docker.com)
  2. Custom Artifactory repository
Enter choice [1]: 2

Artifactory registry URL (e.g. artifactory.corp.example.com/netskope): artifactory.corp.example.com/netskope
Username: svc-netskope
Password/Token: ********

>>> Validating registry connectivity and credentials...
SUCCESS: Registry reachable. Authentication successful.
INFO: Image source configured: Artifactory — artifactory.corp.example.com/netskope

>>> Pulling Docker image: artifactory.corp.example.com/netskope/nsstreamingclient:stable
...
SUCCESS: Docker image pulled successfully!

>>> Pulling watcher image: artifactory.corp.example.com/netskope/nswatcher:stable
...
SUCCESS: Watcher image pulled successfully!

INSTALLATION COMPLETE
```

**On validation failure (auth):**
```
✗ Authentication failed for registry at artifactory.corp.example.com/netskope
  Check your username and password/token, then retry.
```

**On validation failure (connectivity):**
```
✗ Unable to reach registry at artifactory.corp.example.com/netskope
  Verify the URL and that the registry is reachable from this host.
```

---

### 9.2 Config View: Image Source Configuration

**Purpose:** Allow admin to inspect the current image source mode and non-sensitive settings post-install.

**Entry point:** New installer menu option `5. show_config`, consistent with the existing `update_client_key` pattern.

**Expected output (Artifactory mode):**
```
Image Source Configuration
--------------------------
Mode:         artifactory
Registry URL: artifactory.corp.example.com/netskope
Username:     svc-netskope
Password:     ****
```

**Expected output (Docker Hub mode):**
```
Image Source Configuration
--------------------------
Mode:         dockerhub (default)
```

---

### 9.3 Config Edit: Update Image Source Post-Install

**Purpose:** Allow admin to update the Artifactory URL or credentials without reinstalling.

**Entry point:** New installer menu option `6. update_registry`, consistent with the existing `update_client_key` option pattern.

**Expected flow:**
```
Enter option: 6  [update_registry]

Current image source: Artifactory — artifactory.corp.example.com/netskope (user: svc-netskope)

Update registry URL? [y/n]: y
New registry URL: artifactory-new.corp.example.com/netskope

Update credentials? [y/n]: y
Username: svc-netskope
Password/Token: ********

>>> Validating...
SUCCESS: Configuration saved. Artifactory will be used for all future installs and upgrades.
```

---

## 10. Component/Feature Catalog [NPI Phase: Concept]

| Component | Category | Platform Priority | Status | Description |
|-----------|----------|------------------|--------|-------------|
| Image source mode selection (Docker Hub / Artifactory) | Installer / Deploy | RHEL first, then Ubuntu | Coming Soon | Interactive setup to choose image source at install time |
| Artifactory registry URL configuration | Installer / Deploy | RHEL first, then Ubuntu | Coming Soon | Configurable registry URL for Artifactory mode |
| Artifactory authentication (username + token/password) | Installer / Deploy | RHEL first, then Ubuntu | Coming Soon | Mandatory credential support for private Artifactory registries |
| Config view command (`esc config show`) | Installer / Admin | RHEL first, then Ubuntu | Coming Soon | Displays current mode and non-sensitive config; masks secrets |
| Config edit command (`esc config set`) | Installer / Admin | RHEL first, then Ubuntu | Coming Soon | Updates mode, URL, and credentials; validates on save |
| Upgrade compatibility with Artifactory (auto + manual) | Installer / Upgrade | RHEL first, then Ubuntu | Coming Soon | Ensures persisted Artifactory config is used for all upgrade paths |
| Pre-pull connectivity and auth validation | Installer / Deploy | RHEL first, then Ubuntu | Coming Soon (P1) | Validates registry before pull attempt; surfaces actionable errors |
| Custom CA / TLS support | Installer / Deploy | RHEL first, then Ubuntu | Coming Soon (P1) | Support for Artifactory with enterprise CA certificates; installer prompts for CA cert path and places it in the correct runtime directory (see §8.6) |
| Structured error logging for Artifactory failures | Installer / Observability | RHEL first, then Ubuntu | Coming Soon (P1) | All Artifactory-related errors written to ESC logs with clear, structured messages including failure reason, registry URL, and HTTP status where applicable |
| Internal alert collection for Artifactory failures | Installer / Observability | RHEL first, then Ubuntu | Coming Soon (P1) | Failed image pull data collected via internal telemetry pipeline so Netskope Support can diagnose on customer escalation; no customer-facing UI in this iteration |
| Management Console UI — alerts & monitoring | Admin Console / Observability | TBD | Post-GA (P2) | Customer-visible surface showing upgrade history, repository failure timestamps, and ESC warning status; Warning cleared automatically on successful repository access restoration; UX design + ENG UI/backend review required |
| Automatic retry mechanism for failed image pulls | Installer / Upgrade | RHEL first, then Ubuntu | Coming Soon (P1) | Retries failed pulls on a scheduled basis (at least once per day); no thundering herd / Artifactory overload; retry behavior documented in online help |
| Netskope image signature verification | Installer / Security | RHEL first, then Ubuntu | Post-GA (P2) | Verify pulled images were signed by Netskope; protects against tampered or substituted images in Artifactory; Engineering to research approach (e.g., cosign/Sigstore, Docker Content Trust) and ballpark scope before GA |
| Full custom source (registry beyond Artifactory) | Installer / Deploy | TBD | Post-GA (P2) | Support Docker Registry API v2-compatible registries other than Artifactory (e.g., ECR, ACR, Harbor, Nexus); contingent on Engineering defining a supportability model (tested registry list, supported auth models) — see OI-010 |

---

## 11. Business Rules [NPI Phase: Concept]

| Rule ID | Condition | Behavior |
|---------|-----------|----------|
| BR-001 | Mode is `artifactory` | Installer uses the configured registry URL for all Docker image pulls during install and upgrade |
| BR-002 | Mode is `dockerhub` or not set | Installer uses the default public Netskope Docker Hub registry (no change from current behavior) |
| BR-003 | Admin attempts to save Artifactory mode without credentials | Configuration is rejected; installer requires username + password/token before persisting |
| BR-004 | Admin runs `esc config set` with mode `artifactory` | Installer validates connectivity and authentication before persisting; rejects on failure |
| BR-005 | Registry returns HTTP 401 | Installer surfaces an authentication error with guidance to check credentials via `esc config set` |
| BR-006 | Registry returns HTTP 403 | Installer surfaces a permission/policy denial error |
| BR-007 | Registry returns HTTP 404 | Installer surfaces an image-not-found error with guidance to mirror the image to Artifactory |
| BR-008 | Registry is unreachable (timeout / DNS failure) | Installer surfaces a connectivity error with the configured URL |
| BR-009 | Automatic upgrade is triggered with mode `artifactory` | Upgrade proceeds using persisted Artifactory config and credentials; no admin interaction required |
| BR-010 | Admin runs `esc config show` | Password/token fields are always masked (`****`); username and URL are shown in plaintext |
| BR-011 | Credentials are written to any log, diagnostic output, or audit record | Credentials must be masked or omitted; never written in plaintext |
| BR-012 | Kubernetes / Helm deployment is detected | Feature is not applicable; no Artifactory support for K8s/Helm in this iteration |
| BR-013 | Platform is RHEL vs. Ubuntu | RHEL support is delivered first; Ubuntu support follows in a subsequent release |
| BR-014 | Image signature verification is enabled (P2) and pulled image fails signature check | Installer aborts the install or upgrade with an error message indicating verification failure; no container is started from an unverified image |
| BR-015 | Any Artifactory-related error occurs (install or upgrade) | A structured error message is written to the ESC log including: error type, registry URL, HTTP status code (where applicable), and a human-readable description of the failure and recommended action |
| BR-016 | An image pull fails during automatic upgrade | Failure data is reported via internal telemetry so Netskope Support can assist on escalation (P1). In the P2 customer-visible UI: the ESC's status indicator in the Management Console changes to Warning; the Warning is cleared automatically once repository access is restored and a successful pull is confirmed |
| BR-017 | An automatic upgrade fails due to an Artifactory error | The system schedules a retry; retries must occur at minimum once per day; retry intervals must not cause excessive load on the customer's Artifactory instance (e.g., no rapid retry loops); retry behavior must be documented in the online help |
| BR-018 | Admin selects a custom Artifactory registry as the image source | An audit log entry is written to the ESC log recording that the admin selected a custom source (registry URL logged; credentials not logged) |

---

## 12. Analytics & Reporting [NPI Phase: Concept]

| Reporting Area | Priority | Details |
|----------------|----------|---------|
| Transaction events fields | P1 | Not applicable — this feature does not modify transaction event fields |
| Other event fields | P1 | Not applicable |
| Skope IT | P1 | Not applicable |
| Standard Reporting | P1 | Not applicable |
| NAA | P1 | Not applicable |
| Audit | P1 | ESC logs must trace that an admin selected a custom image source (registry URL recorded; see BR-018). This is the primary audit trail for Artifactory mode activation. |

**Monitoring requirements** *(telemetry and mandatory internal monitoring — Engineering owns dimension definition):*

| Monitoring Area | Priority | Details |
|-----------------|----------|---------|
| Internal metrics | P1 | Track how many ESC tenants/installs are using a custom image source (Artifactory mode) vs. Docker Hub default. Used to measure adoption and prioritize future investment. |
| Error reporting | P1 | Download failures must be reported internally so Netskope Support can diagnose and assist when customers escalate. Engineering to define the internal reporting pipeline (see OI-009). |

---

## 13. Architecture, Dependencies & Constraints [NPI Phase: Design/Implement]

### 13.1 Architecture Layers

**Current state (to be changed):**
The installer script pulls two Docker images directly from Docker Hub (`hub.docker.com`):
- `netskope/nsstreamingclient:stable` — the main streaming container
- `netskope/nswatcher:stable` — the watcher container responsible for weekly auto-upgrades

Both pulls require outbound internet access to `hub.docker.com`. This is the exact network requirement that blocks SIX Group and similar customers.

**Target state (this feature):**
When Artifactory mode is configured, both image pulls are redirected to the customer-specified Artifactory registry URL. The installer persists this configuration so the watcher container also uses Artifactory for all subsequent auto-upgrade pulls.

Container runtime support:
- **Ubuntu:** Docker (via systemd service)
- **RHEL 8/9:** Podman (rootless, via `~/.config/containers/containers.conf`)

The Artifactory configuration mechanism must work for both runtimes. On Docker, the installer invokes `docker login` and places CA certificates in `/etc/docker/certs.d/`. On Podman rootless, the installer invokes `podman login` and places CA certificates in `~/.config/containers/certs.d/`. Credentials are stored in the respective runtime's native credential store. See §8.3 and §8.6 for full specification.

### 13.2 Dependencies

| Dependency | Type | Description |
|-----------|------|-------------|
| JFrog Artifactory | External / Customer-managed | Customer's internal Docker registry; must support Docker Registry API v2; must contain both `nsstreamingclient:stable` and `nswatcher:stable` |
| `netskope_event_streamingclient_installer.py` | Internal | Python installer script; must be modified to prompt for and persist Artifactory configuration |
| `netskope/nswatcher:stable` container | Internal | Watcher container performing auto-upgrades; must be updated to read and use persisted Artifactory configuration when pulling new images |
| Docker (Ubuntu) | External / Customer-managed | Container runtime on Ubuntu; different registry auth configuration path than Podman |
| Podman (RHEL) | External / Customer-managed | Rootless container runtime on RHEL 8/9; registry auth via `~/.config/containers/containers.conf` |
| Customer network infrastructure | External / Customer-managed | Network path from install host to Artifactory must be open |

### 13.3 Accessory Requirements

- **RBAC:** N/A — no Admin Console changes in this iteration. Existing RBAC permission "Administration > Event Streaming" (Manage) is sufficient.
- **API requirements:** No new API required for this feature — configuration is handled entirely in the installer. If in a future iteration the Artifactory registry configuration should be manageable via API, it must be attached to the existing Client definition API (`/api/v2/streamingclient/`) rather than introduced as a standalone endpoint.
- **3rd party integrations:** JFrog Artifactory (customer-managed). Netskope does not integrate with Artifactory directly.
- **Audit & compliance:** Install and upgrade actions with the configured registry URL must be traced in ESC logs. Selecting a custom Artifactory source must produce an explicit audit log entry (BR-018). Retry behavior must be documented in the online help so customers understand the automatic recovery mechanism.
- **Data sovereignty:** No Netskope-managed data transits the customer's Artifactory. Images are customer-mirrored artifacts.
- **Security & privacy:** Credentials for Artifactory must not be logged in plaintext anywhere — installer output, Docker/Podman logs, or config file in unencrypted form.
- **Platform integration:** No dependencies on other Netskope products.

### 13.4 Constraints & Guardrails

| Constraint | Description | Impact |
|-----------|-------------|--------|
| Docker Registry API v2 only | Artifactory must expose a Docker v2-compatible registry endpoint | Non-Docker artifact types (Helm, RPM) are out of scope |
| No Kubernetes / Helm | K8s and Helm deployment modes are explicitly excluded | Customers using K8s must wait for a future iteration |
| Installer Python script unchanged | The installer (`netskope_event_streamingclient_installer.py`) is still downloaded from the Netskope API; only Docker/Podman image pulls are redirected via Artifactory | Scope is bounded; addresses the stated customer requirement |
| Both images must be covered | Both `netskope/nsstreamingclient:stable` AND `netskope/nswatcher:stable` must be pulled from Artifactory when in Artifactory mode | If only the main image is covered, auto-upgrades will fail |
| RHEL before Ubuntu | RHEL 8/9 (Podman/rootless) support is delivered first; Ubuntu support follows in a subsequent release | Engineering must handle Podman-specific registry auth on first delivery |
| Secrets never in plaintext | Authentication credentials must not appear in any installer output, Docker/Podman logs, or unencrypted config files | Engineering must audit all output paths for credential leakage |

---

## 14. GTM [NPI Phase: Implement]

### 14.1 Pricing & Packaging

No pricing change. Event Streaming Client requires an existing **"Log Streaming"** or **"Transaction Event Streaming"** license. Artifactory support is a deployment option within the existing license — no new SKU, add-on, or license tier required.

### 14.2 Documentation

The following ESC documentation pages must be updated before GA. All updates are additive — no existing content is removed, only Artifactory-related steps and parameters are added.

| Document | Updates Required |
|----------|-----------------|
| **Event Streaming Client Requirements** | Add Artifactory as a network access requirement in place of (or in addition to) `hub.docker.com`. Update supported repository types to include JFrog Artifactory (Docker Registry API v2). |
| **Event Streaming Client Deployment** | Add Artifactory configuration step to the 5-step deployment flow (between API access setup and client install). Document the `docker_registry` configuration parameter and the two images that must be mirrored: `netskope/nsstreamingclient:stable` and `netskope/nswatcher:stable`. |
| **Event Streaming Client Configuration** | Add a section on registry source mode (`dockerhub` vs. `artifactory`). Document how to set the Artifactory URL and credentials, plus how to revert to Docker Hub. |
| **Event Streaming Client — Red Hat / Podman** | Add Podman-specific Artifactory authentication steps (`~/.config/containers/containers.conf`), noting that rootless Podman has a different credential path than Docker. |
| **Event Streaming Client Operations and Troubleshooting** | Add a troubleshooting tree for Artifactory connectivity failures (HTTP 401/403/404/timeout). Document the automatic retry mechanism: ESC retries at least once per day without overloading the Artifactory instance. Retry behavior must be visible to the customer for support purposes. |
| **Event Streaming Client FAQs** | Add FAQ entries: "Can I use Artifactory instead of Docker Hub?", "What images do I need to mirror?", "What happens if Artifactory is temporarily unavailable?" |
| **Event Streaming Client Architecture** | Note that when Artifactory mode is configured, all Docker/Podman image pulls originate from the customer's Artifactory instance instead of `hub.docker.com`. The outbound network diagram should be updated to reflect this. |
| **Event Streaming Client API Access** | No changes required — API access and RBAC are unchanged. |

> **Note:** Retry behavior documentation is **mandatory per BR-017**. The online help must explicitly explain the retry schedule (at least once per day) and the non-overloading behavior, so customers and support engineers understand that transient Artifactory failures do not require manual intervention.

### 14.3 Support Readiness

Support and SE teams must be prepared to handle Artifactory-related deployment issues before GA:

- **Runbook — Authentication failures (HTTP 401/403):** Verify Artifactory credentials are correctly configured; confirm the token or service account has pull access to the `netskope` repository path; rerun installer with corrected credentials.
- **Runbook — Image not found (HTTP 404):** Confirm both `netskope/nsstreamingclient:stable` and `netskope/nswatcher:stable` have been mirrored to the customer's Artifactory instance; check that the configured registry URL path matches the Artifactory repository location.
- **Runbook — Connectivity failure (timeout/DNS):** Verify network path from the ESC install host to the Artifactory URL is open; check firewall rules and proxy configuration; ESC will retry automatically (at least once per day) — advise customer to check ESC logs for retry status.
- **Runbook — Auto-upgrade failure (watcher container):** Confirm `nswatcher:stable` is mirrored and accessible at the configured Artifactory URL; confirm watcher container is reading the persisted `docker_registry` configuration.
- **SE training:** SEs should understand that Artifactory support unlocks deployment for air-gapped and security-restricted customers who cannot pull directly from Docker Hub. This is a deployment unlock, not a product capability change — all ESC functionality is identical regardless of registry source.

### 14.4 COGS

No material change expected. Artifactory support shifts Docker image pulls to the customer's own infrastructure; Netskope incurs no additional hosting or bandwidth cost.

---

## 15. Rollout & Usage Projections [NPI Phase: Design]

| Rollout Area | Priority | Details |
|--------------|----------|---------|
| Feature controlled by flag | P1 | No feature flags expected. The feature is available to all ESC deployments on the versions that ship it. No tenant-level toggle required. |
| Feature enabled to all tenants | P1 | Available to all customers on the qualifying ESC version. No selective enablement or allowlist. |

- **Rollout phases:**
  - **Beta (Q3 2026):** Limited to 2–5 customers with known Artifactory requirements. Anchor Beta customers: SIX Group and US Cellular Corporation (both currently blocked from deploying ESC — see §2.3). Objective is to validate installer configuration flow, Podman/Docker compatibility, and watcher container propagation in real customer environments. Customer feedback collected before GA decision.
  - **GA (Q4 2026):** General availability to all customers following Beta feedback review and any required fixes. Target installer/container version to be proposed by Engineering — see OI-005.
- **Projected volumes:** Feature is expected to be used by a small segment of the ESC customer base (~5%). Adoption is inherently limited to customers who operate an Artifactory pipeline and have a policy prohibiting direct Docker Hub pulls.
- **Fair use & ToS:** No ToS implications anticipated.

---

## 16. Adoption Metrics [NPI Phase: Design]

- **Definition of "adopted":** Customer has configured Artifactory mode and successfully completed at least one install or upgrade using a custom registry URL.
- **Adoption forecast:** ~5% of the active ESC customer base. This feature addresses a specific high-security segment — customers who operate a managed Artifactory pipeline and enforce a policy against direct Docker Hub pulls. Broad adoption is not expected or targeted.
- **Tracking method:** Internal metrics telemetry (see §12 Monitoring requirements); count of ESC installs reporting `artifactory` mode active vs. `dockerhub`.
- **Key metrics:** Number of ESC installs/upgrades using Artifactory mode; error rate by error type (HTTP 401/403/404/timeout); retry success rate; time-to-first-successful-pull after configuration.

---

## 17. Open Items & Decisions Needed [NPI Phase: Concept]

| Item | Options | Owner | Status |
|------|---------|-------|--------|
| OI-001: Custom Artifactory integration approach | **Resolved.** Registry URL supports three Artifactory patterns (path, port, subdomain — see §8.2). TLS with custom CA is required; certificate paths differ by runtime and privilege level (see §8.6). Credentials are stored in Docker/Podman native credential store, not in a separate installer config. Engineering must implement runtime detection (Docker vs. Podman rootless) to select correct paths. | Engineering | Resolved — see §8.2, §8.3, §8.6 |
| OI-002: Authentication mechanism | **Resolved.** Installer invokes `docker login` (Ubuntu/Docker) or `podman login` (RHEL/Podman) with customer-provided username + API key or identity token. Credentials persist in `~/.docker/config.json` (Docker) or `~/.config/containers/auth.json` (rootless Podman). Plain username/password is also accepted but discouraged. See §8.3. | Engineering | Resolved — see §8.3 |
| OI-003: View/edit config mechanism | **Resolved (PM decision).** Config view and edit are exposed as new installer menu options, consistent with the existing `update_client_key` pattern. Two new options: `show_config` (read-only display of current mode, URL, masked credentials) and `update_registry` (edit mode, URL, credentials with live validation). See §9.2 and §9.3. | Engineering + PM | Resolved — see §9.2, §9.3 |
| OI-004: Watcher container Artifactory propagation | How does the watcher container (`nswatcher`) receive the Artifactory registry config to use when pulling updated images? Options: A) Config is written to a shared volume the watcher reads; B) Watcher is restarted with new env vars by the installer; C) Other. | Engineering | Open |
| OI-005: Target installer/container versions | Target installer version (I.x) and container version (C.x) to be determined by Engineering based on development timeline and release schedule. PM to confirm once Engineering proposes. | Engineering | Engineering to propose |
| OI-006: Image tag handling | The current default tag is `stable`. Must the customer mirror with the same `stable` tag, or can they use their own tag? A) Always use `stable` tag appended to the configured registry URL; B) Customer-configurable tag override | Engineering | Open |
| OI-007: Image signature verification approach (P2) | Engineering to research viable signing mechanisms for both Docker and Podman runtimes (e.g., cosign/Sigstore, Docker Content Trust). Must produce a ballpark scope estimate before GA. Not required for initial delivery to unblock SIX Group. | Engineering | Open (P2) |
| OI-008: Retry interval and backoff parameters | What is the retry schedule for failed image pulls? Minimum: at least once per day. Upper bound: must not overload Artifactory. Engineering to define exact interval, backoff strategy (fixed vs. exponential), and maximum retry window before giving up (if any). Parameters must be documented in online help. | Engineering | Open |
| OI-009: Management Console alert surfacing mechanism | How are Artifactory failure alerts collected and surfaced in the Management Console? Short-term: Engineering may use an internal-only data collection path (e.g., internal telemetry pipeline). Target state: customer-visible alerts. Engineering to propose short-term and long-term implementation approach. | Engineering | Open |
| OI-010: Full custom source — supportability model (P2) | Engineering to evaluate whether Artifactory mode can be generalized to support other Docker Registry API v2-compatible registries. Must answer: A) Are auth models (OAuth tokens for ECR/ACR, basic auth for Harbor/Nexus, etc.) sufficiently standardized to support generically? B) What does a tested/supported registry list look like? C) What is the support burden per additional registry? Engineering to propose a supportability model before this is committed as a deliverable. | Engineering | Open (P2) |

---

## 18. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-05-12 | btan@netskope.com | Initial draft from problem statement, scope, and use case inputs |
| 0.2 | 2026-05-12 | btan@netskope.com | Added SIX Group as customer voice (§2.3); updated OI-001 and OI-002 to reflect Engineering research track for industry-standard Artifactory integration; linked to NPLAN-7304 |
| 0.3 | 2026-05-12 | btan@netskope.com | Expanded §6 use cases and journeys (installer setup flow, view/edit config, upgrade compatibility); added §8.2–8.7 specs (source mode, auth mandatory, upgrade compat, view/edit commands, RHEL priority); updated §7 happy/sad paths; expanded §9 CLI screens; updated §10 component catalog and §11 business rules; added RHEL-first and secrets constraints to §13.4 |
| 0.4 | 2026-05-12 | btan@netskope.com | Reviewed full product documentation (10 PDFs from docs.netskope.com). Major corrections: identified two Docker images in scope (nsstreamingclient + nswatcher); corrected installer to Python script interface; updated §9 CLI screens to match real installer menu pattern; updated §13 architecture with Docker/Podman dual-runtime requirement; added watcher container propagation as OI-004; expanded assumptions (A7, A8); updated constraints and dependencies. |
| 0.5 | 2026-05-12 | btan@netskope.com | Added P2 image authenticity requirements: §1.3 design principle #5, §6.2 P2 use case, §6.3 priority table row, §7.4 FAQ entry, §10 component catalog row, BR-014 business rule, OI-007 open item for Engineering signature verification research. |
| 0.6 | 2026-05-12 | btan@netskope.com | Added P1 error handling requirements: structured ESC log messages, Management Console alerts (internal access short-term), automatic retry (≥1/day, no overload, documented in online help), audit log on custom source selection. Updates across §6.2, §6.3, §7.3, §10, §11 (BR-015–018), §12 (Analytics table from reporting spec), §13.3 (audit & online help doc requirement), §17 (OI-008, OI-009). |
| 0.7 | 2026-05-12 | btan@netskope.com | Added monitoring requirements (§12): internal metrics (ESC using custom source count) and error reporting (internal pipeline for support escalations). Added rollout requirements (§15): no feature flags, available to all tenants on qualifying ESC version. Updated §16 adoption metrics tracking method and key metrics to align with monitoring spec. |
| 0.8 | 2026-05-12 | btan@netskope.com | Added P2 full custom source requirement: support Docker Registry API v2-compatible registries beyond Artifactory (ECR, ACR, Harbor, Nexus), contingent on Engineering defining a supportability model. Updates: §6.2 P2 use case, §6.3 priority row, §8.1 spec note with supportability constraint, §10 component row, OI-010. |
| 0.9 | 2026-05-12 | btan@netskope.com | Added UX/UI and API requirements. §9.0: confirmed No UI for this iteration (P1); specified P2 target state MC UI (upgrade history, failure timestamps, Warning status cleared on recovery). §6.3: split MC alerts row into P1 (internal collection) and P2 (customer-visible UI). §10: split MC alerts component accordingly. BR-016: updated to reflect P1/P2 split and P2 Warning state lifecycle. §13.3: clarified no new API; future config API must attach to existing /api/v2/streamingclient/ endpoint. |
| 1.0 | 2026-05-12 | btan@netskope.com | Completed §2.2 competitive landscape: researched Zscaler, PANW, Skyhigh, Broadcom, Cisco, Akamai. Key finding: no competitor has a containerized log-forwarding client — Netskope's architecture is unique; this feature closes the Docker registry compliance gap that competitors do not face. |
| 1.1 | 2026-05-12 | btan@netskope.com | Completed §14 GTM: added §14.1 Pricing & Packaging (no license change), §14.2 Documentation (8-doc update table with mandatory retry behavior note per BR-017), §14.3 Support Readiness (4-class runbook for 401/403/404/connectivity + SE training), §14.4 COGS (no change). |
| 1.2 | 2026-05-12 | btan@netskope.com | Updated §4 Personas: added Customer Admin (Cloud Management Console) and End User personas with explicit interaction descriptions; retained Security/Platform Team and Support/PS. Updated §15 Rollout: Beta Q3 2026 (2–5 customers), GA Q4 2026 post-feedback. Updated §16 Adoption Metrics: ~5% adoption target, rationale (high-security/Artifactory segment), added time-to-first-successful-pull metric. |
| 1.3 | 2026-05-12 | btan@netskope.com | Resolved OI-001 and OI-002 via registry research. §8.2: expanded registry URL to cover all three Artifactory URL patterns (path/port/subdomain). §8.3: specified three credential types (password/API key/identity token) and Docker/Podman native credential store as storage mechanism. §8.6: fully specified TLS/custom CA requirements with per-runtime certificate paths (Docker, Podman system, Podman rootless). §8.8 new: alternative registry landscape for P2 scope (Harbor, Quay, Nexus, ECR, ACR) with supportability constraint on short-lived vs. long-lived token models. §7.4 FAQ updated. OI-001 and OI-002 marked Resolved. |
| 1.4 | 2026-05-12 | btan@netskope.com | Added US Cellular Corporation as second blocked customer in §2.3 Customer Voice. Updated §15 to name SIX Group and US Cellular as anchor Beta customers. |
| 1.5 | 2026-05-12 | btan@netskope.com | Applied review cleanup: removed internal authoring note from §8.6; updated §10 Custom CA/TLS row to Coming Soon (P1) with §8.6 pointer; replaced stale OI-001 reference in §13.1 with resolved spec pointers (§8.3, §8.6); added A9 TLS/HTTPS assumption to §5; added BR-016 cross-reference to §6.3 P1 alerts row. |
| 1.6 | 2026-05-12 | btan@netskope.com | Updated Appendix B: replaced TBD with confirmed docs.netskope.com/en/event-streaming-client URL and linked to §14.2 documentation update requirements. |
| 1.7 | 2026-05-12 | btan@netskope.com | Resolved OI-003 (PM decision): config view/edit exposed as new installer menu options `5. show_config` and `6. update_registry`, consistent with existing `update_client_key` pattern. Updated §9.1 installer menu, §9.2 and §9.3 entry points. OI-003 marked Resolved. |
| 1.8 | 2026-05-12 | btan@netskope.com | Updated OI-005: target installer/container version is Engineering's decision to propose; PM to confirm. Updated §15 accordingly. |

---

## 19. Appendices

### Appendix A: Demo / Reference Values

*No demo values defined yet.*

### Appendix B: Related Documents

| Document | Location | Description |
|----------|----------|-------------|
| Event Streaming Client Documentation | https://docs.netskope.com/en/event-streaming-client | Full ESC documentation hub — Requirements, Deployment, Configuration, Red Hat/Podman, Operations/Troubleshooting, FAQs, Architecture, API Access. All pages in this hub require updates for Artifactory support (see §14.2). |
