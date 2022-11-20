from pathlib import Path

import yaml


def create_data_file(obj: dict, folder: Path, replace: bool = False) -> Path:
    """The `folder` represents where the `data.yaml` file should be created. This is typically the parent path of the main files used to generate the model. If `replace` is `True`, update the data file if it already exists."""
    if not folder.is_dir():
        raise Exception("Use folder to create `data.yaml`.")
    data_file = folder / "data.yaml"
    if data_file.exists():
        if replace:
            data_file.unlink()
            with open(data_file, "w") as f:
                yaml.safe_dump(obj, f)
    else:
        with open(data_file, "w") as f:
            yaml.safe_dump(obj, f)
    return data_file
