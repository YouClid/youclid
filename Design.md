# Design Decisions

## Users

### Reader

High level goals:
* See both text and visualization
* Easily tell which object in text corresponds to the object on screen
* See construction of visualization

Minimum Viable Product Story:

User opens a web page that has the text and visual side by side.
They can now step through animations of the visual as specified by the author.

### Writer

High level goals:
* Easy as possible to write
* Easily learnable
* Simple syntax
* Easy to read
* Can specify steps in which visual is drawn

Minimum Viable Product Story:

Write the markup language in their text editor. 
They can then compile this into a static html file, that they can view in their browser.

### Extra Ideas

Sorted by priority

* Change reading themes/colors
* Interact with picture, move points
* Side by side writing visual, for the writer (similar to sharelatex)
* Compiler is run once, and then watches the file, automatically recompiling on save as a mode.
* Color scheme for our markup in popular text editors
* Create the entire reading experience
  * links to next and previous texts
  * links to what this visualization uses


### Markup Syntax

Syntax Goals:
* Something to delineate where the markup is and where the text is.
* Something that is nice to write and look at

**Step specification**

Put some sort of flag at the top to say we'll do on eof 3 things:
1. Step for every declaration
2. No steps at all, just draw the whole thing
3. Specficified steps

#### Key decision

One character that surrounds all markup, we get to put whatever we like in between.
Chances are we have these declarations as space separated.


## Architecture

### Backend End

Written using some javascript variant for best flexibility.

It will take in some marked up text, output a static html page.

### Front End

Using THREE.js and WebGL to render the visuals. Other than that all vanilla js.

The backend puts everything into a set of CSS classes and ID's that can easily be styled with CSS.

## Process

As a team of 5 people, we will split into 2 teams, front end and back end. 
One person will float between teams, depending on which team needs more resources.

We will track things that need to be done using GitHub issues, marking priority items and assigning these issues.
