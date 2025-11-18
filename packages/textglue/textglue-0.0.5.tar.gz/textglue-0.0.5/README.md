# textglue

### Text Glue
### An extremely simple text based static templating system

## Commands
 
  - textglue init - creates a minimal starter project.
  - textglue demo - creates a more complex demonstration project.
  - textglue render - builds the project.

## About

textglue supports only two tags:

    {{file:_body.html}} {{template:_body.html}}

The "file" tag includes the raw source of the file, while
the template tag recursively evaluates the file as another
template. By default, the maximum recurse depth for
templates is 8.

Files with an
underscore prefix are ignored unless used in a template.
Files with a ".html" extension are rendered as a template,
and files without an underscore prefix or ".html" extension,
are directly copied to the output folder.

The textglue.json file lets you configure a source directory "src",
an output folder "out", as well as the prefix for which files to
ignore when rendering

Be careful!

The default input and output folders are "src" and
the current directory ".". If the output is not the
working directory, and the source and output folders are
different, then 'textglue render' will delete the output folder
every build.
