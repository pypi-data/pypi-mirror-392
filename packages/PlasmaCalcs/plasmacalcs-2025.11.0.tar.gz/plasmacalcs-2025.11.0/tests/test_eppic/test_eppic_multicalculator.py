"""
File Purpose: misc tests for MultiCalculator with EppicCalculator calculators
"""

import os

import numpy as np
import xarray as xr

import PlasmaCalcs as pc
pc.DEFAULTS.pic_ambiguous_unit = dict(u_t=1)  # must be defined before loading an EppicCalculator.

HERE = os.path.dirname(__file__)


### --------------------- can create multicalculator --------------------- ###

def get_eppic_calculator(**kw_init):
    '''make an eppic calculator'''
    with pc.InDir(os.path.join(HERE, 'test_eppic_tinybox')):
        ec = pc.EppicCalculator.from_here(**kw_init)
    return ec

def test_make_multicalculator():
    '''ensure can make a multicalculator.'''
    ecA = get_eppic_calculator()
    ecB = get_eppic_calculator()
    pc.MultiCalculator({'ecA':ecA, 'ecB':ecB})


### --------------------- can load vars --------------------- ###

def test_multicalculator_load_misc():
    '''ensure can load various values via multicalculator'''
    ecA = get_eppic_calculator()
    ecB = get_eppic_calculator()
    mc = pc.MultiCalculator({'ecA':ecA, 'ecB':ecB})
    # load n
    dos = mc('n')  # DictOfSimilar
    assert np.all(dos['ecA'] == dos['ecB'])
    arr = dos.to_xr('calculator')
    assert 'calculator' in arr.dims
    assert arr.sizes['calculator'] == 2
    assert np.all(arr.isel(calculator=0) == arr.isel(calculator=1))
    # setting snap
    assert ecA.snap != 3
    assert ecB.snap != 3
    mc.snap = 3
    assert ecA.snap == 3
    assert ecB.snap == 3
    # setting fluid
    mc.fluid = pc.ELECTRON
    assert ecA.fluid == pc.ELECTRON
    assert ecB.fluid == pc.ELECTRON
    arr = mc('n').to_xr()
    assert np.all(arr.isel(variable=0) == arr.isel(variable=1))
    # ensure .to_xr() works on Dataset values too
    arr = mc('stats_n', snap=[2,5,7], fluid=pc.IONS).to_xr('calculator')
    assert set(arr.dims) == {'fluid', 'snap', 'calculator'}
    # ensure can do various operations to DictOfSimilar:
    dos = mc('n')
    arr = dos.to_xr()
    assert np.all((dos + 1e7)['ecA'] == dos['ecA'] + 1e7)
    assert np.all((1e7 + dos)['ecB'] == dos['ecB'] + 1e7)
    assert np.all((dos * 2)['ecB'] == dos['ecB'] * 2)
    assert np.all((2 * dos)['ecA'] == dos['ecA'] * 2)
    assert np.all((dos / 5).to_xr() == arr / 5)
    assert np.all((5 / dos).to_xr() == 5 / arr)
    assert np.all((dos - 1e7).to_xr() == arr - 1e7)
    assert np.all((1e7 - dos).to_xr() == 1e7 - arr)
    assert np.all((dos**2).to_xr() == arr**2)
    # other misc DictOfSimilar things:
    assert len(dos.subset(keep=['ecA'])) == 1
    assert len(dos.subset(keep=lambda k,v: k=='ecB')) == 1
    # ensure different results if different snaps
    ecA.snap = [3,6,9]
    ecB.snap = [2,4,6]
    dos = mc('meant_n')
    assert np.any(dos['ecA'] != dos['ecB'])
    # misc operations:
    assert dos.apply(lambda arr: arr.mean()).to_xr().size == 2
