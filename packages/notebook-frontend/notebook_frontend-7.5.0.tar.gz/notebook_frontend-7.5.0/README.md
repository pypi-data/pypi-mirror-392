# notebook-frontend

A Python package distributing Notebook's static assets only, with no Python dependency.

```bash
git clean -fdx
curl --output notebook-7.5.0-py3-none-any.whl https://files.pythonhosted.org/packages/73/96/00df2a4760f10f5af0f45c4955573cae6189931f9a30265a35865f8c1031/notebook-7.5.0-py3-none-any.whl
unzip notebook-7.5.0-py3-none-any.whl
mkdir -p share
cp -r notebook-7.5.0.data/data/share/jupyter share/
cp -r notebook/static src/notebook_frontend/
cp -r notebook/templates src/notebook_frontend/
hatch build
hatch publish
```
