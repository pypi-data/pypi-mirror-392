
DEFAULT_COMMIT_SPEC = """
- Commits consist of header, body and footer.
- Header contains type, optional scope and subject (50 characters max).
- Body is optional and provides additional contextual information.
- Footer is optional and can include breaking changes or issue references.
- Each line MUST be wrapped at 72 characters.

Header types: feat, fix, docs, style, refactor, test, chore
"""

for s in ["claude", "-p", "/commitaid", DEFAULT_COMMIT_SPEC]:
  print(s, end=" ")
