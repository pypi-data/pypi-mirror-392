"""
File Purpose: misc tests for physics using data from eppic hookup in PlasmaCalcs.
These tests require some simulation output.
"""
import os

# setting mp start method to fork (instead of 'spawn') prevents leaked semaphore objects. Not sure why.
# it also makes the tests a bit faster, maybe...
import multiprocessing as mp
mp.set_start_method('fork', force=True)

import numpy as np
import xarray as xr

import PlasmaCalcs as pc
pc.DEFAULTS.pic_ambiguous_unit = dict(u_t=1)  # must be defined before loading an EppicCalculator.

HERE = os.path.dirname(__file__)


### --------------------- can create eppic calculator --------------------- ###

def get_eppic_calculator(**kw_init):
    '''make an eppic calculator'''
    with pc.InDir(os.path.join(HERE, 'test_eppic_tinybox')):
        ec = pc.EppicCalculator.from_here(**kw_init)
    return ec


### --------------------- drifts --------------------- ###

def test_nusn_from_drift():
    '''ensure nusn_from_drift results are reasonable.'''
    ec = get_eppic_calculator()
    margin = 0.25  # 25% margin of error -- this is noisy stuff since box is so small.
    ec.snap = slice(3, None)  # ignore first few snaps - not enough time to reach equil.
    ec.fluid = pc.IONS
    arr = ec('meant_nusn_from_means_hall/nusn')
    assert np.all(1 - margin < arr) and np.all(arr < 1 + margin)
    arr = ec('meant_nusn_from_means_momE/nusn')
    # pederson & ExB drifts contain enough info to get reasonable value for electron too
    ec.fluid = None
    assert np.all(1 - margin < arr) and np.all(arr < 1 + margin)
    arr = ec('meant_nusn_from_means_pederson/nusn')
    assert np.all(1 - margin < arr) and np.all(arr < 1 + margin)
    arr = ec('meant_nusn_from_means_momExB/nusn')
    assert np.all(1 - margin < arr) and np.all(arr < 1 + margin)

def test_get_drift():
    '''ensure drift velocity predictions are close to actual velocities.
    Not exact, due to noise.
    '''
    ec = get_eppic_calculator()
    margin = 0.35  # 35% margin of error -- this is noisy stuff since box is so small.
    ec.snap = slice(3, None)  # ignore first few snaps - not enough time to reach equil.
    arr = ec('mean_mod_u/mean_mod_u_drift')
    assert 1 - margin < arr.min()
    assert arr.max() < 1 + margin
