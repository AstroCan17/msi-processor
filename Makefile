.PHONY: data-sync install devcontainer-setup publish-dataset

install:
	pip install -e ".[dev]"

data-sync:
	FORCE_DATA_SYNC=1 bash .devcontainer/scripts/fetch-input-data.sh

devcontainer-setup: install data-sync

publish-dataset:
	@test -n "$(STORE_ROOT)" || (echo "Set STORE_ROOT=/path/to/store-root" && exit 1)
	bash .devcontainer/scripts/publish-dataset.sh "$(STORE_ROOT)"
