# YouClid
### Geometric Notation for Everyone
#### Joseph Sweeney, Drew Monroe, Ian Dechene, Sailesh Simhadri, Soumya Kundu

### Dependencies
- python3

### Creating a Markup
The format for creating a markup file is specified in [yc-format.txt](https://raw.githubusercontent.com/YouClid/youclid/master/yc-format.txt).
In general, the text that should be interpreted by the parser must be enclosed in brackets, like so: `[line AB]`
The parser currently supports the following data types:
- point
- line
- circle
- polygon

Arguments to the data types are space separated.
The first argument to each data type must be the name of the object (which currently must be one letter point names that make up the object).
The `center` keyword can be used to specify the center point for a circle.
At the bottom of the file, the `loc` keyword must be used to give the points coordinates (floating point numbers between -1 and 1 inclusive), where `(0, 0)` is the center of the canvas.
To mark where this part of the document starts, it must be preceded by a `[Definitions]` tag.
We have provided an example file in [frontend/texts/postulate1.yc](https://raw.githubusercontent.com/YouClid/youclid/master/frontend/texts/postulate-1.yc) which can be used as a reference.

### Running the parser
To run the parser, which will generate HTML from your markup, simply run the following command, replacing the first argument with the path to your `.yc` file, and the argument to `-o` with the path to the `frontend` directory of this repository and then the name of the HTML file that you want to generate:
```
python3 main_parser.py /path/to/marked/up/yc/file -o /path/to/youclid/frontend/test.html
```
If you wish to specify transitions between steps in your text, simply include a \[step\] command.
Any objects created between \[step\] commands will be displayed as one transition.

### Step-by-Step Example
Let's say that you wish to create a diagonal line across the screen.
Start by making a file called `line.yc` with the following contents:
```
This text won't be marked up, since it's not enclosed in bracketes!
This is [line AB], which is made up of [point A] and [point B].

[definitions]
[loc A -0.75 -0.75]
[loc B 0.75 0.75]
```

The first line won't be interpreted by our parser, since it doesn't have any markup.
The second line will create a line named `AB`, which will consist of point `A` and point `B`.
While we do specify these points later on, they are implicitly created upon creation of line `AB`.
This means that you don't even need any of the text after the comma on the second line!
The lines after the blank line give the points locations.
Point `A` is given the coordinates `(-0.75, 0.75)` and point `B` is given the coordinates `(0.75, 0.75)`.

All that is left to do is generate the HTML.
Navigate to the `backend` directory and simply run the `main_parser.py` file as follows.
```
python3 main_parser.py /path/to/marked/up/yc/file -o /path/to/youclid/frontend/file.html
```
Now, you can open the HTML file in your browser, and you should see a line!

### Syntax Highlighting
We plan on creating syntax files for popular text editors.
Currently, the only syntax files we have created are for vim and atom.

#### Vim
In order to utilize the provided syntax files, create the following directory structure in your home directory (if it does not already exist) by running the following commands:
```
mkdir -p ~/.vim/ftdetect
mkdir -p ~/.vim/after/syntax
```
Next, run the following commands to create symlinks to our relevant syntax files, replacing the `/path/to/youclid` with the absolute path to the directory where you cloned our repository
```
ln -s /path/to/youclid/colors/.vim/ftdetect/yc.vim ~/.vim/ftdetect/yc.vim
ln -s /path/to/youclid/colors/.vim/after/syntax/yc.vim ~/.vim/after/syntax/yc.vim
```

The syntax file should pull colors from your vim color scheme.
If you wish to customize the colors, we utilize the following definitions:
- `YouclidKeyword`
- `YouclidMarker`
- `YouclidText`
- `YouclidName`

#### Atom
In order to utilize the provided syntax files, create the following directory structure in your home directory (if it does not exist) by running the following commands:
```
mkdir -p ~/.atom/packages
```
Next, run the following commands to create symlinks to our package, replacing `/path/to/youclid` with the absolute path to the directory where you cloned our repository
```
ln -s /path/to/youclid/colors/packages/language-youclid ~/.atom/packages/language-youclid
```
If you wish to customize the colors, [our `.less` file](https://raw.githubusercontent.com/YouClid/youclid/master/colors/language-youclid/styles/youclid.less) is located in `colors/language-youclid/styles/youclid.less`.
