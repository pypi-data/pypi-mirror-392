# Minimal makefile for Sphinx documentation
#
# This Makefile is compatible with Sphinx 3.4.2+ and Python 3.12+
# For installation: uv pip install -e ".[docs]"

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@if ! command -v $(SPHINXBUILD) > /dev/null 2>&1; then \
		echo "Error: 'sphinx-build' command not found."; \
		echo "Install Sphinx with: uv pip install -e \".[docs]\""; \
		echo "or visit: https://www.sphinx-doc.org/"; \
		exit 1; \
	fi
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@if ! command -v $(SPHINXBUILD) > /dev/null 2>&1; then \
		echo "Error: 'sphinx-build' command not found."; \
		echo "Install Sphinx with: uv pip install -e \".[docs]\""; \
		echo "or visit: https://www.sphinx-doc.org/"; \
		exit 1; \
	fi
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
