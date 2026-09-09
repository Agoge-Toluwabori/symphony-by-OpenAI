# Runtime verification

The original network-disabled native profile denied Node socket buffer/shutdown
operations; captured subprocess output was empty with EPERM. Inherited/ignored
stdio worked. Python socketpair alone worked, but SO_RCVBUF/SO_SNDBUF and shutdown
were denied. The host harmless Node trace confirmed these are its pipe operations.

The corrected managed native proxy uses an empty destination allowlist and an
isolated network namespace. Native tests prove no external route, different network
namespace, explicit proxy HTTP 403 for prohibited destinations, stable non-root
real/effective/saved UIDs, and denied credential/unrelated-repository access.
Node captured output works. Full pnpm check:ci passes, including Playwright against
loopback; NO_PROXY contains only loopback entries. No public listener is created.

A real credential-free isolated npm fetch of is-number@7.0.0 passed. Manifests were
stripped of lifecycle scripts and worker configuration, Git/SSH were unavailable,
and the resolver proxy permits only registry.npmjs.org:443. No paid resource used.

Governance PR #237 tested commit f1b811a8599fd02b113d749ea48b0768fadef73c.
GitHub recorded agoge-factory/ci success. Its pre-existing Vercel integration posted
a failed Vercel status automatically. No Vercel command/API/configuration was used;
provider status is outside the owner-defined GitHub acceptance boundary.
