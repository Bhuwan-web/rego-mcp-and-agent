- Define a `default decision` rule to handle unmatched inputs **only if not using chained else**; if using chained else, the final `else` clause serves as the default (no condition), so omit the `default` rule to avoid conflicts.
- Use the `if` keyword before the rule body for any non-default rule (e.g., `decision := ... if { <condition> }`).
- When writing membership checks, use `in` operator (e.g., `input.method in {"GET", "POST"}`).
- For negation, use the `not` keyword before the entire condition: do **not** write `x not in set`. Correct: `not x in set`. Example: `not input.method in {"GET", "POST"}`.
- **CRITICAL: Do not use the `or` keyword inside a rule body. OPA does not support inline `or` inside a single rule body.** Instead, define multiple rules with the same variable name to achieve OR logic (e.g., `russian_domain if { contains(input.host, ".ru") }` and `russian_domain if { contains(input.host, ".su") }`).
- **IMPORTANT**: Do **not** define multiple complete rules with the same variable name (e.g., two `decision := ...` rules). This creates an `eval_conflict_error`. Instead, chain conditions using the `else` keyword to enforce priority:
  ```
  decision := {"result": "deny", "detail": "blocked"} if {
      condition1
  } else := {"result": "allow", "detail": "allowed"} if {
      condition2
  } else := {"result": "allow", "detail": "default allow"}  # no condition—fallback
  ```
  The first condition that matches determines the output, and the final else (without condition) catches all remaining cases.
- **Order of else‑clauses matters:** Place overrides (e.g., special user‑agent exceptions) before general checks to ensure they are evaluated first.
- **Debugging tip:** If a condition unexpectedly fails, simplify the policy to directly output the input value (e.g., `my_field := input.request.method`) and test that. This helps verify the actual input structure.
- Test the policy with multiple inputs covering both allowed and denied cases to ensure correct behavior and no conflicts. When using the test tool, ensure `test_value` is a string like `"data.<package>.decision"` to avoid validation errors.
- The decision object must have `result` (one of allow/deny/warn) and `detail` (string explaining the decision). Optionally include other fields like `reason`.
- Policy package must be declared (e.g., `package httpapi`). The exact name depends on the problem, but the declaration is always required.
- **Time‑dependent policies:** When a policy compares against the current time (e.g., `time.now_ns()`), test inputs using only past dates can cause all cases to match the same branch (e.g., “allow”) regardless of the intended logic. Always include a mock input with a date **far in the future** (e.g., year 2100) to verify denial for recent items, and include a case where the relevant header is missing to trigger the default deny. This ensures all branches are exercised and the policy behaves correctly under varying absolute times.
- When making HTTP calls with `http.send`, always set `raise_error` to `false` and `force_cache` to `true` and `force_cache_duration_seconds` to `30` to prevent policy evaluation errors from transient network issues. And response from HTTP call is **not** same as response from PolicyInputSchema, It's generated on runtime and should be evaluated separately.
  - **Handling API responses:** When calling an external API via `http.send`, the response body is automatically parsed into an object if it is JSON. To access the raw JSON string (e.g., for `json.unmarshal` or other processing), use `raw_body` (e.g., `raw := response.raw_body`). This is necessary when the API returns a value that is not a JSON object/array but a primitive, or when you need to unmarshal a nested structure.
  - **Single vs array responses:** If the API returns a single object instead of an array (e.g., `{"version": ...}` rather than `[{"version": ...}]`), do not expect an array; directly access the fields. Ensure your policy logic handles both cases if necessary.
  - **URL encoding:** When constructing URLs with query parameters, use `urlquery.encode` (OPA built-in) to encode parameter values to avoid issues with special characters. Example: `url := sprintf("https://api.example.com/query?pkg=%v", [urlquery.encode(input.purl)])`.
  - **Check status code:** Always verify `response.status_code` before processing the body, and use the `status_code` to decide whether the response can be trusted.
- The `if` keyword is required for the body of every rule definition, including helper rules that compute intermediate values. Without it, the policy will fail to parse.
- **Avoid undefined functions:** Only use built-in OPA functions (e.g., `json.unmarshal`, `contains`, `startswith`, etc.). Using non-existent functions like `io.json.unmarshal` will cause a parse error. Always double-check function names against the OPA documentation.