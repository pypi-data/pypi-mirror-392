#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <package1> [package2 ...]"
    echo "Beispiel: $0 ratisbona-utils ratisbona-shellutils ratisbona-pygames"
    exit 1
fi

# Konfigurierbar
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-$HOME/venvs/venv_testpypi}"

if [[ -e "${VENV_DIR}" ]]; then
    echo "Venvdir ${VENV_DIR} existiert. Lösche!"
    rm -rfv "${VENV_DIR}"
fi

echo "==> Erzeuge temporäres Verzeichnis für Wheels..."
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/testpypi_wheels.XXXXXX")"
echo "    TMP_DIR: $TMP_DIR"

echo "==> Lade deine Pakete von TestPyPI (ohne Dependencies)..."
# Hier läuft alles NOCH NICHT im neuen venv.
# Wir holen nur die Wheels deiner eigenen Pakete von TestPyPI.
"$PYTHON_BIN" -m pip download \
    --no-deps \
    --index-url https://test.pypi.org/simple \
    --extra-index-url https://pypi.org/simple \
    -d "$TMP_DIR" \
    "$@"

echo
echo "==> Erstelle frisches venv in: $VENV_DIR"
"$PYTHON_BIN" -m venv "$VENV_DIR"

# venv aktivieren (Linux/macOS)
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "==> Aktualisiere pip im venv..."
python -m pip install --upgrade pip

echo
echo "==> Installiere deine Wheels aus $TMP_DIR,"
echo "    Dependencies kommen dabei ausschließlich von PyPI Main..."
# Ganz wichtig:
# - KEIN TestPyPI hier!
# - Nur PyPI Main als Index
# - Deine Pakete kommen aus den bereits gedownloadeten Wheels
python -m pip install \
    --index-url https://pypi.org/simple \
    "$TMP_DIR"/*.whl

echo
echo "==> Aufräumen: lösche temporäres Wheel-Verzeichnis..."
rm -rf "$TMP_DIR"

echo
echo "Fertig ✅"
echo "Frisches venv: $VENV_DIR"
echo "Zum Aktivieren: source $VENV_DIR/bin/activate"

