# Canny

`canny` takes lines from STDIN, allowing you to interactively select a value, which is then returned to STDOUT.

or in english:  
`canny` creates a clickable pane, based on the standard input.

![example_interaction](assets/example_interaction.gif)

* canny enables interactive filters in piped commands
* a unix-philosophy experiement
* brings the mouse to the cli :)
* a [fzf](https://github.com/junegunn/fzf) inspired tool


## Usage
**But, what does it do?**  
- By default, Canny looks for HTML tags (excluding semantics) and makes tag bodies clickable.
- If there are no tags in the text, every word will be tokenized and clickable.

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

## Installation
You can install `canny` from the PyPI repositories using the following command:
```
pip install --user canny
```
or check the realease page for a manual installation.

***NOTE***
only tested / written for linux

## Issues
Please report possible issues [here](https://github.com/Pieli/canny/issues). 

## License

This project is licensed under the [MIT License](LICENSE).

~ 🦝


