echo "[1 / 3] Setup environment..."
pip install -e .[dev]

echo "[2 / 3] Build API documentation..."
pdoc --docformat google ./afscgap -o website/devdocs/
[[ ! -f website/devdocs/afscgap.html ]] && exit 1

echo "[3 / 3] Build mkdocs..."
cp README.md docs/index.md
mkdocs build
[[ ! -f website/docs/index.html ]] && exit 1

exit 0
