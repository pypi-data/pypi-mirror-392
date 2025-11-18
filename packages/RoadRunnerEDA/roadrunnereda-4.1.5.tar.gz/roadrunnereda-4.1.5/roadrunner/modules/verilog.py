####    ############
####    ############
####
####
############    ####
############    ####
####    ####    ####
####    ####    ####
############
############

import logging
from pathlib import Path
from roadrunner.fn import etype
from roadrunner.help import HelpItem, HelpOption
from roadrunner.config import ConfigContext, ConfigPath, Location
from dataclasses import dataclass
from roadrunner.rr import renderTemplate, workdir_import_list

RRENV_FILE = "RREnv.sv"
CONFIG_FLAGS = {'VERILOG'}
LOGNAME = "Verilog"

def writeEnvFile(loc:Path, vars:dict) -> Path:
    etype((loc,Path), (vars,dict))
    fname = loc / RRENV_FILE
    params = []
    svParams = {key: sv_val(var) for key, var in vars.items()}
    for name, var in vars.items():
        params.append(f"localparam {name} = {sv_val(var)};")
    tpl = renderTemplate(Path('verilog/RREnv.sv'), {'params': svParams})
    with open(fname, "w") as fh:
        print(tpl, file=fh)
    return fname

def sv_val(val):
    if isinstance(val, list):
        return "'{" + ", ".join(sv_val(x) for x in val) + "}"
    elif isinstance(val, (str, Path)):
        return '"' + str(val) + '"'
    else:
        return str(val)

@dataclass
class FileItem:
    node:ConfigPath
    v:list[Path]
    sv:list[Path]
    defines:list[str]
    path:list[Path]
    static:bool
    imports: dict[tuple[Location,Path], Path]
    
HelpItem("module", ("verilog", "includeFiles"), "import verilog files", [
    HelpOption("attribute", "v", "list[file]", None, "list of verilog files"),
    HelpOption("attribute", "sv", "list[file]", None, "list of systemverilog files"),
    HelpOption("attribute", "path", "list[dir]", None, "list of include paths"),
    HelpOption("attribute", "define", "list[str]", None, "list of defines"),
    HelpOption("attribute", "inc", "tree", None, "traversing the config tree")
])
def includeFiles(cfg:ConfigContext, wd:Path) -> list[FileItem]:
    log = logging.getLogger(LOGNAME)
    files = []
    for itm in cfg.move(addFlags=CONFIG_FLAGS).travers():
        files.append(gather(itm, wd))

    return files

def gather(cfg:ConfigContext, wd:Path) -> FileItem:
    etype((cfg,ConfigContext), (wd,Path))
    vSrc = cfg.get(".v", mkList=True, isOsPath=True, default=[])
    svSrc = cfg.get(".sv", mkList=True, isOsPath=True, default=[])
    pathSrc = cfg.get(".path", mkList=True, isOsPath=True, default=[])
    imports = {}
    v = workdir_import_list(wd, vSrc)
    for dst,src in zip(v, vSrc):
        imports[src] = dst
    sv = workdir_import_list(wd, svSrc)
    for dst,src in zip(sv, svSrc):
        imports[src] = dst
    path = workdir_import_list(wd, pathSrc, baseDir=Path("include"))
    incdirset = set()
    for i in path:
        if i.is_dir() or (wd / i).is_dir():
            incdirset.add(i)
        else:
            incdirset.add(i.parent)
    incdirs = list(incdirset)
    defines = cfg.get(".define", mkList=True, default=[])
    static = cfg.location().static
    return FileItem(cfg.pos(), v, sv, defines, incdirs, static, imports)