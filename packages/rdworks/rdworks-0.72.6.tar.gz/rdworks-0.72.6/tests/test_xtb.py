from rdworks import Mol
from rdworks.xtb.wrapper import GFN2xTB
from rdworks.testdata import drugs

from pathlib import Path


datadir = Path(__file__).parent.resolve() / "data"
workdir = Path(__file__).parent.resolve() / "outfiles"

workdir.mkdir(exist_ok=True)

name = 'Acetaminophen'
testmol = Mol(drugs[name], name).make_confs(n=5).optimize_confs()
testmol = testmol.drop_confs(similar=True, verbose=True).sort_confs()
testconf = testmol.confs[0]
print(testconf)

def test_xtb_wrapper():
    conf = testconf.copy()
    gfn2xtb = GFN2xTB(conf.rdmol, xtb_exec='/home2/shbae/local/bin/xtb')
    
    assert gfn2xtb.is_xtb_ready() == True
    assert gfn2xtb.is_cpx_ready() == True
    assert gfn2xtb.is_cpcmx_ready() == True
    assert gfn2xtb.is_ready() == True
    assert gfn2xtb.version() is not None
    
    print("GFN2xTB.singlepoint()")
    outdict = gfn2xtb.singlepoint()
    print(outdict)
    print()


def test_singlepoint():        
    conf = testconf.copy()

    print("number of atoms=", conf.natoms)

    gfn2xtb = GFN2xTB(conf.rdmol)

    print("GFN2xTB.singlepoint()")
    outdict = gfn2xtb.singlepoint()
    print(outdict)
    print()

    print("GFN2xTB.singlepoint(water='gbsa')")
    outdict = gfn2xtb.singlepoint(water='gbsa')
    print(outdict)
    print()

    print("GFN2xTB.singlepoint(water='alpb')")
    outdict = gfn2xtb.singlepoint(water='alpb')
    print(outdict)
    print()

    print("GFN2xTB.singlepoint(water='cpcmx')")
    outdict = gfn2xtb.singlepoint(water='cpcmx')
    print(outdict)
    print()


def test_optimize():
    conf = testconf.copy()
    print("GFN2xTB.optimize()")
    outdict = GFN2xTB(conf.rdmol).optimize(verbose=True)
    print(outdict)
    print()


def test_esp():
    conf = testconf.copy()
    print("GFN2xTB.esp()")
    outdict = GFN2xTB(conf.rdmol).esp_volumetric(max_iterations=500, water='cpcmx')
    print(outdict)
    print()