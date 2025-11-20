# securegen – Multi-Agent Secure Prompt CLI

`securegen` is a developer-first CLI that takes the *prompt* you would normally send to
an AI code generator, runs a multi-agent red-team/blue-team pipeline on it, and returns
a **more secure, rewritten prompt** plus an optional code preview.

You use it like this:

```bash
securegen "build a login API in python"
```

and it outputs:

- The original prompt
- Red-team security findings
- A final secure prompt
- A short secure code preview

This is perfect for demos and daily use in your coding workflow.
