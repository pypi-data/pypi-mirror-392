#!/usr/bin/env python3
import os, shutil
import re
import sys
import json
from pathlib import Path

defaultSrcFolder = 'src'
workingDir = "."
defaultOutFolder = "."
configFile = "textglue.json"

# config
ignorePrefix = "_"
srcFolder = defaultSrcFolder
outFolder = defaultOutFolder

def getTemplateRegex(ignorePrefix):
  return f"((?!{ignorePrefix})[^/]*)\\.glue"

def getFileRegex(ignorePrefix):
  return f"(?!{ignorePrefix})[^/]*" 


def __safeRead(folder, file, result = "", verbose=True):
  try:
    path1 = os.path.join(folder, file)
    norm1 = os.path.normpath(path1)
    if folder != "." and not norm1.startswith(os.path.normpath(folder)):
      print(f"   [Warning]:  path out of bounds: \"{norm1}\" not in \"{folder}\"")
      return result
    with open(norm1) as f:
      result = f.read()
    return result
  except:
    if verbose:
      print(f"Error loading file '{norm1}'")
    return result

def readConfig():
  src = __safeRead(".", configFile, "", False)
  if not src or len(src) == 0:
    print("config not read from textglue.json")
    return
  config = json.loads(src)
  global ignorePrefix
  global srcFolder
  global outFolder
  if "src" in config:
    srcFolder = config.get("src")
  if "out" in config:
    outFolder = config.get("out")
  if "ignorePrefix" in config:
    ignorePrefix = config.get("ignorePrefix")


# by default, render all html files not start with 
def renderFolder(
    template_pattern = getTemplateRegex(ignorePrefix), file_pattern = getFileRegex(ignorePrefix)):
  print(f"\n\nRendering template folder \"{srcFolder}\" to \"{outFolder}\"")
  copyout = srcFolder != outFolder
  if copyout and outFolder != workingDir:
    try: 
      shutil.rmtree(outFolder)
    except:
      print(f"Creating output folder \"{outFolder}\"")
    os.mkdir(outFolder)

  for (root, dirs, files) in os.walk(srcFolder):
    subfolder = root[len(srcFolder )+1:]
    if len(subfolder) > 0 and subfolder[0] == '/':
      subfolder = subfolder[1:]
    for file in files:
      is_template = template_match = re.match(template_pattern, file)
      is_normalfile = re.match(file_pattern, file)
      short_file = file
      if is_template:
        short_file = template_match[1]

      if not is_template and is_normalfile and copyout:
        print()
        print("============ Static File: " + os.path.join(subfolder, file) + " ============")
        if subfolder != "." and len(subfolder) > 0:
          try:
            os.mkdir(os.path.join(outFolder, subfolder))
          except:
            print("Cannot make directory: " + os.path.join(outFolder, subfolder))

        fromPath = os.path.join(srcFolder, subfolder, file)
        toPath = os.path.join(outFolder, subfolder, short_file)
        toFolder = os.path.join(outFolder, subfolder)
        #print("from: " + fromPath, srcFolder, subfolder)
        try:
          os.mkdir(toFolder)
        except:
          pass

        shutil.copyfile(fromPath, toPath)
        continue
        
      if is_template:
        print()
        print("Template: " + os.path.join(subfolder, file))
        print("====================================================")
        if copyout:
          try:
            os.mkdir(os.path.join(outFolder, subfolder))
          except:
            pass
        outPath = os.path.join(outFolder, subfolder, short_file)
        readPath = os.path.join(srcFolder, subfolder, file)
        txt = ""
        # print("   read path: ", readPath)
        # print("  write path: ", outPath)
        #try:
        with open(readPath, 'r') as f:
            src = f.read()
            txt = genTemplate(srcFolder, subfolder, src)
            lines = txt.split("\n")
            n = min(len(lines), 5)
            print(f"\n  Preview ({n}/{len(lines)} Lines):")
            for i in range(n):
              print(f"    {i+1}-  {lines[i]}")
            with open(outPath, 'w') as f2:
              f2.write(txt)
        #except:
        #  print('cannot read file')
          

def parseArgs(s):
    args = {}
    argn = 1
    j = 0
    name = ""
    i = 0
    while i <= len(s):
        ch = s[i] if i < len(s) else " "
        if ch == "\"" or ch == "'":
            i += 1
            if i >= len(s):
                raise ValueError(f"Mismatched quote {ch}, for input:\n> {s}")
            while s[i] != ch:
                if s[i] == "\\":
                    i += 1
                i += 1
                if i >= len(s):
                    raise ValueError(f"Mismatched quote {ch}, for input:\n> {s}")

        if ch == ":":
            name = s[j:i]
            if len(name) == 0:
                raise ValueError("Expected argument name, for input:\n> {s}")
            j = i + 1

        if ch == " ":
            if j == i:
                j += 1
            else:
                token = s[j:i]
                # remove quotes if they wrap the entire string.
                if len(token) == 0:
                    raise ValueError(f"Empty token value for input[{i}:{j}]:\n> [{s}]")
                if (token[0] == token[-1] == "\"" or
                    token[0] == token[-1] == "'"):
                    token = token[1:-1]
                # unnamed args are numbered.
                if len(name) == 0:
                    name = str(argn)
                    argn += 1
                print(f"arg {name}:'{token}'")
                args[name] = token
                name = ""
                j = i + 1

        i += 1

    return args

        
# There are two tags {{template:path args}} and {{file:path}}
# The template tag recursively includes another template.
# The file tag inserts the raw file unmodified.
# both add indents to every line, if the colon separator is used,
# or without indents if the pipe separator {{template|name}} is used.
# generates a page from the src
def genTemplate(topfolder, subfolder, src, recurse=8, args={}):

    if recurse == 0:
        return ""
    i = 0
    result = ""
    pattern = re.compile("{{\\$([_A-Za-z0-9]*)}}")
    matches = pattern.finditer(src)
    for match in matches:
        name = match[1]
        result += src[i:match.start()]

        value = match[0]
        if name in args:
            value = args[name]
        result += value

        i = match.end()

    result += src[i:]
    src = result
    result = ""


    i = 0
    pattern = re.compile("(\n|^)(\\s*)(.*?){{template(:|\\|)([^} ]*)([^}]*)}}")
    matches = pattern.finditer(src)

    for match in matches:
        lastline = match[1]
        indent = match[2]
        prefix = match[3]
        pipe = match[4]
        filepath = match[5]
        args = match[6]
        result += src[i:match.start()]
        if recurse > 1:
          argv = parseArgs(args) if len(args) > 0 else {}
          content = genPageFile(topfolder, subfolder, filepath, recurse - 1, argv)
          if pipe == ":":
            content = content.strip()
            content = "\n".join([indent + s
              for s in content.split("\n")])
            content = content.strip()
            result += lastline + indent
          else:
            result += lastline
          result += prefix + content
        i = match.end()
        #result += I
    result += src[i:]
    # reset src to evaluate "file" tags.
    src = result
    # return result
    result = ""
    i = 0
    pattern = re.compile("(\n|^)(\\s*)(.*?){{file(:|\\|)([^}]*)}}")
    matches = pattern.finditer(src)
    for match in matches:
        lastline = match[1]
        indent = match[2]
        prefix = match[3]
        pipe = match[4]
        filepath = os.path.join(subfolder, match[5])
        result += src[i:match.start()]
        # print('file tag', topfolder, filepath)
        content = __safeRead(topfolder, filepath, "")
        # print('content', content)
        if pipe == ":":
          content = content.strip()
          content = "\n".join([indent + s
            for s in content.split("\n")])
          content = content.strip()
          result += lastline + indent
        else:
          result += lastline
        result += prefix + content
        i = match.end()

    result += src[i:]
    return result


def genPageFile(topfolder, subfolder, file1, recurse=8, args={}):
    filepath = file1.split("/")
    file2 = filepath[-1]
    newsubfolder = os.path.normpath(os.path.join(subfolder, "/".join(filepath[:-1])))
    norm1 = os.path.normpath(os.path.join(topfolder, newsubfolder))
    if not norm1.startswith(topfolder):
      print('folder out of scope: ' + norm1)
    
    src = __safeRead(norm1, file2, "")
    if src == None:
      return ""
    return genTemplate(topfolder, newsubfolder, src, recurse, args)

default_config = """
{
  "info": "TextGlue project. Use command 'textglue render' to build",
  "src": "src",
  "out": ".",
  "ignorePrefix": "_"
}
"""

demo_href = """<a href="{{$url}}">{{$name}}</a>"""

demo_index = """
<!doctype html>
<html>
  <head>
    <title>{{file:html/_name.html}}</title>
    {{file:html/_viewport.html}}
    <style>
      {{file:css/_style.css}}
    </style>
  </head>
  <body>
    {{template:html/_body.html}}
    {{template:html/_footer.html}}
  </body>
</html>
"""

demo_name = """
TTStatic DEMO
""".strip()

demo_footer = """
<hr>
textglue links: 
<br> - {{template:./_href.html name:"Home Page" url:"/"}}
<br> - {{template:./_href.html name:'Github Project' url:"https://gitlab.com/derekmc/derekmc.gitlab.io/-/tree/main/projects/textglue"}}
"""

demo_body = """
<div id='status_div' class='fl-right fff-000'> status goes here. </div>
<h1> {{file:../html/_name.html}} </h1>
<p> This is the textglue demo.</p>
<script>
  {{file:../js/_util.js}}
  {{file:../js/_main.js}}
</script>
"""

demo_viewport = """
<meta name="viewport" content="width=device-width, initial-scale=1.0">
""".strip()

demo_style = """
body{
  font-family: sans-serif;
}
.fl-right{
  float: right;
}
.fff-000{
  color: #fff;
  background: #000;
}
"""

demo_main = """
listen(window, 'load', main)
function main(){
  status('in main.')
}

"""

demo_util = """
__event_cancel = {}
function listen(target, name, f){
  target ??= window
  target.addEventListener(name, f)
  let cancel_callback = ()=>target.removeEventListener(name, f)
  if(!__event_cancel.hasOwnProperty(name)){
    __event_cancel[name] = []}
  __event_cancel[name].push(cancel_callback)
}
function cancel(name){
  let a = __event_cancel[name]
  if(!a) return false
  a.forEach(y=>y())
  return true
}
function clearEvents(){
  for(let x in __event_cancel){
    __event_cancel[x].forEach(y=>y())}
}
function status(s){
  console.info(s)
  text('status_div', s)
}
function id(x){
  return document.getElementById(x)
}
function text(x, s){
  let y = id(x)
  y.innerHTML = ''
  y.appendChild(document.createTextNode(s))
}
"""

demo_readme = """
# TextGlue

TextGlue is a simple static templating
system with two tags: "file" and "template".

The file tag copies the file verbatim into the source,
while the template tag recursively evaluates the
referenced file as a template itself.
"""

def batchWriteFiles(filelist, folder="."):
    try:
      os.mkdir(folder)
    except:
      print(f"  folder \"{folder}\" exists.")

    for (path, content) in filelist:
      outPath = os.path.join(folder, path)
      dirpath = os.path.dirname(outPath)
      if len(dirpath) > 0:
        os.makedirs(dirpath, exist_ok=True)
      if not os.path.exists(outPath) or input(f"Overwrite {outPath}? (N)").lower().strip() in ["y", "yes"]:
        print("overwriting")
        with open(outPath, 'w') as f:
          f.write(content)
      print(f"    file: '{outPath}'")


def initProject(srcFolder=defaultSrcFolder):
    print("== Initializing Simple TextGlue Project ==")
    config_files = [
      ("textglue.json", default_config),
    ]
    init_files = [
      ("README.md", demo_readme),
    ]
    batchWriteFiles(init_files, srcFolder)
    batchWriteFiles(config_files, ".")

def initDemo(srcFolder=defaultSrcFolder):
    print("== Initializing Demo Project ==")
    config_files = [
      ("textglue.json", default_config),
    ]
    demo_files = [
      ("index.html.glue", demo_index),
      ("README.md", demo_readme),
      ("html/_name.html", demo_name),
      ("html/_viewport.html", demo_viewport),
      ("html/_body.html", demo_body),
      ("html/_footer.html", demo_footer),
      ("html/_href.html", demo_href),
      ("css/_style.css", demo_style),
      ("js/_main.js", demo_main),
      ("js/_util.js", demo_util),
    ]
    batchWriteFiles(demo_files, srcFolder)
    batchWriteFiles(config_files, ".")

def ls_cmd():
  print("  Commands:\n" +
    "    - textglue init [srcFolder] - initialize project files, textglue.json and README.md\n" + 
    "    - textglue demo [srcFolder] - initialize the demo project in {srcFolder}\n" +
    "    - textglue render [srcFolder] [outFolder] - render templates, generate output.\n") 

def main_cli():
  print("\n=== textglue: A simple static template system ===")
  args = sys.argv
  # print("args: ", args)
  if len(args) < 2:
    return ls_cmd()
  cmd = args[1] 
  readConfig()
  global srcFolder
  global outFolder
  if len(args) > 2:
    srcFolder = args[2]

  if len(args) > 3:
    outFolder = args[3]

  if cmd == "init":
    initProject(srcFolder)
    return

  if cmd == "demo":
    initDemo(srcFolder)
    #if not os.path.exists(defaultSrcFolder):
    #else:
    #  print(f" | Cannot initialize demo, src_folder \"{defaultSrcFolder}\" already exists.\n | Please remove and try again.")
    return
  if cmd == "render":
    renderFolder()
    return
  print(f" | Unknown command: \"{cmd}\"")


if __name__ == "__main__":
    main_cli()
