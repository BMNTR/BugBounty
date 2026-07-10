---
name: bbp-prototype-pollution
description: Specialized skill for finding and exploiting Client-Side and Server-Side Prototype Pollution vulnerabilities in JavaScript/Node.js applications.
---

# Prototype Pollution Skill

This skill provides methodologies for attacking JavaScript applications by polluting the base object prototype (`Object.prototype`), leading to XSS, authentication bypass, or Remote Code Execution (RCE).

## Workflow

### 1. Identifying Injection Points
Prototype pollution typically occurs when an application recursively merges objects, clones objects, or parses query strings/JSON without properly sanitizing the keys.
- **Targets:** Search parameters in URLs (`?foo=bar`), JSON payloads in POST requests, or websocket messages.
- **Vulnerable Functions:** Look for usage of `merge()`, `clone()`, `extend()`, or libraries like `lodash` (older versions) in the source code or stack traces.

### 2. Testing for Client-Side Prototype Pollution
Attempt to inject properties into the global `Object.prototype` via the URL.
- **Payloads:**
  - `?__proto__[testprop]=testvalue`
  - `?constructor[prototype][testprop]=testvalue`
- **Verification:** Open the browser's developer console and type `Object.prototype.testprop` or just `testprop`. If it returns `"testvalue"`, the application is vulnerable.

### 3. Exploiting Client-Side Prototype Pollution (XSS)
Once polluted, you need to find a "gadget"—a piece of code in the application (or a library like Vue, React, or jQuery) that uses an undefined property from an object, which will now fall back to your polluted value.
- **Example Gadget (jQuery):** Older versions of jQuery might check `options.url`. If `options` doesn't have a `url` property, it reads from `Object.prototype.url`.
- **Exploit:** Inject `?__proto__[url]=javascript:alert(1)//` or `?__proto__[src]=data:,alert(1)//`. When the gadget fires, it executes the XSS payload.

### 4. Testing for Server-Side Prototype Pollution (Node.js)
This is much more dangerous as it affects the entire backend server for all users.
- **Payloads (JSON):** Send a POST request with:
  ```json
  {
    "__proto__": {
      "admin": true
    }
  }
  ```
- **Verification:** If the server returns a 500 error, or if subsequent requests act as if you are an admin (because `req.user.admin` now falls back to `true`), you have polluted the server. **WARNING:** Server-side pollution is often persistent and can easily crash the application (Denial of Service). Test with non-disruptive properties first.

### 5. Exploiting Server-Side Prototype Pollution (RCE)
If the Node.js server uses functions like `child_process.spawn()` or `fork()`, you can achieve RCE.
- **Gadget:** Node.js checks `options.env` or `options.shell`.
- **Exploit:** Pollute the environment variables:
  ```json
  {
    "__proto__": {
      "env": {
        "NODE_OPTIONS": "--require /proc/self/environ"
      }
    }
  }
  ```
