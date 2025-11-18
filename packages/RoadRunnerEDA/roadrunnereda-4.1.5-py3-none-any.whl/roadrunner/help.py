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
from typing import Iterable, Sequence
from roadrunner.fn import etype

class HelpArg:
    pass

class HelpOption(HelpArg):
    def __init__(self, typ:str, names:Sequence[str], valType:str|None=None, default:str|None=None, desc:str=None):
        etype((typ, str), (names, (Sequence, str), str), (valType, (str, None)), (default, (str, None)), (desc, (str, None)))
        self.typ = typ
        self.names = names
        self.valType = valType
        self.default = default 
        self.desc = desc

class HelpProxy(HelpArg):
    def __init__(self, typ:str, scope:Sequence[str]):
        etype((typ, str), (scope, Sequence, str))
        self.typ = typ
        self.scope = scope

    def __iter__(self):
        itm = getHelp(self.typ, self.scope)
        if itm is not None:
            yield from itm
        else:
            logging.getLogger("RRHelp").warning(f"proxy for:{self.typ} scope:{self.scope} did not return anything")

helpDB = []

class HelpItem:
    def __init__(self, typ:str, scope:tuple[str, str] | str, desc:str, opt:Iterable[HelpArg]=[]):
        etype((typ, str), (scope, (tuple, str), str), (opt, Iterable, HelpArg))
        self.typ = typ
        self.scope = scope if isinstance(scope, tuple) else (scope,)
        self.desc = desc
        self.options = opt
        helpDB.append(self)

    def __iter__(self):
        if len(self.options):
            yield from self.options

def iterHelp(typ:str, scope:Sequence[str]|None=None) -> Iterable[tuple[HelpItem, list]]:
    etype((typ, str), (scope, (tuple, None), str))
    for itm in helpDB:
        if itm.typ != typ:
            continue
        if scope is not None and itm.scope[:len(scope)] != scope:
            continue
        yield itm

def getHelp(typ:str, scope:Sequence[str]) -> tuple[HelpItem, list] | None:
    it = iterHelp(typ, scope)
    try:
        return next(it)
    except StopIteration:
        return None
    
