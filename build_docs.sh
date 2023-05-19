echo "[1 / 4] Setup environment..."
pip install -e .[dev]

echo "[2 / 4] Build API documentation..."
pdoc --docformat google ./afscgap -o website/devdocs/
[[ ! -f website/devdocs/afscgap.html ]] && exit 1

echo "[3 / 4] Build paper preview..."
cd inst
bash preview_paper.sh
[[ ! -f ../website/static/paper.pdf ]] && exit 1
cd ..

echo "[4 / 4] Build mkdocs..."
cp README.md docs/index.md
mkdocs build
[[ ! -f website/docs/index.html ]] && exit 1

exit 0
