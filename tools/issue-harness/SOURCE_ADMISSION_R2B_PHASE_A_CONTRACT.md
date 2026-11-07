# Arca #13 — Source Admission R2B Phase A: fixed GET adapter

Status: **SOURCE_ONLY / LOCAL_UNCOMMITTED / NOT_ACTIVE / NO LIVE GITHUB READ**.
Baseline: `upiscium/ChatGPT-Skills@212fcd513c0fe9a5f6e374b4e17676ec3288f3f6`.
Reference design: `/tmp/arca-i13-r2b-d1-20261107/R2B_FIXED_GET_ADAPTER_D1_FINAL.md`,
operator-pinned SHA-256 `0659b2b4d46ec4fc4946881d5fee875fdde38163705a51751c96aa6b8b8ce331`.
Issue #13 stays open. This Phase A source cannot be treated as published, deployed or active.

## What this source implements

- **Fixed route only:** `GET https://api.github.com/repos/upiscium/ChatGPT-Skills/issues/13`, with exact repository spelling and no model-selected URL, redirect, alternate hostname, extra GET or authenticated fallback.
- **Pure injected evaluation:** `evaluate_injected_response(SyntheticHttpResponse | SyntheticTransportFailure)` interprets a synthetic HTTP event and accepts only a structurally valid non-PR Issue. Success is always `SYNTHETIC_PROVIDER_RESPONSE_UNBOUND`, *not* a real provider observation.
- **Defined but unused real GET function:** `run_fixed_real_get(operator_one_shot_allow=False)` defaults to `BLOCKED_LIVE_GATE_REQUIRED`; its concrete `http.client.HTTPSConnection` call is only entered if the explicit, non-authoritative local guard is set to `True`. This flag is **not Human approval**. Phase A tests may invoke this path only with monkeypatched fake connection classes, named `SIMULATED_REAL_PATH`; no live HTTP GET is authorized or performed here.
- **No bound result:** The closed `R2BStatus` enum supports synthetic unbound, operator-environment unbound, and deterministic `BLOCKED_*` statuses only. It has **no** `MATCH_UNATTESTED`, Host-source attestation or file-approval status. R2A's separate synthetic fixture result remains `SYNTHETIC_SOURCE_MATCH_NOT_PROVIDER_OBSERVED`.
- **No source snapshot/registry access:** R2B parses response metadata independently using R1 text restrictions and does not open/modify an R1 registry or source snapshot. There is no proof that Issue #13 currently has an actual staged R1 bundle. A successful later real GET would remain `OPERATOR_ENV_GITHUB_ISSUE_OBSERVED_UNBOUND`, not Source Admission.

The outer result includes Issue number, numeric ID, Node ID, UTC-seconds `updated_at`, and SHA-256 fingerprints of exact title/body/complete response bytes; it does not include title/body plaintext. Numeric ID and Node ID are observed, **not** independently pinned or authenticated. Source content, Human approval and effect authority are NOT verified.

Every result holds `origin_authenticated=false`, `human_approval_verified=false`,
`semantic_approval_verified=false`, `effect_authority=NONE`, and
`activation=NOT_ACTIVE_NOT_PUBLISHED`. The result is not a capability or
authorization token: a same-user Python process can monkeypatch the adapter,
access the private constructor sentinel or use object introspection. Real
operator-side TLS observations are not GitHub-signed or Host-attested evidence.

## Transport and deterministic failure behavior

- Python stdlib `http.client.HTTPSConnection` direct to `api.github.com:443`, no proxy API, no `set_tunnel`, no requests/httpx/gh, no token access or `Authorization` header. Sends fixed `Host`, `User-Agent`, `Accept`, `X-GitHub-Api-Version`, `Accept-Encoding: identity`. Unknown future API-version/media support is a **blocked response**, not permission to negotiate a fallback.
- SSL context built with `ssl.create_default_context()`; `check_hostname=True` and `verify_mode=ssl.CERT_REQUIRED` asserted. This still inherits the Adam process trust roots and `SSL_CERT_FILE` / `SSL_CERT_DIR` if set. A separately approved live canary must unset these variables in its isolated subprocess. Same-user OS trust remains spoofable.
- `http.client` automatically removes chunked transfer encoding. Only **transfer-decoded response-body bytes** are bounded, not raw wire bytes. Limit 1,048,576 bytes with bounded 8KiB `HTTPResponse.read1()` calls (rather than potentially long-blocking `read(n)` accumulation), `Content-Length` size check if present, no content decompression; reject missing/malformed JSON, duplicate keys, 64+ nesting, nonfinite numbers, invalid UTF-8, non-JSON MIME and content encoding other than absent/identity. Header count limited to 64, individual name/value lengths bounded, duplicate names case-insensitively rejected. An explicit Transfer-Encoding other than a single ASCII `chunked` token is rejected; `Transfer-Encoding` combined with `Content-Length` is rejected as ambiguous before reading the response body.
- Only HTTP **200** proceeds to Issue parsing. Presence of `pull_request` (including null) is rejected BEFORE required Issue fields. Positive Issue numeric ID, `I_` Node ID, exact 3 canonical URLs and `number=13`, state `open`, exact UTC timestamp, nonempty body, bounded UTF-8, R1 lexical source controls are enforced. No Unicode normalization, implicit revision/pin provenance or Human-approval inference.
- 304 -> NOT_FULL_RESPONSE, 3xx -> REDIRECT, 401 -> AUTH, 403 follows R2A precedence (Retry-After, then remaining-zero -> RATE_LIMIT, malformed remaining -> HTTP_STATUS, otherwise AUTH), 404/410 -> RESOURCE, 429 -> RATE_LIMIT, 5xx and DNS/connect/TLS/reset/timeout/partial read -> UNAVAILABLE, HTTP framing and malformed headers/body -> SCHEMA, other non-200 -> HTTP_STATUS. Errors are fail-closed and do not retry, switch credentials or use an operator-supplied source fallback.
- The socket timeout (3 seconds) is per blocking operation. `read1(n)` reduces unbounded accumulation in the **body** phase so best-effort monotonic checks can run between body reads, but `getaddrinfo`, `getresponse` / header `readline`, chunk-size parsing, and trailers can still dribble or block. **Only the future externally supervised GNU `timeout --signal=TERM --kill-after=2s 10s` process watchdog offers a whole-canary termination boundary**, approximately 10–12 seconds plus OS scheduling overhead; this is **not** a strict 10-second in-process guarantee. `watchdog_argv` only constructs argv; this module never executes subprocesses.

## Test and boundary verification

Phase A tests are **fully synthetic**, including the simulated concrete path:
- every test guards `HTTPSConnection`, `socket.create_connection`, `getaddrinfo`, socket `connect` / `connect_ex` / `sendto`, and `SSLContext.wrap_socket`, raising an uncaught `BaseException` sentry so accidental real networking **fails the test** rather than being reclassified as an expected transport BLOCKED status.
- fake connection records method, fixed hostname, route, headers, GET count, no Authorization, no redirect, no retry;
- fake `http.client.HTTPResponse` with chunked framing decodes bytes in memory, including a total decoded size above 1 MiB; `RawIOBase` dribble-socket test verifies the actual stdlib `read1` behaviour and its best-effort limit; reject ambiguous Transfer-Encoding/Content-Length framing and unsupported transfer-codings;
- status, malformed headers, Content-Length, oversize, malformed chunk, partial stream, DNS/TLS/cert/timeout, dribble and monotonic threshold cases;
- Issue/PR discrimination, schema/text/URL/identity validation, caller-supplied metadata not becoming trusted;
- unchanged R1/R2A/Core/MCP and exact 2 MCP read-only tools, including existing official MCP SDK v2 stdio tests.

The actual Plugin, Source Registry and production runtime are NOT touched. Use
isolated Python 3.12/3.13 test suites with automatic Plugin/source SHA inventory
before publication. Independent source/security review must evaluate exact bytes.

## Scope and stop conditions

**Phase A:** new operator-side source module, tests and contract only. No source
Commit, Push, PR, Ready/Merge, Release, Plugin update, Tunnel change, Source
activation, real GitHub GET, KAGARI/OpenCode Task or Issue mutation.

**Phase B:** separately authorized one-time unauthenticated public GitHub GET
with external watchdog, a separately controlled environment, actual read-only
operator evidence and **UNBOUND result only**. Failure is a stop, never a
silent fallback to the existing broad `gh` token.

**Later phases:** existing genuine R1 bundle one-snapshot loader, revision/alias
and OS ownership checks, possible independently administered Host identity,
Human approval evidence, deployment/publication and all write/effect actions
require independent design and Human authorization. Do not infer permission
from this Phase A source code or tests.
