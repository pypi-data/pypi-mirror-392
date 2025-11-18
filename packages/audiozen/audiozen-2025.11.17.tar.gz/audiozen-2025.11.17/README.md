# AudioZEN

## Documentation

- [Release a new audiozen version](./docs/release.md)
- [How to manage data files](./docs/how_to_manage_data_files.md)
- [How to split the repo into read-only standalone repos?](./docs/how_to_distribute_monorepo.md)
- [How to manage experiment configurations](./docs/how_to_manage_exp_config.md)

## Prerequisites

```bash
# Install uv for speed up virtual environment creation and management
uv venv -p 3.12 venv/torch251_cu124_py312
source venv/torch251_cu124_py312/bin/activate

# Install the package
uv pip install -e .

# cd to the model directory
uv pip install -r /path/to/requirements.txt
```

## Prerequisites

```shell
rsync -avPxH --no-g --chmod=Dg+ /home/xhao/proj/audiozen xhao@10.21.4.91:/home/xhao/proj/audiozen --exclude="*.git" --exclude="*.egg-info" --exclude="*.egg" --exclude="*.pyc" --exclude="*.log" --exclude="*.npy"
```
