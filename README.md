# substack-to-pdf
This project isn't actively developed but if you have some use for it feel free to set up an
issue or PR.

## Usage:
```sh
pip install -r requirements
python main.py [Substack_URL]
```
Substack_URL must point to the main page eg. [https://forcoloredgirlswhotech.substack.com/]()

## Actually substack-to-epub, but:
```sh
sudo apt-get install pandoc
sudo apt-get install texlive-latex-base texlive-latex-extra
pandoc -o out.pdf input.epub
```
For conversion to .mobi use `calibre`.

