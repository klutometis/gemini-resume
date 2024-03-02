# Gemini Resume

This is code for a workshop called
[Interview Prep with Bard](https://lu.ma/bardmeetup9) which shows off
multi-model plus function-calling capabilities in Gemini.

Given descriptions of the function-calls `search_jobs` and `search_leetcode`;
does the following:

1. Parses a PDF resume; and, based on the resume:
2. Calls `search_jobs` to find relevant, nearby jobs; and
3. Calls `search_leetcode` to find relevant practice problems.

The function-call spec looks something like this:

```python
search_leetcode_api = FunctionDeclaration(
    name="search_leetcode",
    description="Searches for LeetCode problems for a given job.",
    parameters={
        "type": "object",
        "properties": {
            "job_title": {"type": "string"},
        },
    },
)
```

and the resulting function-call:

```json
name: "search_leetcode"
args {
  fields {
    key: "job_title"
    value {
      string_value: "Software Architect"
    }
  }
}
```

In our case, we translate into Python and `exec` it; but you could imagine
crafting a `POST` or something similar.
