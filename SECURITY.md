# Security policy

## Supported versions

Security fixes are currently accepted for the latest version on the `main` branch. No release support window is defined yet.

## Reporting a vulnerability

Please do not disclose exploitable details in a public issue. Use the repository host’s private vulnerability reporting feature when available, or contact the maintainers privately through the address listed in the repository profile. Include affected files/versions, impact, and a safe reproduction. No response-time guarantee is currently published.

## Security notes

This project is a reference implementation and has no authentication, authorization, or tenant isolation. Do not expose it to untrusted users without a reviewed access-control design. Keep API keys outside source control, review provider handling of prompts and retrieved documents, and treat guardrails as defense-in-depth rather than a security boundary.

The checked-in document corpus includes third-party material whose redistribution rights have not been verified. Review rights before redistributing.

Pull requests run a Gitleaks history scan. Contributors should also use the hosting provider's secret scanning and push protection where available; a clean automated scan is not proof that no secret was ever exposed.
