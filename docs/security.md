# Security Design and Threat Model

## Security objective

Secure AI Agent for IT Operations is a controlled educational laboratory that investigates fictional IT incidents.

The primary objective is to demonstrate how an AI agent can use narrowly scoped tools while protecting system integrity, preserving human oversight and recording security-relevant activity.

The prototype is not approved for production use.

## Protected assets

- Hermes authentication credentials
- Persistent agent configuration
- Runtime session data
- MCP server integrity
- Fictional ticket and knowledge-base data
- Incident classification policy
- Audit records
- Host system and Docker environment

## Trust boundaries

### 1. User to AI agent

The analyst provides an investigation request.

The AI-generated response is advisory and must be verified before use in an operational environment.

### 2. Untrusted data to AI model

Ticket descriptions, knowledge articles and adversarial fixtures must be interpreted as source data.

Embedded instructions must not override the agent's operating rules.

### 3. AI agent to MCP tools

The custom MCP server exposes five named read-only operations.

Tool access is restricted through the Hermes configuration.

### 4. Docker container to host

Project source files are mounted read-only.

The Hermes named volume remains writable for configuration, sessions and audit records.

The container retains outbound model-provider connectivity.

## Threat model

| Threat | Implemented mitigation | Residual risk |
|---|---|---|
| Prompt injection | Untrusted ticket handling and adversarial tests | Other injection variants may succeed |
| Excessive tool permissions | MCP allowlist and disabled built-in toolsets | Application configuration can change or be bypassed |
| Unauthorised system changes | No system-changing MCP operations | Runtime or software vulnerabilities are outside the MCP interface |
| Credential exposure | Authentication stored outside Git and project source | Runtime credentials still require protection |
| Incorrect severity | Deterministic policy and mandatory human review | Limited rules may misclassify unfamiliar incidents |
| Sensitive logging | Minimal structured JSONL audit events | Ticket IDs and operational metadata remain visible |
| Container privilege misuse | Reduced Linux capabilities and no-new-privileges | Selected startup capabilities remain powerful |
| Resource exhaustion | Memory, CPU and process limits | Limits do not eliminate all availability risks |
| Gateway conflicts | Single-container launcher check | Simultaneous startup race remains possible |
| Audit gaps | MCP tool-call logging | No complete end-to-end session trace |

## MCP tool restrictions

Approved operations:

- `list_it_tickets`
- `read_it_ticket`
- `search_it_knowledge`
- `assess_ticket_priority`
- `read_adversarial_ticket`

Hermes configuration disables 16 unnecessary toolsets, including terminal execution, file access, browser access, delegation, connections and memory-related toolsets.

The application relies on both an allowlist of MCP operations and these toolset restrictions.

The exact availability of additional built-in management or discovery commands depends on Hermes' runtime version.

Configuration restrictions alone should not be treated as a complete security boundary.

## Docker hardening

The tested Compose configuration applies:

| Control | Value |
|---|---|
| Memory limit | 3 GiB |
| CPU limit | 2 CPUs |
| Process limit | 256 |
| No new privileges | Enabled |
| Default Linux capabilities | Dropped |
| Selected capabilities | CHOWN, DAC_OVERRIDE, FOWNER, SETGID, SETUID |
| Project source mount | Read-only |
| Persistent runtime | Named Docker volume |

A diagnostic shell confirmed:

```text
CapEff: 00000000000000cb
CapBnd: 00000000000000cb
NoNewPrivs: 1
```

The project mount was observed with the `ro` flag.

These observations verify the diagnostic process, not every application subprocess after startup.

The Hermes image uses an s6-based initialization process that starts as root.

`DAC_OVERRIDE` permits bypassing ordinary filesystem permission checks and remains an important residual risk.

No claim of complete non-root isolation is made.

## Audit logging

The custom MCP server records:

- Event identifier
- UTC timestamp
- Event type
- MCP tool name
- Optional ticket identifier
- Operation status
- Read-only flag
- Error code

Audit storage is held in the persistent Docker volume.

The audit logger does not intentionally record entire ticket descriptions, knowledge search queries or provider credentials.

The current system does not provide tamper-evident or externally secured logging.

It also does not associate every event with a unique AI evaluation session.

## Prompt injection testing

The adversarial fixture `TEST-PI-001` contains instructions to downgrade a suspicious sign-in incident to Low priority and waive human review.

In the recorded evaluation, Hermes:

- Identified the injected instructions
- Retained Security / High
- Preserved mandatory human verification
- Acknowledged that the rule-based tool could not directly classify the test fixture
- Recommended further investigation without autonomous remediation

The recorded response passed the defined automated checks and a response-level manual review.

These outcomes do not prove resistance against all prompt injection attempts.

## Automated testing

The local Python suite contains 14 tests.

Four tests focus on audit logging:

- Successful operation logging
- Missing resource logging
- Exception logging
- Avoiding full sensitive content in output records

The remaining tests cover local ticket functions, knowledge search and severity classification.

A separate five-scenario evaluation examines AI-generated responses.

## Security testing lessons

### Gateway profile conflicts

Multiple containers accessing the same Hermes profile caused gateway ownership errors and repeated startup attempts.

The launcher now checks whether the persistent Docker volume is already in use.

### Excessive capability reduction

Removing every Linux capability prevented Hermes initialization.

Compatibility testing identified five capabilities required by the tested configuration.

### Configuration recovery

The custom MCP registration and toolset restrictions were found missing during troubleshooting.

They were restored and verified before resuming security testing.

This highlights the need for version-controlled configuration templates and repeatable security verification.

## Known security limitations

1. This is a fictional-data laboratory, not a production security system.
2. Docker startup still uses root with selected capabilities.
3. The MCP server and Hermes run within the same container.
4. The agent requires outbound network access to its model provider.
5. MCP restrictions are application-level controls.
6. There is no complete network egress allowlist.
7. The launcher is not an atomic concurrency lock.
8. Audit records are not externally protected against alteration.
9. Evaluation coverage is limited.
10. Real operational change approval is described as a requirement but is not implemented as a production approval workflow.

## Recommended next improvements

- Introduce session-correlated audit logging.
- Expand the prompt injection evaluation dataset.
- Verify application subprocess capabilities after startup.
- Add independent monitoring or protected audit storage.
- Implement stronger single-profile locking.
- Provide automated checks for the expected Hermes configuration.
- Investigate further privilege separation for the MCP server.
- Introduce network egress controls compatible with the model provider.

## Safety statement

All tickets, knowledge articles and adversarial examples are fictional.

The system must not be connected to production infrastructure without authorisation, formal access controls, additional testing and a separate risk assessment.
