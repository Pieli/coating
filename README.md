# Canny
* canny enables interactive filters in piped commands
* A unix-philosophy experiement
* brings the mouse to the cli :)
* a [fzf](https://github.com/junegunn/fzf) inspired tool

(TODO insert gif here)

## Usage
What does it do?

Here are some examples, after the installation step [here](#Installaion)

This will open the selected file/directory of the current directory in vim.
```sh
vim $(ls -C | canny)
```

Another possible usage is this:
```sh
ls -C | canny | xargs xdg-open
```
This opens the selected file with it's standard application.

## Installation
```
pip install --user canny
```
or check the realease page for a manual installation.

***NOTE***
only tested / written for linux



~ 🦝

