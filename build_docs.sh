echo "[1 / 3] Setup environment..."
pip install -e .[dev]

echo "[2 / 3] Build API documentation..."
pdoc --docformat google ./afscgap -o website/devdocs/
[[ ! -f website/devdocs/afscgap.html ]] && exit 1

echo "[3 / 3] Build paper preview..."
cd inst
bash preview_paper.sh
[[ ! -f ../website/static/paper.pdf ]] && exit 1
cd ..
