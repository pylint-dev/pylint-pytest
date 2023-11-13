---
name: Bug report
about: Create a report to help us improve
title: ''
labels: bug
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Package versions

<!-- e.g., get them by running
pip list |& grep -E '\b(pylint|pytest|pylint-pytest)\b' | sed 's/^/* /'
-->

* pylint:
* pytest:
* pylint-pytest:

(add any relevant pylint/pytest plugin here)

Folder structure
```console
$ tree -L 2

```

File content
```python
```

pylint output with the plugin
```bash
```

(Optional) pytest output from fixture collection
```bash
$ pytest --fixtures --collect-only <path/to/test/module.py>
<paste output here, can omit the built-ins>
```

**Expected behavior**
A clear and concise description of what you expected to happen.

**Additional context**
Add any other context about the problem here.
