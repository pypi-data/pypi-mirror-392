"""
File Purpose: loading single-fluid MHD quantities related to radiative transfer synthesis.
"""

# builtins
import os
import shutil
import datetime as datetime
from collections.abc import Callable
import inspect

# public/common external (and, part of PlasmaCalcs requirements already)
import xarray as xr
import numpy as np

# private/external (not part of PlasmaCalcs requirements)
from ..tools import ImportFailed  # <-- helps if import fails
try:
    from muse.instr import utils as muse_instr_utils  
except ImportError as err:
    muse_instr_utils = ImportFailed("muse.instr.utils", err=err, locals=locals(), abbrv='muse_instr_utils')

try:
    import ChiantiPy.core as ch
except ImportError as err:
    ch = ImportFailed("ChiantiPy.core", err=err, locals=locals(), abbrv='ch')

# internal
from .mhd_bases import MhdBasesLoader
from ..defaults import DEFAULTS
from ..tools import (
    simple_property, format_docstring,
    product, xarray_sum,
    xr1d, _xarray_save_prep,
    xarray_max_dim_sizes, xarray_predict_result_size, xarray_result_size_check,
)
from ..errors import (
    InputError, InputConflictError,
    ComponentValueError, DimensionalityError,
)


### --------------------- Helper functions --------------------- ###

def lambda_to_doppler(wave, wave0):
    """
    Convert wavelength to Doppler velocity units (km/s).

    Parameters
    ----------
    wave : array-like
        Observed wavelength(s) [same units as wave0, e.g., Angstroms].
    wave0 : float
        Rest wavelength.

    Returns
    -------
    array-like
        Doppler velocity in km/s.
    """
    cc = 2.99792458e10 / 1e5
    return (wave / wave0 - 1.0) * cc  # outputs in km/s


def doppler_to_lambda(doppler, wave0):
    """
    Convert wavelength to Doppler velocity units (km/s).

    Parameters
    ----------
    doppler : array-like
        Doppler velocity in km/s.
    wave0 : float
        Rest wavelength.

    Returns
    -------
    array-like
        Observed wavelength(s) [same units as wave0, e.g., Angstroms]
    """
    cc = 2.99792458e10 / 1e5
    return wave0 * (1.0 + doppler / cc)  # outputs in units of wave0


def read_qloss(file="Radloss_Chianti.dat"):
    """
    Read radiative loss table from file.

    Parameters
    ----------
    file : str
        Filename for the radiative loss table.

    Returns
    -------
    tg : ndarray
        Temperature grid.
    qloss : ndarray
        Radiative loss values.
    """
    f = open("Radloss_Chianti.dat", "r")
    first_line = f.readline()
    ntg = int(first_line.strip())
    tg = np.zeros(ntg)
    qloss = np.zeros(ntg)

    for ii, line in enumerate(f):
        tg[ii], qloss[ii] = np.float64(line.strip().split())

    return tg, qloss

#@pcAccessor.register('radiative_interp_correction', totype='array')   # <-- would be fine, if desired!
def interp_correction(array, bins, dim, *, log=True):
    """
    Compute interpolation masks and normalization factors for a variable (e.g., temperature)
    for use in DEM/VDEM binning with or without logarithmic scaling.

    This function is typically used to prepare masks and normalization factors for
    temperature-differential emission measure (DEM) or velocity-differential emission measure (VDEM)
    calculations, by binning along a specified axis (e.g., logT or velocity).
    It supports both linear and logarithmic binning.

    See Rempel et al. (2017) for details.

    Parameters
    ----------
    array : xarray.DataArray
        variable to be interp-corrected. E.g., array of log10(temperature) values.
    bins: xarray.DataArray
        1D array of (evenly-spaced) bin centers (internally, assumes bin width = (bins[1]-bins[0])/2).
    dim: str
        apply the correction along this dimension of array.
        For VDEMS, this is the dimension along which the LOS integration will be performed.
    log : bool, optional
        whether to use logarithmic binning (default: True).

    Returns
    -------
    maskvalue : xarray.DataArray
        Boolean mask indicating which cells fall into each bin,
        multiplied by fn, the normalization factor for each bin, with values clipped to [0, 1].
    xn : xarray.DataArray
        Interpolation weight for each bin, with values clipped to [0, 1].
    """
    x = dim
    if not isinstance(bins, xr.DataArray):
        raise TypeError("interp_correction: bins must be an xarray.DataArray")
    if bins.ndim != 1:
        raise DimensionalityError(f'interp_correction: expected 1D bins; got bins.ndim={bins.ndim}')

    xarray_result_size_check(array, bins)  # if result would be too huge, make crash instead!

    delta = (bins.values[1] - bins.values[0]) / 2

    value = array
    #if log:
    #    value = np.log10(value)
    value1 = value.roll({x:1})

    minvalue = np.minimum(value, value1)
    maxvalue = np.maximum(value, value1)
    
    ### compute masks ###
    maskvalue = maxvalue >= bins - delta
    maskvalue *= minvalue < bins + delta  # bool * bool <--> logical AND

    maskmin = xr.where(minvalue >= bins - delta, minvalue, bins - delta)
    maskmax = xr.where(maxvalue < bins + delta, maxvalue, bins + delta)

    ### correction coefficient ###
    fn = np.abs(maskmax - maskmin) / np.abs(value1 - value)

    ### interpolation weights ###
    if log:
        xn = (10**value - 10**bins) / np.abs(10**value - 10**value1)
    else:
        xn = (value - bins) / np.abs(value - value1)

    ### limits ###
    fn = fn.fillna(0.0)
    fn = xr.where(fn < 1.0, fn, 1.0)
    fn = xr.where(fn > 0.0, fn, 0.0)
    xn = xn.fillna(0.0)
    xn = xr.where(xn < 1.0, xn, 1.0)
    xn = xr.where(xn > 0.0, xn, 0.0)

    return maskvalue * fn, xn

#@pcAccessor.register('radiative_los_correction', totype='array')   # <-- would be fine, if desired!
def los_correction(array, bins, dim, *, log=False):
    """
    Compute line-of-sight (LOS) correction masks and normalization factors for velocity or other variables.

    This function is typically used to prepare masks and normalization factors
        for velocity-differential emission measure (VDEM) calculations,
        by binning along a specified axis (e.g., Doppler velocity).
        It supports both linear and logarithmic binning.

    See Rempel et al. (2017) for details.

    Parameters
    ----------
    array: xarray.DataArray
        variable to be interp-corrected. E.g., array of velocity values.
    bins: xarray.DataArray
        1D array of (evenly-spaced) bin centers (internally, assumes bin width = (bins[1]-bins[0])/2).
    dim: str
        apply the correction along this dimension of array.
        For VDEMS, this is the dimension along which the LOS integration will be performed.
    log : bool, optional
        whether to use logarithmic binning (default: True).

    Returns
    -------
    maskvalue : xarray.DataArray
        Boolean mask indicating which cells fall into each bin,
        multiplied by fn, the normalization factor for each bin, with values clipped to [0, 1].
    """
    x = dim
    if not isinstance(bins, xr.DataArray):
        raise TypeError("los_correction: bins must be an xarray.DataArray")
    if bins.ndim != 1:
        raise DimensionalityError(f'los_correction: expected 1D bins; got bins.ndim={bins.ndim}')
        
    delta = (bins.values[1] - bins.values[0]) / 2

    xarray_result_size_check(array, bins)  # if result would be too huge, make crash instead!

    value = array
    if log:
        value = np.log10(value)

    value1 = value.roll({x:1})

    minvalue = np.minimum(value, value1)
    maxvalue = np.maximum(value, value1)

    ### compute masks ###
    maskvalue = maxvalue >= bins - delta
    maskvalue *= minvalue < bins + delta  # bool * bool <--> logical AND

    maskmin = minvalue.where(minvalue >= bins- delta)
    maskmin = maskmin.fillna(bins - delta)
    maskmax = maxvalue.where(maxvalue <= bins + delta)
    maskmax = maskmax.fillna(bins + delta)
    ### correction coefficient ###
    fn = np.abs(maskmax - maskmin) / np.abs(value1 - value) 
    ### limits ###
    fn = fn.where(fn < 1, 1)
    fn = fn.where(fn > 0, 0)

    return maskvalue * fn


### --------------------- MhdRadiativeLoader --------------------- ###

class MhdRadiativeLoader(MhdBasesLoader):
    '''computes single-fluid MHD quantities related radiative transfer'''

    # # # HELPER METHODS # # #
    def _radiative_assert_single_component(self):
        '''asserts self.current_n_component() == 1; raise ComponentValueError otherwise.
        The error message will be particularly helpful and give options for how to fix the error.
        '''
        if self.current_n_component() != 1:
            errmsg = ("Inside of a MhdRadiativeLoader method, requiring a single component, "
                      f"but got self.component={self.component}.\nConsider specifying component, "
                      "e.g. via self.component='x', or self(f'{var}_y'), or self(var, component='z')")
            raise ComponentValueError(errmsg)

    # # # VARIOUS SETTINGS # # #
    @property
    def _extra_kw_for_quantity_loader_call(self):
        '''extra kwargs which can be used to set attrs self during self.__call__.
        The implementation here returns ['vdem_logT', 'vdem_loopdim'] + any values from super().
        '''
        return ['vdem_logT', 'vdem_loopdim'] + super()._extra_kw_for_quantity_loader_call

    # # # EMISSION MEASURE # # #

    cls_behavior_attrs.register('emiss_mode', default='notrac_noopa')
    EMISS_MODE_OPTIONS = {
        'notrac_noopa': 'Emission measure with no TRAC correction, no opacity',
        'trac_noopa': 'Emission measure with TRAC correction, no opacity',
        'notrac_opa': 'Emission measure with no TRAC correction, and with opacity',
        'trac_opa': 'Emission measure with TRAC correction and opacity',
    }

    emiss_mode = simple_property('_emiss_mode', default='notrac_noopa', validate_from='EMISS_MODE_OPTIONS',
            doc="Selects the emission measure calculation mode. See self.EMISS_MODE_OPTIONS for options.")

    _EMISS_MODE_TO_EM_VAR = {
        'notrac_noopa': 'emiss_notrac', 
        'trac_noopa': 'emiss_trac', 
        'notrac_opa': 'emiss_notrac', 
        'trac_opa': 'emiss_trac',
    }
    _EMISS_MODE_TO_DEPS = {
        'notrac_noopa': ['emiss_notrac'],
        'trac_noopa': ['emiss_trac'],
        'notrac_opa': ['emiss_notrac', 'tau'],
        'trac_opa': ['emiss_trac', 'tau'],
    }

    @known_var(attr_deps=[('emiss_mode', '_EMISS_MODE_TO_DEPS')])
    def get_emiss(self):
        """Emission measure (EM) based on the selected emission mode (self.emiss_mode).
        Depends on self.emiss_mode; see self.EMISS_MODE_OPTIONS for details.

        Result is always in cgs, regardless of self.units.
        """
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        var = self._EMISS_MODE_TO_EM_VAR[self.emiss_mode]
        with self.using(units='cgs'):
            if "_noopa" in self.emiss_mode:
                return self(var)
            elif "_opa" in self.emiss_mode:
                return self(var) * np.exp(-self("tau"))

    @known_var(deps=['ne', 'r'])
    def get_emiss_notrac(self):
        '''Emission measure in cgs without TRAC correction.
        Result is always in [cgs], regardless of self.units.

        nh = r / (n_per_nh * mh)
        emiss_notrac = ne * nh / self.emiss_norm [1/cm^6]
        '''
        self.assert_single_fluid_mode('emiss_notrac')
        with self.using(units='cgs'):
            r_per_nH_tot = (self.elements.n_per_nH() * self.elements.m * self.u('amu')).sum()
            val = self('ne') * self('r') / (r_per_nH_tot * self.emiss_norm)
            return val

    cls_behavior_attrs.register('emiss_norm', default=1e27)
    emiss_norm = simple_property('_emiss_norm', default=1e27,
        doc='''Emission Measure normalization factor. Used in self('emiss')
        and related vars. emiss = unnormed_emiss / emiss_norm.''')

    cls_behavior_attrs.register('emiss_trac_coeff')
    emiss_trac_coeff = simple_property('_emiss_trac_coeff', default=3,
        doc='''TRAC coefficient for emiss_trac calculation.
         transition region using an adaptive conduction coefficient (Johnston et al. 2020).''')

    @known_var(deps=['emiss_notrac', 'B', 'T'], ignores_dims=['component'])
    def get_emiss_trac(self):
        '''Emission measure in cgs with TRAC correction.
        Result is always in [cgs], regardless of self.units.

        nh = r / (n_per_nh * mh)
        emiss_trac = ne * nh * trac_correction / normalization

        self.emiss_trac_coeff tells the TRAC coefficient (default 3) 
        '''
        self.assert_single_fluid_mode('emiss_trac')
        if not set(('x', 'y', 'z')) <= set(self.maindims):  # i.e., x, y, and z are not all in maindims:
            errmsg = f'emiss_trac requires 3D data (x, y, and z), but got self.maindims={self.maindims}.'
            raise DimensionalityError(errmsg)
        with self.using(units='cgs'):
            emis = self('emiss_notrac')
            bx = self("B", component='x', units = 'raw')  # only using relative values of Bx,By,Bz so 'raw' is cheaper.
            by = self("B", component='y', units = 'raw')  #    also, 'cgs' B would complain, by default.
            bz = self("B", component='z', units = 'raw')
            tg = self('T')
            dx = self('dx')
            dy = self('dy')
            dz = self('dz')

            tg_dep, qloss_dep = read_qloss()
            Lt = xr.DataArray(qloss_dep, coords={"T": tg_dep}, dims="T").interp(T=tg)

            Q_Chianti = emis * (Lt * self.emiss_norm)
            modb = np.sqrt(bx**2 + by**2 + bz**2)
            kappa_spitzer = 1e-6 * tg**2.5 # 1e-6 comes from TRAC method (dimensions?)

            L_R = (
                self.emiss_trac_coeff
                * (np.abs(bx) * dx + np.abs(by) * dy + np.abs(bz) * dz)
                / modb
            )

            fmin = np.sqrt(kappa_spitzer * tg / Q_Chianti) / (2.0 * L_R)
            fmin = fmin.where(fmin <= 1, 1.0)

            emis *= fmin
            return emis


    # # # VDEM # # #
    # differential emission measure as a function of temperature and velocity.

    # temperature and velocity bins determined by rcoords_logT and rcoords_vdop_kms:
    cls_behavior_attrs.register('rcoords_vdop_kms')
    rcoords_vdop_kms = simple_property('_rcoords_vdop_kms', default=np.arange(-100,100,10), 
            doc='''velocity [km/s] (or, doppler shift) values, used by some MhdRadiativeLoader vars.
            E.g., used in VDEMs and in getting spectra.
            Can be a scalar, a 1D list or numpy array, or 1D xr.DataArray with dimension 'vdop'.''')
    @known_var
    def get_rcoords_vdop(self):
        '''velocity (or, doppler shift) values used by some vars (e.g. vdems and spectra), in [self.units] system,
        along dimension 'vdop', with coords always in km/s regardless of self.units.
        Determined by self.rcoords_vdop_kms (which can be set directly), converted to [self.units].
        '''
        result = xr1d(self.rcoords_vdop_kms, name='vdop', lenient=True)  # [km/s]
        return result * (self.u("u", convert_from='si') * 1e3)  # [self.units]

    cls_behavior_attrs.register('rcoords_logT')
    rcoords_logT = simple_property('_rcoords_logT', default=np.arange(4.6,6.5,0.1), 
            doc='''log10(Temperature [K]) values used by some MhdRadiativeLoader vars.
            E.g., used in VDEMs and in G(T) lookup tables.
            Can be a scalar, a 1D list or numpy array, or 1D xr.DataArray with dimension 'logT'.
            Note: rcoords_logT minimum value can never be less than self.vdem_logT_min.
                (attempting to set bad value will cause crash & helpful error message.)''')
    @rcoords_logT.setter
    def rcoords_logT(self, value):
        value = xr1d(value, name='logT', lenient=True)
        minval = np.min(value).item()
        if minval < self.vdem_logT_min:
            errmsg = (f'cannot set self.rcoords_logT to something with minimum ({minval:.3g}) less than '
                      f'self.vdem_logT_min={self.vdem_logT_min:.3g}.\n'
                      f'To proceed, first set vdem_logT_min to a smaller value, then try again.\n'
                      f'(To set both simultaneously, use self.vdem_logT = (new_min, new_coords).)')
            raise InputConflictError(errmsg)
        self._rcoords_logT = value

    @known_var
    def get_rcoords_logT(self):
        '''log(Temperature) values used by some vars (e.g. vdems and G(T)), in [self.units] system,
        along dimension 'logT', with coords always telling log(T [K]) regardless of self.units.
        Determined by self.rcoords_logT (which can be set directly), converted to [self.units].
        '''
        result = xr1d(self.rcoords_logT, name='logT', lenient=True)  # log10([K])
        u = self.u("temperature", convert_from='si')
        if u != 1.0:  # [EFF] small efficiency improvement, added because u will very commonly be 1.
            result = result + np.log10(u)   # (this formula also works if u==1, but would just add 0.)
        return result  # log10([self.units])

    cls_behavior_attrs.register('vdem_logT_min', default=4)
    vdem_logT_min = simple_property('_vdem_logT_min', default=4,
            doc='''Minimum log10(temperature [K]) to include in VDEM calculations.
            some VDEMs ignore emiss contributions from very cold regions (T < self.vdem_logT_min).
            Note: vdem_logT_min can never be more than minimum value of self.rcoords_logT.
                (attempting to set bad value will cause crash & helpful error message.)''')
    @vdem_logT_min.setter
    def vdem_logT_min(self, value):
        minval = np.min(self.rcoords_logT).item()
        if value > minval:
            errmsg = (f'cannot set self.vdem_logT_min to something ({value:.3g}) more than '
                      f'the minimum of self.rcoords_logT ({minval:.3g}).\n'
                      f'To proceed, first set rcoords_logT to a larger value, then try again.\n'
                      f'(To set both simultaneously, use self.vdem_logT = (new_min, new_coords).)')
            raise InputConflictError(errmsg)
        self._vdem_logT_min = value

    @property
    def vdem_logT(self):
        '''(self.vdem_logT_min, self.rcoords_logT).
        Can set both at once via self.vdem_logT = (desired_min, desired_coords)
        '''
        return (self.vdem_logT_min, self.rcoords_logT)
    @vdem_logT.setter
    def vdem_logT(self, value):
        newmin, coords = value
        minval = np.min(coords).item()
        if newmin > minval:
            errmsg = (f'cannot set self.vdem_logT = (newmin, newcoords) when newmin > min(newcoords)!\n'
                      f'got newmin={newmin:.3g}, min(newcoords)={minval:.3g}.')
            raise InputConflictError(errmsg)
        # avoid ever having logT_min > min(rcoords_logT):
        oldmin = self.vdem_logT_min
        self.vdem_logT_min = min(oldmin, newmin)
        # actually set the values:
        self.rcoords_logT = coords
        self.vdem_logT_min = newmin  # <-- in case newmin > oldmin

    # other vdem settings:
    cls_behavior_attrs.register('vdem_ignores_photosphere', default='z=0')
    vdem_ignores_photosphere = simple_property('_vdem_ignores_photosphere', default='z=0',
            doc='''Specifies how the photosphere is treated in VDEM calculations.
            Options include:
                'z=0' --> account for photosphere by ignoring all values at z < 0.
                False --> do not worry about photosphere.''')

    cls_behavior_attrs.register('vdem_mode', default='interp')
    VDEM_MODE_OPTIONS = {
        'interp': (
            "Interpolate the velocity-differential emission measure (VDEM) in temperature only."
            "This mode uses 'Matthias trick' for temperature binning, providing a balance between speed and accuracy."
        ),
        'nointerp': (
            "No interpolation: "
            "Computes the VDEM by direct binning in both temperature and velocity without any interpolation. "
        ),
        'allinterp': "Interpolate in both temperature and velocity.",
    }
    vdem_mode = simple_property('_vdem_mode', default='interp', validate_from='VDEM_MODE_OPTIONS',
            doc='''Selects the velocity-differential emission measure (VDEM) calculation mode.
            See self.VDEM_MODE_OPTIONS for options.''')

    _VDEM_MODE_TO_VDEM_VAR = {'interp': 'vdem_interp',
                             'nointerp': 'vdem_no_interp',
                             'allinterp': 'vdem_allinterp',
                            }

    # vdem vars:
    @known_var(attr_deps=[('vdem_mode', '_VDEM_MODE_TO_VDEM_VAR')])
    def get_vdem(self):
        '''VDEM (intergrated along an axis), as a function of temperature and velocity.

        Generic to all vdem vars:
            temperature and velocity are determined by self.rcoords_logT and self.rcoords_vdop_kms,
                which can be set directly.

            Result is always in [cgs] units, regardless of self.units.

            Might ignore photosphere, depending on self.vdem_ignores_photosphere;
                see help(type(self).vdem_ignores_photosphere) for details.

            Result is along line of sight corresponding to self.component (must be a single value).
            Can set via, e.g., self.component='x', or self('vdem_y'), or self(var, component='z').

        Specific to this vdem var:
            Result depends on self.vdem_mode; see self.VDEM_MODE_OPTIONS for details.
        '''
        var = self._VDEM_MODE_TO_VDEM_VAR[self.vdem_mode]
        return self(var)

    @known_var(deps=['emiss', 'u', 'T', 'rcoords_logT', 'rcoords_vdop'])
    def get_vdem_no_interp(self):
        '''VDEM (intergrated along an axis), without interpolation.
        See self.help('vdem') or help(self.get_vdem) for more details about vdems.
        '''
        self._radiative_assert_single_component()

        U_NORM = 1e5  # converts from cgs to km/s. Not necessary, but helps avoid rounding errors(?)

        x = str(self.component)
        with self.using(units='cgs'):
            ### get relevant vals ###
            dx = self(f'd{x}')
            tg = self("T")
            ulos = - self("u", component=x) / U_NORM
            emiss = self('emiss')
            if self.vdem_ignores_photosphere == 'z=0':
                emiss = emiss * (emiss["z"] > 0)

            ### compute masks ###
            logT = self('rcoords_logT')
            vdop = self('rcoords_vdop') / U_NORM
            dlogT = logT.isel(logT=1).item() - logT.isel(logT=0).item()
            dvdop = vdop.isel(vdop=1).item() - vdop.isel(vdop=0).item()
            # temperature mask everywhere outside of the bin (bin is from logT-dlogT/2 to logT+dlogT/2)
            masktg = tg >= 10.0 ** (logT - dlogT / 2.0) 
            masktg *= tg < 10.0 ** (logT + dlogT / 2.0)   # bool * bool <--> logical AND
            # velocity mask everywhere outside of the bin (bin is from vdop-dvdop/2 to vdop+dvdop/2)
            maskvel = ulos >= vdop - dvdop / 2.0
            maskvel *= ulos < vdop + dvdop / 2.0  # bool * bool <--> logical AND

            ### compute vdem = (masktg * maskvel * dx * emiss).sum(x) ###
            vdem = self._vdem_multiply_then_sum_along(masktg, maskvel, dx, emiss, dim=x)
            return vdem


    @known_var(deps=['emiss', 'u', 'T', 'rcoords_logT', 'rcoords_vdop'])
    def get_vdem_interp(self):
        '''VDEM (intergrated along an axis), with interpolation (Matthias trick along T)
        See self.help('vdem') or help(self.get_vdem) for more details about vdems.

        Specific to this vdem var:
            ignores emiss contributions from very cold regions (log10(T) < self.vdem_logT_min).
        '''
        self._radiative_assert_single_component()

        U_NORM = 1e5  # converts from cgs to km/s. Not necessary, but helps avoid rounding errors(?)

        x = str(self.component)
        with self.using(units='cgs'):
            ### get relevant vals ###
            dx = self(f'd{x}')
            tg = self("T")
            ulos = - self("u", component=x) / U_NORM
            emiss = self('emiss')
            if self.vdem_ignores_photosphere == 'z=0':
                emiss = emiss * (emiss["z"] > 0)
            emiss = xr.where(tg > 10**(self.vdem_logT_min), emiss, 0)   # avoid contributions from very cold regions.

            ### compute masks and interpolation details ###
            logT = self('rcoords_logT')
            vdop = self('rcoords_vdop') / U_NORM
            dvdop = vdop.isel(vdop=1).item() - vdop.isel(vdop=0).item()
            # temperature mask (and interp correction details)
            masktg, xn = self.interp_correction(np.log10(tg), bins=logT, dim=x, log=True)
            # velocity mask everywhere outside of the bin (bin is from vdop-dvdop/2 to vdop+dvdop/2)
            maskvel = ulos >= vdop - dvdop / 2.0
            maskvel *= ulos < vdop + dvdop / 2.0

            ### do interpolation ###
            # emiss with interp correction weighting adjacent cells
            emiss1 = emiss.roll({x:1})
            emiss_interped = emiss * (1.0 - xn) + emiss1 * xn

            ### drop first point (roll() makes it bad) ###
            arrays = [masktg, maskvel, dx, emiss_interped]
            arrays = [a.isel({x: slice(1, None, None)}) if x in a.dims else a for a in arrays]

            ### compute vdem = (masktg * maskvel * dx * emiss).sum(x) ###
            vdem = self._vdem_multiply_then_sum_along(*arrays, dim=x)
            return vdem


    @known_var(deps=['emiss', 'u', 'T', 'rcoords_logT', 'rcoords_vdop'])
    def get_vdem_allinterp(self):
        """VDEM (intergrated along an axis), with interpolation (Matthias trick along T and u)
        See self.help('vdem') or help(self.get_vdem) for more details about vdems.

        Specific to this vdem var:
            ignores emiss contributions from very cold regions (log10(T) < self.vdem_logT_min).
        """
        self._radiative_assert_single_component()

        U_NORM = 1e5  # converts from cgs to km/s. Not necessary, but helps avoid rounding errors(?)

        x = str(self.component)
        with self.using(units='cgs'):
            ### get relevant vals ###
            dx = self(f'd{x}')
            tg = self("T")
            ulos = - self("u", component=x) / U_NORM
            emiss = self('emiss')
            if self.vdem_ignores_photosphere == 'z=0':
                emiss = emiss * (emiss["z"] > 0)
            emiss = xr.where(tg > 10**(self.vdem_logT_min), emiss, 0)   # avoid contributions from very cold regions.

            ### compute masks and interpolation details ###
            logT = self('rcoords_logT')
            vdop = self('rcoords_vdop') / U_NORM
            # temperature mask (and interp correction details)
            masktg, xn = self.interp_correction(np.log10(tg), bins=logT, dim=x, log=True)
            # velocity mask
            maskvel = self.los_correction(ulos, bins=vdop, dim=x)

            ### do interpolation ###
            # emiss with interp correction weighting adjacent cells
            emiss1 = emiss.roll({x:1})
            emiss_interped = emiss * (1.0 - xn) + emiss1 * xn

            ### drop first point (roll() makes it bad) ###
            arrays = [masktg, maskvel, dx, emiss_interped]
            arrays = [a.isel({x: slice(1, None, None)}) if x in a.dims else a for a in arrays]

            ### compute vdem = (masktg * maskvel * dx * emiss).sum(x) ###
            vdem = self._vdem_multiply_then_sum_along(*arrays, dim=x)
            return vdem
    
    # vdem looping details:
    # cls_behavior_attrs <-- intentionally not registered, because shouldn't affect results!
    #  it just affects internal behaviors and efficiency.
    #  instead, added to self._extra_kw_for_quantity_loader_call,
    #    so it can still be adjusted in the usual way, like self(var, vdem_loopdim=...)
    vdem_loopdim = simple_property('_vdem_loopdim', default=('int', 0.45, 'GB'),
        doc='''None, str, or (str, int, mode). Tells which dimension to loop over additionally during vdems.
        None --> computes vdem without looping.
            Conceptually simplest. But, internally builds array with vdop, logT, and maindims (e.g. x,y,z),
            which might be larger than DEFAULTS.RESULT_ARRAY_GBYTES_MAX and thus trigger MemorySizeError.
        'vdop' --> loop over each point along the vdop dimension; concatenate result.
        'logT' --> loop over each point along the logT dimension; concatenate result.
        str from self.maindims (e.g., 'x') --> loop over each point along that dimension;
            concatenate result (usually), but if it is the dim being integrated along, keep a running sum instead.
        'int' or 'sum' --> loop over the dimension being integrated along.
            No need to concatenate result! Instead, keeps a running sum during the loop.
        (str, int, mode) --> loop over the dimension indicated by str, but in chunks of the indicated size!
            mode can be:
                'size' --> number of points in the dimension.
                    E.g., ('logT', 5, 'size') does first 5 points along logT, then next 5, etc.
                'n' --> number of chunks (roughly)
                    E.g., ('logT', 5, 'n') does first 1/5 of logT points, then next 1/5, etc.
                    Not guaranteed to be exactly 5 chunks, due to rounding.
                'GB' --> size of chunk arrays in GB (approximately)
                    E.g., ('logT', 5, 'GB') picks chunk size for logT such that each chunk is 5 GB or less.''')

    _vdem_errmsg_if_too_big = \
        '''while computing vdem, multiplying arrays (before summing) would be too large!
        The limit is set by DEFAULTS.RESULT_ARRAY_GBYTES_MAX = {GBmax} GB.
        Predicted size: {nGB:.2f} GB, corresponding to dims with sizes (number of items):
            {dimsizes}.

        Options to fix this problem include any combination of the following:
            - adjust self.chunks to break up the problem along self.maindims.
                E.g., self(vdem_var, chunks=dict(x_size=5)) does the first 5 points along x,
                    then the next 5, then the next 5, etc, and joins at the end.
                using chunks also enables to use multiprocessing, E.g. self(..., ncpu=10).
                Use ncpu=None to use all available CPUs. (Up to number of cores on machine/node).

            - adjust self.vdem_loopdim to loop over an internal dimension.
                E.g., self(vdem_var, vdem_loopdim='logT') loops across logT dimension,
                    doing 1 point at a time, then joining at the end (after the sum).
                Another good option is vdem_loopdim='int', to loop across the dimension being integrated,
                    to keep a running sum and avoid the need to concatenate at the end.
                Also worth considering the default: vdem_loopdim=('int', 0.45, 'GB'),
                    which loops across chunks along the dimension being integrated,
                    ensuring that each chunk size is at most 0.45 GB
                        (if possible; else just do 1 point at a time.)

            - (simple but not recommended) increase DEFAULTS.RESULT_ARRAY_GBYTES_MAX.
                or, set it to None to disable this check entirely.
                (Warning: might crash machine if internal array is too big!!)'''

    def _vdem_multiply_then_sum_along(self, *arrays, dim):
        '''returns result of product of arrays then .sum(dim=dim).
        Equivalent to (arrays[0] * arrays[1] * ...).sum(dim=dim).

        But, internally, may loop over a dimension, depending on self.vdem_loopdim.
        See help(type(self).vdem_loopdim) for details.

        Also, before doing the product, checks if the array size would be too big,
            i.e. bigger than DEFAULTS.RESULT_ARRAY_GBYTES_MAX.
        If it would be too big, raise helpful MemorySizeError,
            with suggestions for how to fix the problem
            (e.g. adjusting self.chunks, self.vdem_loopdim, and/or DEFAULTS.RESULT_ARRAY_GBYTES_MAX).
        '''
        # [TODO] most of this can maybe be encapsulated into a more generic function...
        #   (if any non-vdem needs a similar looping behavior, could be worthwhile.)
        loop = self.vdem_loopdim
        if loop is None:  # simplest, but also most likely to be too big
            xarray_result_size_check(*arrays, errmsg=self._vdem_errmsg_if_too_big)
            result = xarray_sum(product(arrays), dim=dim, missing_dims='ignore')
            return result
        else:
            ## bookkeeping ##
            if isinstance(loop, str):
                loop = (loop, 1, 'size')
            # loopdimstr
            loopdimstr, loopsize, mode = loop
            _valid_loopdimstrs = (*self.maindims, 'logT', 'vdop', 'int', 'sum')
            if loopdimstr not in _valid_loopdimstrs:
                raise InputError(f"invalid loop dim str: {x!r}; expected one of {_valid_loopdimstrs}")
            if loopdimstr in ('int', 'sum'):
                x = dim   # x tells vdem internal loopdim. Might be 'logT', 'vdop' or a maindim (e.g., 'x', 'y', 'z')
            else:
                x = loopdimstr
            # size
            dim_sizes = xarray_max_dim_sizes(*arrays)
            _valid_modes = ('size', 'n', 'GB')
            if mode not in _valid_modes:
                raise InputError(f"invalid loop mode: {mode!r}; expected one of {_valid_modes}")
            if mode == 'size':
                size = loopsize
            elif mode == 'n':
                size = dim_sizes[x] // loopsize  # e.g. dimsize=110, n=25 --> size=4.
            elif mode == 'GB':
                full_GB = xarray_predict_result_size(*arrays, units='GB')
                # e.g. loopsize = 0.5 GB, full_GB = 2.3 --> size = int(dimsize / 5)
                size = int(dim_sizes[x] * min(1, loopsize / full_GB))  # min() in case loopsize > full_GB.
                if DEFAULTS.DEBUG >= 2:
                    print(f'_vdem_multiply_then_sum_along chose size={size} (of full={dim_sizes[x]}) '
                          f'for loopdim={x!r}, to make {full_GB * size/dim_sizes[x]:.3f} GB per chunk.')
            if size < 1:
                size = 1
            # slicers (based on size)
            if size == dim_sizes[x]:
                slicers = None  # no need to loop after all!
            elif size == 1:
                slicers = list(range(dim_sizes[x]))  # loop over each point
            else:
                slicers = []
                for i in range(0, dim_sizes[x], size):
                    slicers.append(slice(i, min(i+size, dim_sizes[x]), None))
            # print final looping decisions:
            if DEFAULTS.DEBUG >= 3:
                print(f'_vdem_multiply_then_sum_along using x={x!r}, size={size}, (due to mode={mode})')
            ## looping ##
            if slicers is None:  # not looping after all!
                xarray_result_size_check(*arrays, errmsg=self._vdem_errmsg_if_too_big)
                result = xarray_sum(product(arrays), dim=dim, missing_dims='ignore')
            elif x == dim:   # looping over the dimension being integrated along!
                for i, idx in enumerate(slicers):
                    arrays_i = [a.isel({x: idx}, drop=True) if x in a.dims else a for a in arrays]
                    if i == 0:
                        xarray_result_size_check(*arrays_i, errmsg=self._vdem_errmsg_if_too_big)
                        result = xarray_sum(product(arrays_i), dim=dim, missing_dims='ignore')
                    else:
                        result += xarray_sum(product(arrays_i), dim=dim, missing_dims='ignore')
            else:  # looping over any other dimension (must concat at the end)
                result = []
                for i, idx in enumerate(slicers):
                    arrays_i = [a.isel({x: idx}, drop=True) if x in a.dims else a for a in arrays]
                    if i == 0:
                        xarray_result_size_check(*arrays_i, errmsg=self._vdem_errmsg_if_too_big)
                    result.append(xarray_sum(product(arrays_i), dim=dim, missing_dims='ignore'))
            return result


    # # # MOMENTS # # #

    @known_pattern(r'(.+)_moments_(.+)', deps=[1])
    def get_moments(self, var, *, _match=None):
        """First three moments of a var, e.g., vdem or spectra. 
        I0 = (int(I du)) [erg/cm^2/s/sr]
        I1 = (int(I u du))/I0 [km/s]
        I2 = (int(I u^2 du))/I0-I1^2 [km/s]

        dim_moments_var --> self(var).pc.moments(dim=dim).
        e.g., vdop_moments_vdem --> self('vdem').pc.moments(dim='vdop')

        result is a Dataset with data_vars 'moment_0', 'moment_1', 'moment_2'.
        """
        dim, var, = _match.groups()
        arr = self(var)
        return arr.pc.moments(dim=dim)


    # # # Thermal + Instrumental Velocity # # #

    cls_behavior_attrs.register('w_instrumental_si', default=0.0)
    w_instrumental_si = simple_property('_w_instrumental_si', default=0.0,
        doc='''instrumental broadening for thermal velocity, in SI units.
        vtherm_instr = sqrt((kB T / m) + self.w_instrumental_si^2)''')

    @known_var
    def get_w_instrumental(self):
        '''instrumental broadening for thermal velocity, in self.units system.
        w_instrumental = self.w_instrumental_si, converted to self.units system.

        See also: vtherm_instr
        '''
        return xr.DataArray(self.w_instrumental_si * self.u('u', convert_from='si'))

    @known_var(deps=['Tjoule', 'm', 'w_instrumental'], aliases=['vth_instr', 'vthermal_instr'])
    def get_vtherm_instr(self):
        '''thermal velocity including instrumental broadening.
        vtherm_instr = sqrt((kB T / m) + w_instrumental^2)

        w_instrumental can be set via self.w_instrumental_si = value.
        '''
        return (self('Tjoule')  / self('m') + self('w_instrumental')**2)**0.5


    # # # G(T), G(T,n) # # #
    # contribution function(?)
    # depends on electron pressure or number density.

    # electron pressure and number density values determined by rcoords_Pe_cgs and rcoords_logD_cgs:
    cls_behavior_attrs.register('rcoords_Pe_cgs', default=1e15)
    rcoords_Pe_cgs = simple_property('_rcoords_Pe_cgs', default=1e15, 
            doc='''electron Pressure [cgs units] values, used by some MhdRadiativeLoader vars.
            E.g., used by G(T) when self.gofnt_mode=='pressure'.
            Can be a scalar, a 1D list or numpy array, or 1D xr.DataArray with dimension 'Pe'.''')
    @known_var
    def get_rcoords_Pe(self):
        '''electron Pressure values for G(T) for fixed pressure, in [self.units] system,
        along dimension 'P', with coords always in [cgs] units regardless of self.units.
        Determined by self.rcoords_Pe_cgs (which can be set directly), converted to [self.units].
        '''
        result = xr1d(self.rcoords_Pe_cgs, name='Pe', lenient=True)  # [cgs]
        return result * self.u("pressure", convert_from='cgs')  # [self.units]

    cls_behavior_attrs.register('rcoords_logD_cgs')
    rcoords_logD_cgs = simple_property('_rcoords_logD_cgs', default=np.arange(8,11,0.5), 
            doc='''log10(electron number density [cgs units]) values, used by some MhdRadiativeLoader vars.
            E.g., used by G(T,ne) when self.gofnt_mode=='density'.
            Can be a scalar, a 1D list or numpy array, or 1D xr.DataArray with dimension 'logD'.''')
    @known_var
    def get_rcoords_logD(self):
        '''log(electron number density) values for G(T,ne), with ne in [self.units] system,
        along dimension 'logD', with coords always telling log10(ne [cgs]) regardless of self.units.
        Determined by self.rcoords_logD_cgs (which can be set directly), converted to [self.units].
        '''
        result = xr1d(self.rcoords_logD_cgs, name='logD', lenient=True)  # log10([cgs])
        return result + np.log10(self.u("number_density", convert_from='cgs'))   # log10([self.units])

    # other G(T) settings:
    cls_behavior_attrs.register('gofnt_mode', default='pressure')
    GOFNT_MODE_OPTIONS = {'pressure': 'Compute G(T) for a fixed electron pressure',
                          'density': 'Compute G(T,ne)'
                          }
    gofnt_mode = simple_property('_gofnt_mode', default='pressure', validate_from='GOFNT_MODE_OPTIONS',
            doc='''Selects the G(T) calculation mode. See self.GOFNT_MODE_OPTIONS for options.''')
    
    cls_behavior_attrs.register('gofnt_interp_mode', default='interp')
    GOFNT_INTERP_MODE_OPTIONS = {
        'interp': (
            "Interpolate the emission measure x G(T) in temperature."
            "This mode uses 'Matthias trick' for temperature binning, providing a balance between speed and accuracy."
        ),
        'nointerp': (
            "No interpolation: "
            "Computes the emission measure x G(T) direct binning in both temperature and velocity without any interpolation. "
        ),
    }
    gofnt_interp_mode = simple_property('_gofnt_interp_mode', default='interp',
            validate_from='GOFNT_INTERP_MODE_OPTIONS',
            doc='''Selects the emission measure x G(T) calculation mode.
            See self.GOFNT_INTERP_MODE_OPTIONS for options.''')

    cls_behavior_attrs.register('gofnt_abundance', default='sun_coronal_2021_chianti')
    gofnt_abundance = simple_property('_gofnt_abundance', default='sun_coronal_2021_chianti',
            doc='''Abundance(?) to use for G(T) calculations.
            Passed directly to muse.instr.utils.chianti_gofnt_linelist via "abundance" kwarg.''')

    cls_behavior_attrs.register('gofnt_wavelength_range', default=[171.07, 171.08])
    gofnt_wavelength_range = simple_property('_gofnt_wavelength_range', default=[171.07, 171.08],
        doc='''Wavelength range (as [min, max]) (in [Angstrom] units) to use for G(T) calculations.
        Passed directly to muse.instr.utils.chianti_gofnt_linelist via "wavelength_range" kwarg.''')

    cls_behavior_attrs.register('rcoords_wavelength_A', default=171.07)
    rcoords_wavelength_A = simple_property('_rcoords_wavelength_A', default=171.07,
        doc='''Wavelength (in [Angstrom] units) used by some MhdRadiativeLoader vars.
        E.g., used in get_spectra().
        [TODO] can it be a 1D list/array, or is it required to be a scalar?''')
    
    
    # G(T) vars
    @known_pattern(r'GofT_(.+)_ion', deps=['rcoords_logT'],
                   attr_deps=[('gofnt_mode', {'pressure': 'rcoords_Pe', 'density': 'rcoords_logD'})])
    def get_Gofnt(self, var, *, _match=None):
        '''G(T,ne) from ChiantiPy and muse library for a given ion. E.g., GofT_fe_9_ion
        Always in [cgs] (erg*cm^3/s/sr) regardless of self.units.

        ion string (like 'fe_9') is passed into muse.instr.utils.chianti_gofnt_linelist,
            via ionList = [ionstr]. See that function for more details about available ions.

        "returns G(T,ne) and spectral line properties, including wavelength and transition probabilities." 
        [TODO] what does that mean?

        CAUTION: directly adjusts the value of self.rcoords_wavelength_A, based on result.
        '''
        ionstr, = _match.groups()

        # finds in Chiantypy the line list with the properties listed above
        if self.gofnt_mode == "pressure":
            line_list = muse_instr_utils.chianti_gofnt_linelist(
                temperature = 10**self('rcoords_logT'),
                pressure = self('rcoords_Pe', units='cgs'),  # ChiantiPy wants cgs
                abundance = self.gofnt_abundance,
                wavelength_range = self.gofnt_wavelength_range,
                ionList = [ionstr],
                minimum_abundance = None,
            )

            # Selecting the strongest line
            line_list["gofnt_max"] = line_list.gofnt.sum(['logT']) 
        elif self.gofnt_mode == 'density':
            line_list = muse_instr_utils.chianti_gofnt_linelist(
                temperature = 10**self('rcoords_logT'),
                density = 10**self('rcoords_logD', units='cgs'),   # ChiantiPy wants cgs
                abundance = self.gofnt_abundance,
                wavelength_range = self.gofnt_wavelength_range,
                ionList = [ionstr],
                minimum_abundance = None,
            )

            # Selecting the strongest line
            line_list["gofnt_max"] = line_list.gofnt.sum(['logT']) 
        else:
            assert False, f"coding error if reached this line; invalid gofnt_mode: {self.gofnt_mode!r}"
        sort_index = np.argsort(-line_list.gofnt_max, 
                                axis=line_list.gofnt_max.get_axis_num('trans_index'))
        line_list_sort = line_list[dict(trans_index=sort_index)]
        line_list_sort_c = line_list_sort.isel(trans_index=0)
        # SE - it's weird for a known_var to alter a behavior_attr
        # JMS yes ... but it's convenient here.
        # [TODO] long-term, better to include directly in output somehow (e.g., array.attrs?)
        #    (SE - for now it is okay. left a note in docstring to let user know the attr will be adjusted.)
        self.rcoords_wavelength_A = line_list_sort_c.squeeze().wvl.values
        return line_list_sort_c

    @known_pattern(r'GofT_(.+)_ion_atmos', deps=['T', {0: 'GofT_{group0}_ion'}],
                   attr_deps=[('gofnt_mode', {'density': 'ne'})])
    def get_Gofnt_atmos(self, var, *, _match=None):
        '''Interpolated G(T) with temperature, for a given ion.
        Always in [cgs] (erg*cm^3/s/sr) regardless of self.units.
        For details about available ions, see muse.instr.utils.chianti_gofnt_linelist
        '''
        ionstr, = _match.groups()
        with self.using(units='cgs'):
            goftn = self(f'GofT_{ionstr}_ion').gofnt * self.emiss_norm
            tg = self('T')
            if self.gofnt_mode == "pressure":
                return goftn.interp(logT=np.log10(tg))
            elif self.gofnt_mode == "density": 
                nel = self('ne')
                return goftn.interp(logT=np.log10(tg),logD=np.log10(nel))
            else:
                assert False, f"coding error if reached this line; invalid gofnt_mode: {self.gofnt_mode!r}"

    @known_pattern(r'GofT_(.+)_ion_em',
                   attr_deps=[('gofnt_interp_mode', {'interp': [{0: 'GofT_{group0}_ion_em_interp'}],
                                                   'nointerp': [{0: 'GofT_{group0}_ion_em_no_interp'}]})])
    def get_Gofnt_em(self, var, *, _match=None):
        '''Emission * G(T) for a given ion. Results always in [cgs] (erg/cm^2/s/sr).
        For details about available ions, see muse.instr.utils.chianti_gofnt_linelist
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        ionstr, = _match.groups()

        if self.gofnt_interp_mode == "interp": 
            return self(f"GofT_{ionstr}_ion_em_interp")
        elif self.gofnt_interp_mode == "nointerp": 
            return self(f"GofT_{ionstr}_ion_em_no_interp")
        else:
            assert False, f"coding error if reached this line; invalid gofnt_interp_mode: {self.gofnt_interp_mode!r}"

    @known_pattern(r'GofT_(.+)_ion_em_no_interp', deps=['emiss', {0: 'GofT_{group0}_ion_atmos'}])
    def get_Gofnt_em_nointerp(self, var, *, _match=None):
        '''Emission * G(T) for a given ion. Results always in [cgs] (erg/cm^2/s/sr).
        For details about available ions, see muse.instr.utils.chianti_gofnt_linelist
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        ionstr, = _match.groups()
        with self.using(units='cgs'):      
            goftn = self(f'GofT_{ionstr}_ion_atmos')
            em = self('emiss')
            return goftn * em

    @known_pattern(r'GofT_(.+)_ion_em_interp', deps=['emiss', 'T', {0: 'GofT_{group0}_ion'}])
    def get_Gofnt_em_interp(self, var, *, _match=None): # uhm .... not sure why, but for not sharp temperature gradient has an artifact ... 
        '''Emission * G(T) for a given ion. Results always in [cgs] (erg/cm^2/s/sr).
        For details about available ions, see muse.instr.utils.chianti_gofnt_linelist
        '''
        self._radiative_assert_single_component()
        ionstr, = _match.groups()
        x = str(self.component)
        with self.using(units='cgs'):      
            goftn_atmos = self(f'GofT_{ionstr}_ion_atmos')
            emiss = self('emiss')
            emiss = emiss * (emiss["z"] > 0)  # [TODO] connect to "vdem_ignores_photosphere" option or something like it

            emiss1 = emiss.roll({x:1})
            # removing emission from first cell due to roll
            emiss1[{x:0}] = 0.0

            masktg, xn = self.interp_correction(np.log10(self('T')), bins=self('rcoords_logT'), dim=x, log=True)
            emiss_interped = emiss * (1.0 - xn) + emiss1 * xn  # emiss with interp correction weighting adjacent cells

            result = masktg * goftn_atmos * emiss_interped
            return result.sum(dim='logT')

    @known_var
    def get_h_he_absorb(self, wavelength=None):
        '''Opacities at wavelength=self.rcoords_wavelength_A.
        from hydrogen and helium bound free absorption (Anzer & Heinzel, 2005)
        '''
        rhe = 0.1
        opa1d = self('chianti_opa1d_table')
        arr = (opa1d.h) * self('opac_h') + rhe * ((1 - opa1d.hei - (1-opa1d.hei-opa1d.he)) *
                                                  self('opac_hei') + (opa1d.hei) * self('opac_heii'))
        arr[arr < 0] = 0
        return arr

    @known_var
    def get_chianti_opa1d_table(self, tabname='chianti'):
        '''Ionization state table from ChiantiPy.
        result is an xr.Dataset with data_vars 'h', 'he', 'hei',
            telling the H, HeI, and HeII ionization fractions, respectively.
        '''
        h = ch.Ioneq.ioneq(1)
        h.load(tabname)
        he = ch.Ioneq.ioneq(2)
        he.load(tabname)
        opa1d = xr.Dataset()
        opa1d['he'] = xr.DataArray(he.Ioneq[0, :], coords={"logT": np.log10(he.Temperature)}, dims="logT")
        opa1d['hei'] = xr.DataArray(he.Ioneq[1, :], coords={"logT": np.log10(he.Temperature)}, dims="logT")
        opa1d['h'] = xr.DataArray(h.Ioneq[0, :], coords={"logT": np.log10(h.Temperature)}, dims="logT")
        return opa1d

    @known_var
    def get_opac_h(self):
        '''H opacity at self.rcoords_wavelength_A.
        See Anzer & Heinzel, 2005 for details. 
        '''
        ghi = 0.99
        o0 = 7.91e-18  # cm^2
        ohi = 0
        if self.rcoords_wavelength_A <= 912: # Amstrong
            ohi = o0 * ghi * (self.rcoords_wavelength_A / 912.0)**3
        return ohi

    @known_var
    def get_opac_hei(self):
        '''HeI opacity at self.rcoords_wavelength_A.
        See Anzer & Heinzel, 2005 for details. 
        '''
        c = [-2.953607e1, 7.083061e0, 8.678646e-1,
             -1.221932e0, 4.052997e-2, 1.317109e-1,
             -3.265795e-2, 2.500933e-3]
        ohei = 0
        if self.rcoords_wavelength_A <= 504: # Amstrong
            for i, cf in enumerate(c):
                ohei += cf * (np.log10(self.rcoords_wavelength_A))**i
            ohei = 10.0**ohei
        return ohei

    @known_var
    def get_opac_heii(self):
        '''HeII opacity at self.rcoords_wavelength_A.
        See Anzer & Heinzel, 2005 for details. 
        '''
        gheii = 0.85
        o0 = 7.91e-18  # cm^2
        oheii = 0
        if self.rcoords_wavelength_A <= 228: # Amstrong
            oheii = 16 * o0 * gheii * (self.rcoords_wavelength_A / 912.0)**3
        return oheii

    @known_var(deps=['r', 'h_he_absorb', 'T'],load_across_dims=['component'])
    def get_tau(self):
        '''Optical depth along a line of sight.
        Result is always in [cgs] units, regardless of self.units.
        [TODO] formula + explain what is happening inside here with all the interp() calls..
        '''
        # self._radiative_assert_single_component()  # <-- no need; guaranteed by load_across_dims=['component'].
        x = str(self.component)
        with self.using(units='cgs'):   
            rho = self("r")
            grph = (self.elements.n_per_nH() * self.elements.m * self.u('amu')).sum() 
            h_he_absorb = self('h_he_absorb')
            absorption = h_he_absorb.interp(
                logT=np.log10(self('T'))
                ).fillna(h_he_absorb.interp(logT=np.log10(self('T'))).max())

            # Assume ds is a 1D array of distances along the LOS, and axis is the LOS axis (0, 1, or 2)
            ds = self(f'd{x}')

            # Compute the integrand
            integrand = (absorption * ds * rho) / grph

            # Cumulative sum along the LOS axis
            # return integrand.cumsum(dim=x,direction='reverse')
            return integrand.sortby(x, ascending=False).cumsum(x).sortby(x)


    @known_pattern(r'spectra_(.+)_ion_prof',
                   deps=['vtherm_instr', 'u', 'rcoords_vdop', {0: 'GofT_{group0}_ion_em'}],
                   attr_deps=[('emiss_mode', {'notrac_opa': 'tau', 'trac_opa': 'tau'})])
    def get_spectra(self, var, *, _match=None): # this one could be break in two functions, one with and the other without abs. 
        '''Synthetic spectra for a given ion. Always in [cgs] units, regardless of self.units.
        Units erg/cm^2/s/sr/Angs

        Result depends on self.rcoords_vdop_kms and self.rcoords_wavelength_A, which can be set directly.
        Result varies along the 'vdop' dimension which indicates doppler velocity (in km/s).

        [TODO] formula/details
        '''
        ionstr, = _match.groups()
        self._radiative_assert_single_component()
        x = str(self.component)
        with self.using(units='cgs'):
            # force noopa emiss mode, when getting _ion_em
            emiss_mode = self.emiss_mode
            if "_opa" in emiss_mode:
                emiss_mode = emiss_mode.replace("_opa", "_noopa")
            em = self(f'GofT_{ionstr}_ion_em', emiss_mode=emiss_mode)
            sig = self('vtherm_instr') / 1e5 # Conversion from cgs to km/s
            vlos = self('u') / 1e5 # Conversion from cgs to km/s
            vdop = self('rcoords_vdop') / 1e5 # Conversion from cgs to km/s
            wvl = doppler_to_lambda(self.rcoords_vdop_kms, self.rcoords_wavelength_A)  # from km/s to Angstrom
            with self.maintaining('wavelength'):
                I_slice = []
                for i_v, v_arr in enumerate(vdop):  # looping because "tau" not is ready to handle 'vdop' dim.
                    if "_opa" in self.emiss_mode:
                        self.rcoords_wavelength_A = wvl[i_v]
                        em_opa = em * np.exp(-self("tau"))
                    else:
                        em_opa = em
                    phi = np.exp(-0.5 * ((v_arr - vlos) / sig)**2) / (np.sqrt(2 * np.pi) * sig)
                    dlos = self(f'd{x}') 
                    I_slice.append((em_opa * phi * dlos).sum(dim=x))
            int = xr.concat(I_slice,dim="vdop")
            int = int.assign_coords(wavelength=("vdop",wvl))
        return int


    # # # INTERPOLATION CORRECTIONS # # #

    @format_docstring(_static_helper_doc=interp_correction.__doc__, sub_ntab=2)
    def interp_correction(self, array_or_var, bins, dim=None, *, log=False):
        """
        Compute interpolation masks and normalization factors for a variable (e.g., "T")
        for use in DEM/VDEM binning with or without logarithmic scaling.

        Works just like the "static" method (not attached to this class),
        but with a few extra convenient features here:
            (1) first arg can be array (as in static method), OR a var.
                if it is a var (i.e., a str), use array=self(var)
            (2) dim does not need to be provided;
                if not provided, use dim=str(self.component).

        Docstring from "static" method copied below, for convenience.
        -------------------------------------------------------------
            {_static_helper_doc}
        """
        if isinstance(array_or_var, str):
            var = array_or_var
            array = self(var)
        else:
            array = array_or_var
        if dim is None:
            dim = str(self.component)
        return interp_correction(array=array, bins=bins, dim=dim, log=log)

    @format_docstring(_static_helper_doc=los_correction.__doc__, sub_ntab=2)
    def los_correction(self, array_or_var, bins, dim=None, *, log=False):
        """
        Compute line-of-sight (LOS) correction masks and normalization factors for a variable (e.g., "u")

        Works just like the "static" method (not attached to this class),
        but with a few extra convenient features here:
            (1) first arg can be array (as in static method), OR a var.
                if it is a var (i.e., a str), use array=self(var)
            (2) dim does not need to be provided;
                if not provided, use dim=str(self.component).
        """
        if isinstance(array_or_var, str):
            var = array_or_var
            array = self(var)
        else:
            array = array_or_var
        if dim is None:
            dim = str(self.component)
        return los_correction(array=array, bins=bins, dim=dim, log=log)


    # # # VDEM PIPELINE # # #

    def vdem_pipeline(self, *, 
                      los_dim='z', 
                      iz0 = 50, 
                      tg_percent = 0.1, 
                      dlogT = 0.1,
                      mintg_cut = 4.6, 
                      maxtg_cut = 7.7, 
                      tg_bins = 60,
                      ulos_bin = 60,
                      vel_percent = 0.1,
                      dvdop = 10,
                      minvel_cut = -3000,
                      maxvel_cut = 3000,
                      modelname = '',
                      zarr_version = 2,
                      chunks=256,
                      ncpu=12,
                      author,
                      ):
        '''make some standard vdem plots.

        CAUTION: creates and DELETES a directory named _pc_caches_zarr_saving.zarr, without warning.
            If you happened to have a directory like that before running this pipeline,
            the pipeline will destroy whatever is inside of it (via shutil.rmtree).
            (Hopefully the name is unique enough that this won't cause any issues though...)

        [TODO] info about all of the inputs.
        '''

        import matplotlib.pyplot as plt
        from matplotlib import colors
        from dateutil.tz import gettz

        WEST = gettz("US/Western")

        chosen_code = type(self).__name__.replace("Calculator","")
        
        self.units = 'cgs'
        self.emiss_norm = 1e27 
        self.component = los_dim
        top = np.argmax(self.get_maindims_coords()['z'])
        if iz0 is None:
            iz0 = np.argmin(np.abs(self.get_maindims_coords()['z']))
        if top < iz0:
            sl = slice(top,iz0)
        else:
            sl = slice(iz0,top)

        self.slices = ({'z':sl})
        tg = self("T")
        ulos = self("u", units = 'si') / 1e3 # to km/s

        # The histogram allows to find the temperature and velocity limits
        fig, ax = plt.subplots(1, 2, figsize=(12, 6))
        hist_values = np.log10(tg).plot.hist(density=True, bins=tg_bins, ax=ax[0])

        maxtg = (
                np.ceil(
                    np.max(hist_values[1][np.where(hist_values[0] > np.max(hist_values[0]) * tg_percent / 100.0)])
                    / dlogT
                )
                * dlogT
            )
        mintg = (
                np.floor(
                    np.min(hist_values[1][np.where(hist_values[0] > np.max(hist_values[0]) * tg_percent / 100.0)])
                    / dlogT
                )
                * dlogT
            )
        if mintg_cut is not None:
            mintg = np.max([mintg, mintg_cut])
        if maxtg_cut is not None:
            maxtg = np.min([maxtg, maxtg_cut])

        hist_values = ulos.plot.hist(density=True, bins=ulos_bin, ax=ax[1])
        fig.tight_layout()
        fig.savefig(
            f"T_ulos_hist_{chosen_code}_{modelname}_{author}_{datetime.datetime.now(WEST).date()!s}_{self.snap}.png"
        )
        
        maxvel = (
                np.ceil(
                    np.max(hist_values[1][np.where(hist_values[0] > np.max(hist_values[0]) * vel_percent / 100.0)])
                    / dvdop
                )
                * dvdop
            )
        minvel = (
                np.floor(
                    np.min(hist_values[1][np.where(hist_values[0] > np.max(hist_values[0]) * vel_percent / 100.0)])
                    / dvdop
                )
                * dvdop
            )
        if minvel_cut is not None:
            minvel = np.max([minvel, minvel_cut])
        if maxvel_cut is not None:
            maxvel = np.min([maxvel, maxvel_cut])
        
        self.rcoords_logT = np.arange(mintg, maxtg, dlogT)
        self.rcoords_vdop_kms = np.arange(minvel, maxvel, dvdop)
        self.tabin.extrapolate_kind = "constant"

        vdem = self('vdem', chunks=dict(x=chunks), ncpu=ncpu)
        mom = vdem.pc.moments(dim='vdop')
        fig, ax = plt.subplots(1, 3, figsize=(12, 6))
        mom.moment_0.sum(dim='logT').plot.imshow(norm=colors.LogNorm(vmin=1e-5,vmax=1e5), ax=ax[0])
        mom.moment_1.sum(dim='logT').plot.imshow(ax=ax[1], cmap="bwr")
        mom.moment_2.sum(dim='logT').plot.imshow(ax=ax[2])
        fig.tight_layout()
        fig.savefig(
            f"vdem_moment_{chosen_code}_{modelname}_{author}_{datetime.datetime.now(WEST).date()!s}_{self.snap}.png"
        )

        vdem_cut = self('vdem', 
                        slices=dict(z=slice(iz0, iz0+5)),
                        vdem_logT = (0, np.arange(3.0,4.5,0.1)),
                        rcoords_vdop_kms=np.arange(-1.0e1,1.e1,1),
                        vdem_mode='nointerp',
                        vdem_ignores_photosphere=False,
                        vdem_loopdim=None,
                        chunks=dict(x=chunks),
                        ncpu=ncpu,
                        component='z',
                        )

        mom = vdem_cut.pc.moments(dim='vdop')
        fig, ax = plt.subplots(1, 2, figsize=(12, 6))
        mom.moment_0.sum(dim='logT').plot(ax=ax[0])
        mom.moment_1.sum(dim='logT').plot(vmin=-5,vmax=5,cmap='bwr', ax=ax[1])
        ax[1].set_title("Doppler velocity (positive must be downward)")
        fig.tight_layout()
        fig.savefig(
            f"vdem_moment_ph_{chosen_code}_{modelname}_{author}_{datetime.datetime.now(WEST).date()!s}_{self.snap}.png"
        )

        add_history(vdem, locals(), self.vdem_pipeline)
        # save array! need to do a trick with saving it temporarily, then loading, then re-saving,
        #  to avoid strange errors with zarr saving metadata. Not sure why, yet.
        #  caution: creates and deletes _pc_caches_zarr_saving.zarr directory, without warning.
        #vdem.attrs["behavior"] = self.behavior   #<-- [TODO] causes save failure if self.behavior contains arrays.
        if os.path.exists("_pc_caches_zarr_saving.zarr"):
            shutil.rmtree("_pc_caches_zarr_saving.zarr")
        vdem = _xarray_save_prep(vdem)
        vdem0 = vdem[0]
        vdem0.to_zarr("_pc_caches_zarr_saving.zarr", zarr_version=zarr_version)
        vdem_temp0 = xr.open_zarr("_pc_caches_zarr_saving.zarr", zarr_version=zarr_version).compute()
        vdem0 = xr.Dataset()
        vdem0["vdem"] = vdem_temp0.vdem
        vdem0.attrs = vdem[0].attrs
        vdem0.x.attrs["long_name"] = "X"
        vdem0.y.attrs["long_name"] = "Y"
        vdem0.x.attrs["units"] = "cm"
        vdem0.y.attrs["units"] = "cm"
        vdem0.vdem.attrs["units"] = "1e27 / cm5"
        vdem0.vdem.attrs["description"] = "DEM(T,vel,x,y)"
        vdem0.vdop.attrs["long_name"] = r"v$_{Doppler}$"
        vdem0.vdop.attrs["units"] = "km/s"
        vdem0.logT.attrs["long_name"] = r"log$_{10}$(T)"
        vdem0.logT.attrs["units"] = r"log$_{10}$ (K)"
        vdem0.to_zarr(
            f"vdem_{chosen_code}_{modelname}_los{los_dim}_{author}_{datetime.datetime.now(WEST).date()!s}_{self.snap}.zarr", zarr_version = zarr_version
        )
        shutil.rmtree("_pc_caches_zarr_saving.zarr")
        return vdem


def add_history(ds: xr.Dataset, local_vars: dict, func: Callable) -> None:
    """
    Add a history entry to a dataset.

    Parameters
    ----------
    ds : `xarray.Dataset`
        Dataset to update.
    local_vars : `dict`
        Local variables from the calling function.
    func : `Callable`
        Function being recorded in the history.
    """
    string_vals = []
    for arg, value in local_vars.items():
        if arg in inspect.signature(func).parameters:
            if isinstance(value, xr.Dataset | xr.DataArray | np.ndarray):
                if isinstance(value, np.ndarray) and value.shape in [(), (1,)]:
                    string_vals.append(f"{arg}={value.tolist()}")
                elif isinstance(value, xr.DataArray) and value.size == 1:
                    string_vals.append(f"{arg}={value.values.tolist()}")
                else:
                    string_vals.append(f"{arg}={arg}")
            else:
                string_vals.append(f"{arg}={value}")

    history_entry = f"{func.__name__}({', '.join(string_vals)})"
    if "HISTORY" in ds.attrs:
        if isinstance(ds.attrs["HISTORY"], list):
            ds.attrs["HISTORY"].append(history_entry)
        else:
            ds.attrs["HISTORY"] = [ds.attrs["HISTORY"], history_entry]
    else:
        ds.attrs["HISTORY"] = [history_entry]

    today = datetime.datetime.now(tz=datetime.timezone.utc)
    if "date created" in ds.attrs:
        ds.attrs["date modified"] = today.strftime("%d-%b-%Y")
    else:
        ds.attrs["date created"] = today.strftime("%d-%b-%Y")
