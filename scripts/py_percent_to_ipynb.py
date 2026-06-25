"""Convierte un script .py en formato 'percent' (celdas '# %%') a un .ipynb.

Markdown: bloques que empiezan por '# %% [markdown]' (lineas siguientes con prefijo '# ').
Codigo:   el resto de bloques '# %%'.
"""
import sys
import nbformat as nbf

src = sys.argv[1]
dst = sys.argv[2] if len(sys.argv) > 2 else src.replace(".py", ".ipynb")

lines = open(src).read().splitlines()
cells, cur, is_md = [], [], False


def flush():
    if not cur:
        return
    body = "\n".join(cur).strip("\n")
    if not body.strip():
        return
    if is_md:
        md = "\n".join((l[2:] if l.startswith("# ") else l[1:] if l.startswith("#") else l) for l in cur)
        cells.append(nbf.v4.new_markdown_cell(md.strip("\n")))
    else:
        cells.append(nbf.v4.new_code_cell(body))


i = 0
while i < len(lines):
    line = lines[i]
    if line.startswith("# %%"):
        flush()
        cur, is_md = [], ("[markdown]" in line)
        i += 1
        continue
    cur.append(line)
    i += 1
flush()

nb = nbf.v4.new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, dst)
print(f"wrote {dst} · {len(cells)} celdas ({sum(c.cell_type=='markdown' for c in cells)} md / {sum(c.cell_type=='code' for c in cells)} code)")
