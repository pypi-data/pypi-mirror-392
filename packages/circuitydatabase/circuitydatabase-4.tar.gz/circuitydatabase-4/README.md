# circuitydatabase
Source for the Circuity Database designed to be distributed through PyPI.

# Installation instructions
```
python3 -m pip install circuitydatabase
```

# Running circuity from the command-line
```
% circuity --csv-path example/directory/data_file.csv --query 'justin age'
```

An example data file with basic information about tackle football players is available [here](https://drive.google.com/file/d/1EDxiKXJDzGPlb90zu5MsxMMr_VGLbn0Q/view?usp=share_link).

# Developer instructions
## Publishing new versions

```
% python3 -m build
% twine upload dist/*
```
