# Panelyze

**Panelyze** is an interactive, spreadsheet-style DataFrame viewer for Python. Built on top of [itables](https://github.com/mwouts/itables) and [ipywidgets](https://ipywidgets.readthedocs.io/), it enables users to explore, filter, and inspect pandas DataFrames directly inside Jupyter Notebooks, Google Colab, or VS Code Notebooks — without writing filtering logic or switching to external tools.

---

## Key Features

- **Interactive DataFrame display** with scrollable, sortable, and searchable tables
- **Column-level filtering** via dropdowns or text input
- **Missing value inspector** for quickly isolating rows containing `NaN` values
- **Integrated column selector** with “Select All” toggle
- **Notebook-native interface**, optimized for JupyterLab, Google Colab, and VS Code
- **Zero configuration** — simply import and view your data

---

## Installation

Install from [PyPI](https://pypi.org/project/panelyze/):

```bash
pip install panelyze
```

---

## Usage

```python
from panelyze import panelyze
import pandas as pd

# Load your data
df = pd.read_csv("your_data.csv")

# Launch the interactive panel
panelyze(df)
```

Inspect, sort, filter, and explore your DataFrame directly within your notebook environment.

---

## Requirements

Panelyze depends on the following Python packages:

- [`pandas`](https://pypi.org/project/pandas/)
- [`itables`](https://pypi.org/project/itables/)
- [`ipywidgets`](https://pypi.org/project/ipywidgets/)
- [`IPython`](https://pypi.org/project/ipython/)

These will be installed automatically when using `pip`.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contributing

Contributions are welcome. Please open issues or submit pull requests to improve functionality, performance, or documentation.

---

## Related Projects

- [pandas-profiling](https://github.com/ydataai/pandas-profiling) — automated EDA for pandas
- [sweetviz](https://github.com/fbdesignpro/sweetviz) — visualized data comparison and exploration
- [itables](https://github.com/mwouts/itables) — interactive pandas tables via DataTables.js

---

Made with ❤️ for the data science community.