<p align="center">
  <img src="https://github.com/Pieli/canny/blob/main/assets/canny_logo_small.png" />
</p>
<p align="center">
 <a href="https://github.com/Pieli/canny/actions/workflows/pylint.yml">
    <img src="https://github.com/Pieli/canny/actions/workflows/pylint.yml/badge.svg">
  </a>
 <a href="https://github.com/Pieli/canny/actions/workflows/python-publish.yml">
    <img src="https://github.com/Pieli/canny/actions/workflows/python-publish.yml/badge.svg?branch=main">
  </a>
</p>


`canny` creates a clickable pane, based on the standard input.

or more precise:  
  
`canny` reads lines from STDIN, allowing you to interactively select a value, which is then returned to STDOUT.

![example_interaction](assets/example_interaction.gif)

* canny enables interactive filters in piped commands
* a unix-philosophy experiment
* brings the mouse to the cli :)
* a fzf inspired tool
<p align="center">
  <img width=80% src="https://github.com/Pieli/canny/blob/main/assets/demo.gif" />
</p>


**But, what does it do?**  
- Every non-white space becomes a token
- Every token will be possible element for selection
- After a selection, the token will be returned through standard output

## Usage
Here are some examples, after the [installation step](#installation)  

This will open the selected file/directory of the current directory in vim:
```sh
vim $(ls -C | canny)
```

Another possible usage is this:
```sh
ls -C | canny | xargs xdg-open
```
This opens the selected file with it's standard application.

For more ways to use `canny` check out the `examples` directory.  

### Html Parser
- when run with the `--tags` flag, canny will look for HTML tags (excluding semantics) and makes tag bodies clickable.
- this function allows for a predefinition of clickable elements, in contrast to the default case, where every non-whitespace character is clickable
- if the tags are nested, only the highest level of tags is clickable
- in the case ther are no tags in the text, every word will be tokenized and clickable.

<p align="center">
  <img width=70% src="https://github.com/Pieli/canny/blob/main/assets/ice-cream.gif" />
</p>


## Installation
> [!Note]
> only tested / written for linux

You can install `canny` from the PyPI repositories using the following command:
```
pip install canny
```
or check the realease page for a manual installation.

on ubuntu first install ncurses-term:
```
apt install ncurses-term
```


## Issues

> [!Important]
> This tool currently supports python3.10 and upwards

On version with a python version lower than 3.10 the `curses.BUTTON5` constant is not supported.

Please report possible issues [here](https://github.com/Pieli/canny/issues). 

## License

This project is licensed under the [GPLv3 License](LICENSE).

---
Made with love by 🦝

