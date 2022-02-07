# substack-to-pdf
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


## TODO
 * Download assets like images
 * Cleanup code