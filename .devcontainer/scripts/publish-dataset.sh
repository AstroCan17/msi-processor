#!/usr/bin/env bash
set -euo pipefail
SOURCE_DIR="${1:-}"
DATA_REPO_OWNER="${DATA_REPO_OWNER:-AstroCan17}"
DATA_REPO_NAME="${DATA_REPO_NAME:-ipf-data}"
DATASET_TAG="${DATASET_TAG:-datasets-msi-v1}"
DATASET_ASSET_NAME="${DATASET_ASSET_NAME:-input-data.tar.gz}"
GITHUB_MAX_BYTES=$((2 * 1024 * 1024 * 1024))
[[ -n "${SOURCE_DIR}" && -d "${SOURCE_DIR}" ]] || { echo "Usage: publish-dataset.sh <store-root>"; exit 1; }
TMP_DIR="$(mktemp -d)"; trap 'rm -rf "${TMP_DIR}"' EXIT
ARCHIVE="${TMP_DIR}/${DATASET_ASSET_NAME}"
tar -czf "${ARCHIVE}" -C "${SOURCE_DIR}" .
( cd "${TMP_DIR}" && sha256sum "${DATASET_ASSET_NAME}" > "${DATASET_ASSET_NAME}.sha256" )
(( $(stat -c%s "${ARCHIVE}") <= GITHUB_MAX_BYTES )) || { echo "ERROR: archive > 2 GiB"; exit 1; }
if gh release view "${DATASET_TAG}" --repo "${DATA_REPO_OWNER}/${DATA_REPO_NAME}" >/dev/null 2>&1; then
  gh release upload "${DATASET_TAG}" "${ARCHIVE}" "${TMP_DIR}/${DATASET_ASSET_NAME}.sha256" --repo "${DATA_REPO_OWNER}/${DATA_REPO_NAME}" --clobber
else
  gh release create "${DATASET_TAG}" "${ARCHIVE}" "${TMP_DIR}/${DATASET_ASSET_NAME}.sha256" --repo "${DATA_REPO_OWNER}/${DATA_REPO_NAME}" --title "Dataset ${DATASET_TAG}"
fi
