# Risk Table

| Risk                  | Mitigation Strategy                                       |
|-----------------------|-----------------------------------------------------------|
| Selector-Drift        | Implement hash-based diffing on key selectors.            |
| Proxy Outage          | Use a resilient proxy pool with automated rotation.       |
| Cost Creep            | Set hard limits on token and cloud spend with alerts.     |
| Secret Echo           | Ensure all script outputs redact sensitive information.   |
| Secrets Leak          | Store secrets in a secure vault (e.g., GitHub Secrets).   |
