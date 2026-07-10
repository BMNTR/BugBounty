---
name: bbp-business-logic
description: Specialized skill for identifying and exploiting business logic flaws, race conditions, and payment manipulation vulnerabilities.
---

# Business Logic & Race Condition Skill

This skill focuses on exploiting flaws in the application's intended logic rather than standard injection vectors.

## Workflow

### 1. Payment & Price Manipulation
- **Negative Values:** Change item quantities or prices to negative numbers (e.g., `price=-10.00`, `quantity=-5`). This might result in the application crediting the attacker's account.
- **Currency Mismatch:** If an item costs 100 USD, change the currency parameter to a cheaper currency (e.g., `currency=INR`) while keeping the amount 100.
- **Rounding Errors:** Exploit how the backend rounds fractions. Buy an item for $0.001 to see if it rounds down to $0.00 but still processes the transaction.

### 2. Race Conditions (Limit Overruns)
Exploit the gap between the time an application checks a condition (Time of Check) and the time it executes an action (Time of Use).
- **Target Areas:** Coupon redemption, fund transfers, voting, password resets, stock depletion.
- **Technique:** Send multiple identical requests simultaneously using tools like Turbo Intruder (Burp Suite) or custom Python scripts.
- **Goal:** E.g., Use a single-use $10 coupon 5 times simultaneously to get a $50 discount before the database updates the coupon status to "used".

### 3. State & Workflow Bypass
- **Skipping Steps:** Analyze multi-step processes (e.g., e-commerce checkout: `cart -> shipping -> payment -> confirmation`). Try accessing the `confirmation` endpoint directly without completing the `payment` step.
- **Parameter Tampering:** Identify hidden parameters (e.g., `is_admin=false`, `discount_applied=0`) and modify them.

### 4. Rate Limiting & Brute Force Evasion
- **Bypassing IP Bans:** Rotate IP addresses or use headers like `X-Forwarded-For: [random IP]`.
- **Null Byte Injection:** Append `%00` to usernames to create seemingly unique requests that resolve to the same user: `admin%00`.
- **Case Sensitivity:** If the application blocks `admin`, try `Admin` or `ADMIN`.
