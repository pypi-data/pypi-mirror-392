"""
File Purpose: loading single-fluid Muram quantities related to Equation Of State (EOS).
"""
import os

from ...errors import SnapValueError
from ...mhd import MhdEosLoader
from ...tools import simple_property, alias
from ...defaults import DEFAULTS

''' --------------------- MuramEosLoader--------------------- '''

class MuramEosLoader(MhdEosLoader):
    '''single-fluid Bifrost quantities related to Equation of State (EOS): ne, T, P.

    The implementation here assumes tables available at table=self.tabin[var],
        for var='ne', 'T', or 'P', and each having a table.interp(r=r, e=e) method,
        which gives value of var in 'raw' units.
    '''

    # non-aux functionality is inherited from MhdEosLoader.
    # 'aux' functionality is implemented here: read directly from aux files.

    EOS_MODE_OPTIONS = {**MhdEosLoader.EOS_MODE_OPTIONS,
        'aux': '''read directly from aux files for eosP, eosT, and eosne.'''
    }

    def _all_eos_aux_files_exist(self):
        '''returns whether eos aux files (eosP, eosT, and eosne) exist for all snaps in self.'''
        try:
            loadable = self.directly_loadable_vars()
        except SnapValueError:
            return False  # [TODO] this is overly restrictive...
        else:
            return all(var in loadable for var in ('eosT', 'eosP', 'eosne'))

    def _default_eos_mode(self):
        '''default for how to handle "Equation of State" related variables (ne, T, P).
        (provides default value for self.eos_mode.)

        result will be 'aux' if files for 'eosT', 'eosP', and 'eosne' exist for each snap,
        else 'table' if 'tabparams.in' file exists,
        else 'ideal'.
        '''
        if self._all_eos_aux_files_exist():
            return 'aux'
        elif os.path.isfile(os.path.join(self.dirname, 'tabparams.in')):
            return 'table'
        else:
            return 'ideal'

    # tell super().get_ne to use self('ne_aux') if eos_mode=='aux':
    _EOS_MODE_TO_NE_VAR = {**MhdEosLoader._EOS_MODE_TO_NE_VAR, 'aux': 'ne_aux'}

    # tell super().get_T to use self('T_aux') if eos_mode=='aux':
    _EOS_MODE_TO_T_VAR = {**MhdEosLoader._EOS_MODE_TO_T_VAR, 'aux': 'T_aux'}

    # tell super().get_P to use self('P_aux') if eos_mode=='aux':
    _EOS_MODE_TO_P_VAR = {**MhdEosLoader._EOS_MODE_TO_P_VAR, 'aux': 'P_aux'}

    @known_var(dims=['snap'])
    def get_ne_aux(self):
        '''electron number density, from 'eosne' file.'''
        ufactor = self.u('n', convert_from='cgs')
        return self.load_maindims_var_across_dims('eosne', u=ufactor, dims=['snap'])

    @known_var(dims=['snap'])
    def get_T_aux(self):
        '''temperature, from 'eosT' file.'''
        # note: multifluid T_aux assumes same T for all fluids.
        return self.load_maindims_var_across_dims('eosT', u='K', dims=['snap'])

    @known_var(dims=['snap'])
    def get_P_aux(self):
        '''pressure, from 'eosP' file.'''
        ufactor = self.u('pressure', convert_from='cgs')
        return self.load_maindims_var_across_dims('eosP', u=ufactor, dims=['snap'])


    # # # VAR-SPECIFIC EOS MODES # # #
    # in some cases, muram has aux data for some vars but not others;
    # in that case, might want, e.g., 'aux' eos_mode for some vars but 'table' for others.

    cls_behavior_attrs.register('eos_mode_ne', default=None)
    cls_behavior_attrs.register('eos_mode_T', default=None)
    cls_behavior_attrs.register('eos_mode_P', default=None)

    eos_mode_ne = simple_property('_eos_mode_ne',  default=None,
            doc='''None or str telling the eos_mode for electron number density, e.g. 'aux'. 
            None --> ignored; just use self.eos_mode. See help(type(self).eos_mode) for details.''')
    eos_mode_T = simple_property('_eos_mode_T',  default=None,
            doc='''None or str telling the eos_mode for temperature, e.g. 'aux'. 
            None --> ignored; just use self.eos_mode. See help(type(self).eos_mode) for details.''')
    eos_mode_P = simple_property('_eos_mode_P',  default=None,
            doc='''None or str telling the eos_mode for pressure, e.g. 'aux'. 
            None --> ignored; just use self.eos_mode. See help(type(self).eos_mode) for details.''')

    eos_mode_ne_explicit = alias('eos_mode_ne',
        doc='''alias to self.eos_mode_ne if not None, else self.eos_mode.
        Probably: internal methods use this, but user only uses eos_mode_ne.''')
    @eos_mode_ne_explicit.getter
    def eos_mode_ne_explicit(self):
        result = self.eos_mode_ne
        return self.eos_mode if result is None else result

    eos_mode_T_explicit = alias('eos_mode_T',
        doc='''alias to self.eos_mode_T if not None, else self.eos_mode.
        Probably: internal methods use this, but user only uses eos_mode_T.''')
    @eos_mode_T_explicit.getter
    def eos_mode_T_explicit(self):
        result = self.eos_mode_T
        return self.eos_mode if result is None else result

    eos_mode_P_explicit = alias('eos_mode_P',
        doc='''alias to self.eos_mode_P if not None, else self.eos_mode.
        Probably: internal methods use this, but user only uses eos_mode_P.''')
    @eos_mode_P_explicit.getter
    def eos_mode_P_explicit(self):
        result = self.eos_mode_P
        return self.eos_mode if result is None else result

    @known_var(attr_deps=[('eos_mode_ne_explicit', '_EOS_MODE_TO_NE_VAR')])
    def get_ne(self):
        '''electron number density. Depends on self.eos_mode; see help(type(self).eos_mode) for details
        (To override eos_mode for just ne, can set self.eos_mode_ne instead.)
        'ideal' --> cannot get ne. Crash with TypevarNanError.
        'table' --> ne from plugging r and e into EOS lookup tables (see self.tabin).
        'aux' --> get directly from Muram aux files.
        [more options might be available (depending on subclass) -- see self.EOS_MODE_OPTIONS.]
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        with self.using(eos_mode=self.eos_mode_ne_explicit):
            return super().get_ne()

    @known_var(attr_deps=[('eos_mode_T_explicit', '_EOS_MODE_TO_T_VAR')])
    def get_T(self):
        '''Temperature. Depends on self.eos_mode; see help(type(self).eos_mode) for details
        (To override eos_mode for just T, can set self.eos_mode_T instead.)
        'ideal' --> cannot get temperature. Crash with TypevarNanError.
        'table' --> T from plugging r and e into EOS lookup tables (see self.tabin).
        'aux' --> get directly from Muram aux files.
        [more options might be available (depending on subclass) -- see self.EOS_MODE_OPTIONS.]
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        with self.using(eos_mode=self.eos_mode_T_explicit):
            return super().get_T()

    @known_var(attr_deps=[('eos_mode_P_explicit', '_EOS_MODE_TO_P_VAR')])
    def get_P(self):
        '''Temperature. Depends on self.eos_mode; see help(type(self).eos_mode) for details
        (To override eos_mode for just P, can set self.eos_mode_P instead.)
        'ideal' --> cannot get pressure. Crash with TypevarNanError.
        'table' --> P from plugging r and e into EOS lookup tables (see self.tabin).
        'aux' --> get directly from Muram aux files.
        [more options might be available (depending on subclass) -- see self.EOS_MODE_OPTIONS.]
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        with self.using(eos_mode=self.eos_mode_P_explicit):
            return super().get_P()
