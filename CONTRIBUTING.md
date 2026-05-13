# Contributing

To avoid committing large Jupyter Notebook outputs into the repository, run the following from the repository root before working with notebooks. This installs a Git filter that automatically strips notebook outputs on commit:

```bash
pip install nbstripout
nbstripout --install
```
