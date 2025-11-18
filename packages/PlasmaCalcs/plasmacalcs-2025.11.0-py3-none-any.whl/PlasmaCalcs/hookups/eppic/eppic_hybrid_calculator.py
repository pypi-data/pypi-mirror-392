"""
File Purpose: EppicHybridCalculator, for outputs from eppic hybrid simulations.
"""

import xarray as xr

from .eppic_calculator import EppicCalculator
from ...dimensions import IONS
from ...errors import FluidValueError, LoadingNotImplementedError
from ...tools import (
    simple_property,
    xarray_sel,
)

class EppicHybridCalculator(EppicCalculator):
    '''
    EppicHybridCalculator is a subclass of EppicCalculator that is designed to
    handle hybrid simulations in EPPIC. It provides methods for loading and
    processing data specific to hybrid simulations.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hybrid = True

    @known_var(load_across_dims=['fluid'])
    def get_distribution_type(self):
        '''distribution type: DataArray of strings: 'electron', 'ion', or 'neutral'
        (useful internally for handling electrons differently,
            since electrons are fluid while ions are PIC particles.)
        '''
        if self.fluid.is_electron():
            return xr.DataArray('electron')
        elif self.fluid.is_ion():
            return xr.DataArray('ion')
        elif self.fluid.is_neutral():
            return xr.DataArray('neutral')
        else:
            raise FluidValueError(f'expected electron, ion, or neutral fluid; got {self.fluid}')

    @known_var(partition_across_dim=('fluid', 'distribution_type'))
    def get_deltafrac_n(self, *, distribution_type):
        '''normalized density perturbation. deltafrac_n = (n - n0) / n0.
            For hybrid simulations, electron density is the sum of the ion densities  
        '''
        # [TODO][EFF] maybe cache n for ions if recently got it for all ions,
        #    to avoid recalculating, in the "common" case of "get n for all species"...
        if distribution_type == 'electron':
            n0 = self.get_n0()
            n = self('sum_fluids_n', fluid=IONS)
            return (n - n0) / n0
        else:
            return super().get_deltafrac_n()

    @known_var(partition_across_dim=('fluid', 'distribution_type'))
    def get_u(self, *, distribution_type, _ne=None):
        '''velocity. for non-electrons: u = flux / n
        
        For electrons, it comes from the momentum equation for u_e, neglecting du_e/dt:
            The electron momentum equation looks like:
                du_e/dt = -grad(Pe)/(me ne) + (qe/me) (E + u_e x B) - nu_en (u_e - u_n)
            Dropping du_e/dt enables to solve for u_e, using some vector identities.
            Will also ignore u_n (the implementation asserts it is 0).
            Without pressure term, the result would be:
                u_e = (1/(1+Ke^2)) * ((Ke/|B|) * E + (Ke^2/|B|^2) * E x B),
                where Ke = kappae = (qe |B|) / (me nu_en).
            Including the pressure term is "easy", it can be joined with E in the original equation:
                du_e/dt = (qe/me) (E_eff + u_e x B) - nu_en (u_e - u_n), where
                E_eff = E - grad(Pe)/(ne qe).
            Meaning, the full result will be:
                u_e = (1/(1+Ke^2)) * ((Ke/|B|) * E_eff + (Ke^2/|B|^2) * E_eff x B)

        [EFF] optionally, can provide ne as _ne to avoid recalculating it, if already known.
        '''
        if distribution_type == 'electron':
            # assert u_n = 0
            u_n = self('u_n')
            if not (u_n == 0).all():
                raise LoadingNotImplementedError('get_flux for electrons when u_netural != 0')
            # evaluate formula
            n = self('n') if _ne is None else _ne
            # [EFF] calculate E_eff & B first, to avoid recalculating them multiple times.
            #   will need all components, even if len(self.component)==1,
            #   because internally will calculate E AND E cross B
            with self.using(component=None):
                B = self('B')
                E = self('E')
                P = n * self.u('kB') * self('T')
                E_from_P = self.gradient(P) / (n * self('q'))
                E_eff = E - E_from_P
            mod_B = self('mod_B', _B=B)
            skappa = self('skappa')
            E_eff__x = xarray_sel(E_eff, component=self.component)  # E_eff with self.component component(s)
            E_eff_cross_B__x = self('Eeff_cross_B', _Eeff=E_eff, _B=B)
            # ^ could have done self.cross_product(E_eff, B) for full result (all components)
            #   but the way used above enables self to manage components nicely,
            #   e.g. if only 1 component in self.component, result will compute only that component, too.
            u = (1/(1 + skappa**2)) * ((skappa/mod_B) * E_eff__x + (skappa**2/mod_B**2) * E_eff_cross_B__x)
            return u
        else:
            return super().get_u()

    @known_var(partition_across_dim=('fluid', 'distribution_type'))  # [TODO] deps (for electrons)
    def get_flux(self, *, distribution_type):
        '''flux. (for non-electrons: directly from EPPIC. for electrons: from momentum equation)

        For electrons, get u from momentum equation for u_e, neglecting du_e/dt.
        See self.help('u') (or help(self.get_u)) for more details.
        Then, flux_e = n_e * u_e
        '''
        if distribution_type == 'electron':
            n = self('n')
            u = self('u', _ne=n)
            return n * u
        else:
            return super().get_flux()
    
    @known_var(partition_across_dim=('fluid', 'distribution_type'))
    def get_n0(self, *, distribution_type):
        '''background density. (directly from Eppic.)
        For hybrid simulations, electron density is the sum of the ion densities  
        note: as with all other quantities, this will be output in [self.units] unit system;
            numerically equal to eppic.i value if using 'raw' units.
        '''
        if distribution_type == 'electron':
            return self('sum_fluids_n0', fluid=IONS)
        else:
            return super().get_n0()

    cls_behavior_attrs.register('_Te_fix_factor', default=2/3)
    _Te_fix_factor = simple_property('_Te_fix_factor_', default=2/3,
        doc='''factor to multiply electron temperature by, to correct for issue in hybrid EPPIC.
        (if hybrid EPPIC "temperature" output gets fixed, can set this to 1,
        and maybe pick a different default / fancier behavior to try to distinguish whether
            you are working with a pre-fix output or post-fix output,...
            maybe based on file date for the snapshot files? Or, some other flag in eppic.i...)''')
        
    @known_var(partition_across_dim=('fluid', 'distribution_type'), aliases=['temp'])
    def get_T(self, *, distribution_type):
        ''' temperature in Kelvin.

        For electrons, just loads 'temperature' from snapshot.
            NOTE: also, multiplies by self._Te_fix_factor, default 2/3,
                to account for issue with "temperature" outputs in hybrid EPPIC.
        For ions, equivalent to rmscomps_Ta.
            (Use self.T_indim_only=True if you want to ignore Ta_z in 2D sim)
        '''
        # [TODO] actually, should probably define get_Ta_or_Tajoule for electrons,
        #    since that is the "base" var in super().
        #    e.g. I think Ta for electrons could just return 'temperature' (without varying across component);
        #    that might make it just work, but it might also take some debugging to get it right.
        #    - SE (2025/05/07)
        if distribution_type == 'electron':
            result = self.load_maindims_var_across_dims('temperature', dims=['snap']) / self.u('kB')
            result = result * self._Te_fix_factor
            return result
        else:
            return super().get_T()
    
    @known_var(partition_across_dim=('fluid', 'distribution_type'))
    def get_T_box(self, *, distribution_type):  # [TODO] deps (for electrons)
        '''temperature of the entire simulation box, as if full of particles,
        and observed by something that could not resolve the individual cells.
        Equivalent: rmscomps(Ta_from_moment2).

        Ignores Ta components for directions in which the box has no extent.

        NOTE: electron temperatures are handled carefully, via the description above.
            Since we only know the isotropic T for electrons in each cell,
            the formula to get T_box for electrons is a bit more complicated:

            T_x = nmean_T + m * (nmean_(u_x^2) - nmean_(u_x)^2)
            T_box = rmscomps(T), e.g.:
                if 3D in x,y,z: sqrt(T_x^2 + T_y^2 + T_z^2) / sqrt(3)
                if 2D in x,y:   sqrt(T_x^2 + T_y^2) / sqrt(2)
            where nmean is the density-weighted mean over the entire box,
            i.e. mean(n * quantity) / mean(n).

            see Evans+2025 Appendix C for more details, including the derivation.
        '''
        if distribution_type == 'electron':
            ## naive implementation:
            # return self('mean_T')  # Te is isotropic for hybrid eppic --> T_box is just mean_T.

            ## careful implementation (see Evans+2025 Appendix C)
            with self.using(component=self.maindims):   # e.g., ignore u_z if 2D in x,y
                # [TODO][EFF] respect self.stats_dimpoint_wise for nmean computations.
                #   (useful if arrays are very large.)
                T = self('T')
                m = self('m')
                n = self('n')
                u = self('u', _ne=n)
                n0 = n.mean(dim=self.maindims)
                nmean_T = (n * T).mean(dim=self.maindims) / n0
                nmean_ux2 = (n * u**2).mean(dim=self.maindims) / n0
                nmean_ux = (n * u).mean(dim=self.maindims) / n0
                Tx = nmean_T + m * (nmean_ux2 - nmean_ux**2)
                return self.rmscomps(Tx)
        else:
            return super().get_T_box()
