# merge-front-back

Command line program merge_front_back to merge two single-sided scanned PDFs into a duplex document.

Scan the odd pages first with your scanner.  Flip your stack of paper over and scan the even pages into a seperate document.  The pages will be scanned in reverse order.  

Use merge_front_back to interleave the pages into a propertly ordered PDF.

Instructions are available, run the command without arguments:

```powershell
merge_front_back  
```



## Installation

### For General Use

Install pipx if you don't already have it installed:  https://github.com/pypa/pipx.  On Windows you can use this to install pipx:
```powershell
winget install pipx
pipx ensurepath
```.  

Now install merge-front-back:

```bash
pipx install merge-front-back
```

### For Use in a Specific Python Enviornment 

This project uses Python packaging and is compatible with [uv](https://github.com/astral-sh/uv).  

For an editiable install:

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

To simply install in your current Python environment:
```bash
pip install merge-front-back
```