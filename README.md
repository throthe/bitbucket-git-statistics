# Bitbucket Git Statistics

## Notes

The tool is based on git-fame 2.0.1 and adjusted to make the inserted and deleted lines of code visible.

## How to run

* create virtual environment: ```python -m venv ./.venv```
* activagte virtual environment (Windows) ```.venv/Scripts/activate```
* install packages: ```python -m pip install -r requirements.txt```
* run statistics: ```python -m main```

# Git-Fame (in folder ./git-fame)

Github: https://github.com/casperdcl/git-fame/tree/main

## Commands for git-fame

```python -m git-fame.gitfame --loc=ins,del --cost hour -s --enum <REPOSITORY_PATH>```

```python -m git-fame.gitfame --loc=ins,del --cost hour -s --enum --format=yml --file=test.yml <REPOSITORY_PATH>```