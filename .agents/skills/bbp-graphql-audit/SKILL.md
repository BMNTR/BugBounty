---
name: bbp-graphql-audit
description: Specialized skill for auditing GraphQL APIs, including introspection, query batching, and mutation exploitation.
---

# GraphQL Audit Skill

This skill provides methodologies for attacking modern APIs built with GraphQL.

## Workflow

### 1. Discovery & Introspection
- Identify GraphQL endpoints (typically `/graphql`, `/api/graphql`, `/v1/graphql`).
- Attempt to run an Introspection query to map the entire API schema.
- **Payload:** `{"query": "{ __schema { types { name fields { name } } } }"}`
- If introspection is disabled, use tools like `clairvoyance` to brute-force the schema based on error messages (e.g., "Did you mean 'user'?").

### 2. Information Disclosure (InQL)
- Analyze the extracted schema using tools like InQL (Burp Suite extension) or GraphQL Voyager to visualize relationships.
- Look for hidden queries or mutations that are not exposed in the client UI (e.g., `getInternalStats`, `deleteUser`).

### 3. Denial of Service (DoS) via Complex Queries
- **Deep Nesting:** If the schema has circular relationships (e.g., `Author -> Post -> Author -> Post`), craft deeply nested queries to exhaust server resources.
- **Alias Batching:** Use aliases to request the same expensive query multiple times in a single request.
  ```graphql
  query {
    q1: expensiveQuery(id: 1) { data }
    q2: expensiveQuery(id: 2) { data }
    ...
  }
  ```

### 4. Rate Limit & Authorization Bypass
- **Alias-Based Rate Limit Evasion:** If the server limits login attempts to 5 per minute, use aliases to send 100 login attempts in a single request.
- **IDOR in GraphQL:** Test every query and mutation that takes an ID as an argument. Check if you can query or modify data belonging to other users.

### 5. Mutation Exploitation
- Examine all available mutations (operations that modify data).
- Test for mass assignment vulnerabilities by passing unexpected arguments to mutations (e.g., adding `isAdmin: true` to an `updateProfile` mutation).
