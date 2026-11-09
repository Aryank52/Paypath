# PayPath Confidential Computing & TEE Evaluation

## Overview & Motivation
As an AI-driven agentic payment platform, PayPath handles high-value commerce decisions and sensitive merchant dispute policies. This evaluation examines the feasibility, architectural fit, and deployment strategy for **Trusted Execution Environments (TEEs)** and **Confidential Computing** (e.g. AWS Nitro Enclaves, GCP Confidential VMs, AMD SEV-SNP, Intel SGX).

---

## 1. Candidate Workloads for TEE Isolation

### A. PayCore Cryptographic Key & Secret Management (High Priority)
- **Problem**: PayPal client secrets and webhook signature keys in memory could be exposed to root compromises on the host OS.
- **TEE Solution**: Execute PayCore's signing and token acquisition inside a hardware-isolated enclave. Even hypervisor administrators cannot inspect enclave memory.

### B. Autonomous Spending & Policy Constraint Verification (High Priority)
- **Problem**: Compromised infrastructure could theoretically alter deterministic policy engine thresholds (e.g., changing autonomous limit from $250.00 to $10,000.00).
- **TEE Solution**: Run the policy verification rules inside an attested enclave, producing a cryptographic attestation token verifying that the policy decision ran unmodified.

### C. Multi-Merchant Private Policy RAG (Medium Priority)
- **Problem**: Merchants sharing a platform want mathematical proof that proprietary dispute allowances never leak across tenants.
- **TEE Solution**: Index and search embeddings inside confidential memory.

---

## 2. Platform Trade-Off Analysis
| Dimension | Standard Container (Current) | Confidential VM (GCP/AWS) | Hardware Enclave (Nitro / SGX) |
| :--- | :--- | :--- | :--- |
| **Development Complexity** | Low (FastAPI + Docker) | Low (Lift-and-shift) | High (Requires custom enclave bridge) |
| **Performance Overhead** | None | 2% – 5% CPU penalty | Variable (I/O proxying across enclave) |
| **Memory Isolation** | Software container namespaces | Full memory encryption via AMD SEV | Strict enclave cryptographic boundary |
| **Hackathon Feasibility** | **Immediate (Active)** | Ready for cloud deploy | Post-hackathon enterprise tier |

---

## 3. Recommendation & Roadmap
1. **Current Phase**: Enforce software-level defense-in-depth (PostgreSQL row-level isolation, strict RBAC, MFA, input sanitization).
2. **Next Enterprise Milestone**: Deploy PayPath ASGI backend to GCP Confidential VMs with AMD SEV-SNP memory encryption enabled via simple infrastructure-as-code flag.
3. **Phase 3**: Package PayCore signing service as an independent enclave microservice.

