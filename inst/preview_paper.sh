[[ ! -f author-info-blocks.lua ]] && wget https://raw.githubusercontent.com/pandoc/lua-filters/master/author-info-blocks/author-info-blocks.lua
[[ ! -f scholarly-metadata.lua ]] && wget https://raw.githubusercontent.com/pandoc/lua-filters/master/scholarly-metadata/scholarly-metadata.lua

sudo apt-get update

sudo apt-get install pandoc pandoc-citeproc texlive-extra-utils texlive-fonts-recommended texlive-latex-base texlive-latex-extra

pandoc paper.md --bibliography=paper.bib --lua-filter=scholarly-metadata.lua --lua-filter=author-info-blocks.lua -o ../website/static/paper.pdf
