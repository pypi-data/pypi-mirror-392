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

from pathlib import Path
from roadrunner.config import ConfigContext, PathNotExist
from roadrunner.fn import etype, relpath
from roadrunner.help import HelpItem, HelpOption, HelpProxy, HelpArg
from roadrunner.rr import Call, Pipeline, renderTemplate, asset
import roadrunner.modules.verilog
import roadrunner.modules.cpp
import roadrunner.modules.files
import logging


NAME = "Verilator"
HelpItem("tool", NAME, "Verilator Simulator")

DEFAULT_FLAGS = ['VERILATOR', 'DPI']

HelpItem("command", (NAME, "run"), "run Verilator lint check", [
    HelpProxy("function", (NAME, "do_compile")),
    HelpProxy("module", ("files", "share")),
    HelpProxy("module", ("files", "handleFiles")),
    HelpOption("attribute", "check", "bool", "true", "run the logchecker"),
    HelpProxy("function", (NAME, "do_check"))
])
def cmd_run(cfg:ConfigContext, pipe:Pipeline, vrsn:str) -> int:
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    wd = pipe.initWorkDir()

    flags = cfg.get('.flags', mkList=True, default=[]) + DEFAULT_FLAGS
    fcfg = cfg.move(addFlags=set(flags))

    check = fcfg.get('.check', default=True, isType=bool)

    with pipe.inSequence("verilator"):

        roadrunner.modules.files.share(fcfg, pipe)
        roadrunner.modules.files.handleFiles(fcfg, wd, pipe)

        do_compile(fcfg, wd, vrsn, pipe)

        call = Call(wd, 'simulation', NAME, vrsn)
        call.addArgs(['obj_dir/VSim'])
        pipe.addCall(call)

        if check:
            do_check(wd, pipe)

    return 0
HelpItem("command", (NAME, "lint"), "run Verilator lint check", [
    HelpProxy("function", (NAME, "do_compile")),
    HelpProxy("module", ("files", "share")),
    HelpProxy("module", ("files", "handleFiles"))
])
def cmd_lint(cfg:ConfigContext, pipe:Pipeline, vrsn:str) -> int:
    etype((cfg,ConfigContext), (pipe,Pipeline), (vrsn,(str,None)))
    wd = pipe.initWorkDir()

    with pipe.inSequence("lint"):

        roadrunner.modules.files.share(cfg, pipe)
        roadrunner.modules.files.handleFiles(cfg, wd, pipe)

        do_compile(cfg, wd, vrsn, pipe, lint=True)

    return 0

HelpItem("function", (NAME, "do_check"), "run logcheck", [])
def do_check(wd:Path, pipe:Pipeline):
    with open(wd / "logcheck.py", "w") as fh:
        print(asset(Path('rr/logcheck.py')).source, file=fh)
    call = Call(wd, 'logcheck', "Python3")
    call.addArgs(['python3', 'logcheck.py', 'simulation.stdout'])
    pipe.addCall(call)

def do_compile(cfg:ConfigContext, wd:Path, vrsn:str, pipe:Pipeline, lint:bool=False) -> int:
    etype((cfg,ConfigContext), (wd,Path), (vrsn,(str,None)), (pipe,Pipeline), (lint,bool))
    log = logging.getLogger(NAME)

    toplevel = cfg.get('.toplevel', isType=str)
    trace = cfg.get('.trace', default='none', isType=str)
    noExitOnWarning = cfg.get('.noExitOnWarning', default=False, isType=bool)

    envfile = roadrunner.modules.verilog.writeEnvFile(wd, {})

    extraFiles = [relpath(envfile, wd)]

    if trace != 'none':
        #include RRTrace
        code = renderTemplate(Path("verilog/RRTraceTop.sv"), {'toplevel': toplevel})
        with open(wd / "RRTraceTop.sv", "w") as fh:
            print(code, file=fh)
        extraFiles.append(Path("RRTraceTop.sv"))
        toplevel = "RRTraceTop"
        
    hasWaivers = do_VerilogFiles(cfg, wd, pipe, extraFiles)
    do_DpiModules(cfg, wd, pipe)

    if trace != 'none' and hasWaivers:
        log.warning("Trace is enabled and waivers are present, that does not work - adding --no-fatal")
        noExitOnWarning = True


    call = Call(wd, 'verilator', NAME, vrsn)
    call.addArgs(['verilator', '--cc'])
    if lint:
        call.addArgs(['--lint-only'])
    else:
        call.addArgs(['--binary'])
    if trace == 'vcd':
        call.addArgs(['--trace'])
    elif trace == 'fst':
        call.addArgs(['--trace-fst'])
    elif trace == 'none':
        pass
    else:
        raise ValueError(f"Unknown trace type: {trace}")
    if noExitOnWarning:
        call.addArgs(['-Wno-fatal'])
    call.addArgs(['--timing'])
    call.addArgs(['--top-module', toplevel])
    call.addArgs(['-o', 'VSim'])
    call.addArgs(['-f', 'sources.cmd'])
    call.addArgs(['-f', 'dpiModules.cmd'])

    pipe.addCall(call)

    return 0

# returns if there are waivers
def do_VerilogFiles(cfg:ConfigContext, wd:Path, pipe:Pipeline, addFiles:list=[]) -> bool:
    etype((cfg,ConfigContext), (wd,Path), (pipe,Pipeline), (addFiles, list, Path))
    lst = roadrunner.modules.verilog.includeFiles(cfg.move(), wd)

    files = addFiles[:]
    defs = set()
    incs = set()
    waivers = []

    for ncfg in cfg.travers():
        itm = roadrunner.modules.verilog.gather(ncfg, wd)
        for fname in itm.sv + itm.v:
            if fname not in files:
                files.append(fname)
        for d in itm.defines:
            defs.add(d)
        for inc in itm.path:
            incs.add(inc)
        waivers += gatherWaivers(ncfg, itm)

    if len(waivers):
        waiverFile = writeWaiverFile(wd, waivers)
        files.insert(0, waiverFile)
        hasWaivers = True
    else:
        hasWaivers = False

    with open(wd / 'sources.cmd', 'w') as fh:
        for d in defs:
            print(f"-D{d}", file=fh)
        for fname in files:
            print(f"{fname}", file=fh)
        for inc in incs:
            print(f"-I{inc}", file=fh)
    return hasWaivers

# mod:
#   sv: mod.sv
#   vWaive:
#     - file: mod.sv
#       rule: BLKSEQ
#       lines: 24-25

def loadWaiver(cfg:ConfigContext, itm:roadrunner.modules.verilog.FileItem):
    etype((cfg,ConfigContext))
    file = cfg.get('.file', isOsPath=True)
    rule = cfg.get('.rule', isType=str)
    lines = cfg.get('.lines', isType=str)
    #verilog
    dstFile = itm.imports[file]
    return {'file': dstFile, 'rule': rule, 'lines': lines}

def gatherWaivers(cfg:ConfigContext, itm:roadrunner.modules.verilog.FileItem):
    etype((cfg,ConfigContext))
    waivers = []
    #find waivers
    try:
        vCfg = cfg.move(".vWaiver")
    except PathNotExist:
        return waivers
    if vCfg.isList():
        for _, lCfg in vCfg:
            waivers.append(loadWaiver(lCfg, itm))
    else:
        waivers.append(loadWaiver(vCfg, itm))
    return waivers

def writeWaiverFile(wd:Path, waivers:list):
    fname = 'waiver.vlt'
    #write waiver file
    templ = renderTemplate(Path('verilator/waiver.vlt'), {'waivers': waivers})
    with open( wd / fname, 'w') as fh:
        print(templ, file=fh)
    return fname

def do_DpiModules(cfg:ConfigContext, wd:Path, pipe:Pipeline):
    etype((cfg,ConfigContext), (wd,Path), (pipe,Pipeline))

    used = []

    with open(wd / 'dpiModules.cmd', 'w') as fh:
        for vnode in cfg.travers():
            node = vnode.real()
            try:
                dpiMod = node.move(".dpiModule")
            except PathNotExist:
                continue
            if node.pos() in used:
                continue
            used.append(node.pos())
            for itm in roadrunner.modules.cpp.includeFiles(dpiMod, wd):
                for path in itm.path:
                    print(f'-CFLAGS -I../{path}', file=fh)
                for lib in itm.libpath:
                    print(f'-CFLAGS -L../{lib}', file=fh)
                for lib in itm.lib:
                    print(f'-CFLAGS -l{lib}', file=fh)
                if itm.std is not None:
                    print(f'-CFLAGS -std={itm.std}', file=fh)
                print(*map(str, itm.c), sep='\n', file=fh)
                print(*map(str, itm.cpp), sep='\n', file=fh)
