# Roadmap

## 🌐 Server-Side Features & the Custom Server Roadmap

The official **Wand Remote mobile application** (and any other feature that depends on Wand's backend validating an active subscription) **will not work** with a local patch alone. These features require a real server-side Pro entitlement.

**Can server-based features be supported?**  
Yes — but it requires infrastructure beyond a local file patch:

1. A **custom server** that emulates Wand's API subscription-validation endpoints closely enough for the desktop client to accept a Pro state.
2. Patching or proxying the **Wand mobile application** so it communicates with that custom server instead of Wand's production backend.

This involves ongoing hosting and maintenance costs. I can only commit to it if there is enough demand.

**If the number of requests reaches a sufficient level**, I can offer server-based Pro features as a **low-cost subscription — likely around $15 USD per year**.

**How to request it:**  
**Contact me directly** or **open a feature-request issue** on the repository. Include the specific server-side feature you need and how often you would use it. Demand is tracked from those requests.

---
