echo "[1 / 2] Build API documentation..."
pdoc --docformat google ./afscgap -o website/devdocs/
[[ ! -f website/devdocs/afscgap.html ]] && exit 1

echo "[2 / 2] Build paper preview..."
cd inst
bash preview_paper.sh
[[ ! -f ../website/static/paper.pdf ]] && exit 1
cd ..
