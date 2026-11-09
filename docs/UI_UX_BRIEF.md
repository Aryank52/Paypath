# PayPath — UI/UX Design Brief & Guidelines

## 1. Visual Philosophy: Fintech Precision & AI Clarity
PayPath is an AI transaction command platform for financial professionals and intelligent consumers. The interface rejects generic AI clutter (gimmicky 3D shapes, oversaturated gradients, meaningless animated particle backgrounds) in favor of:
- **Clean Neutral Slate:** Crisp slate/zinc backgrounds (`#090d16` dark / `#f8fafc` light) with high-contrast typography.
- **Fintech Accent Palette:** Electric emerald (`#10b981`) for verified transactions, crisp amber (`#f59e0b`) for review/approval gates, vibrant rose (`#ef4444`) for blocked/high risk, and refined indigo (`#6366f1`) for AI orchestration.
- **Micro-Interactions & Restrained Motion:** Subtle status indicator pulses, smooth drawer transitions, and responsive hover elevations.

## 2. Core Screens & Navigation

### 1. Dashboard Overview
- **Key Metrics:** Total Volume, Attention Required, Active Safeguards, Pending Approvals, Verified Recoveries.
- **Quick Action Bar:** "Ask PayPath AI", "New Guarded Purchase", "Submit Return/Claim".
- **Recent Transaction Feed & Anomalies.**

### 2. Transaction Intelligence Explorer (AG Grid)
- **Grid Features:** Full-text search, column grouping by merchant/risk, status filtering, date range pickers.
- **Custom Renderers:**
  - Status Pill: `CAPTURED`, `PENDING`, `REFUNDED`, `VERIFIED`.
  - Risk Level: `LOW`, `MEDIUM`, `HIGH` with visual badges.
  - AI Insight: One-line concise summary of the transaction's health.
  - Quick Actions: One-click "View Lifecycle", "Report Issue", "Analyze Policy".

### 3. RECLAIM Resolution Center
- **Split View Layout:**
  - Left Panel: Dispute Details, Evidence Uploader (drag-and-drop images/receipts), and Policy Citations.
  - Right Panel: AI Resolution Proposal, Confidence Meter (e.g. 94%), Policy Grounding Summary, and Approval Gateway with explicit "Approve Refund", "Request More Info", "Escalate" controls.

### 4. Payment Guard Studio
- Visual rule builder for user spending limits, merchant whitelists/blacklists, and approval thresholds.
- Transaction simulation sandbox: Test how a prospective purchase would be evaluated by the Guard engine.

### 5. AI Command Center
- Conversational drawer / modal accessible from any screen with keyboard shortcut (`Cmd/Ctrl + K`).
- Quick prompts: *"Find unusual charges this week"*, *"Why was payment #384 flagged?"*, *"Show pending refund approvals"*.

### 6. Merchant & Policy Center
- Document uploader with real-time chunk preview and rule extraction editor.
- Version history table and policy simulation workbench.

