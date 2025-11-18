"""
File Purpose: vector derivatives (e.g. curl, div, grad)
"""
import xarray as xr

from ..quantity_loader import QuantityLoader
from ...dimensions import YZ_FROM_X, XYZ
from ...errors import DimensionalityError
from ...tools import (
    alias,
    pcAccessor,
    xarray_differentiate, xarray_isel,
    join_along_dimension,
)


### --------------------- Vector Derivatives Helper Methods --------------------- ###

@pcAccessor.register('gradient', aliases=['grad'])
def gradient(array, components=XYZ, *, _post_slices=None):
    '''return gradient of array as a single vector array.
    The result will have 'components' dimension.

    components: iterable of str or Component objects
        which components to include in the result.
        result['component'][i] will be components[i],
        and result.isel(component=j) will be the derivative along str(components[j]).
        E.g., if components=[Component('x', 0), Component('y', 1)],
            then result['component'][1] == Component('y', 1),
            and result.isel(component=1) = d(array)/dy.
        The derivative is taken along the corresponding dimension,
            e.g. d(array)/dy is xarray_differentiate(array, dim='y').

        Note that any components provided here but missing from array will become 0 in result.
            e.g., components=[x,y,z] but 'z' not in array -->
                np.all(result.isel(component=2) == 0).

    _post_slices: None or dict of indexers
        [EFF] if provided, apply these indexers to results after taking each derivative,
            but before merging into the final array.
        Equivalently, could just result.isel(**_post_slices).
        But, indexing before merging can help avoid ever creating a large array.
    '''
    result = []
    for x in components:
        xstr = str(x)
        if xstr in array.dims:
            diff = xarray_differentiate(array, str(x))
        else:
            diff = xr.zeros_like(array)
        diff = diff.assign_coords(component=x)  # make sure component coord is correct
        result.append(diff)
    if _post_slices:
        result = [xarray_isel(diff, **_post_slices) for diff in result]
    return join_along_dimension(dimension='component', arrays=result)

# [TODO] divergence and curl functions, too!


### --------------------- Vector Derivative Loader --------------------- ###

class VectorDerivativeLoader(QuantityLoader):
    '''vector derivatives (e.g. curl, div, grad).
    E.g. div_u --> div(u), i.e. du_x/dx + du_y/dy + du_z/dz.
    '''
    # div_{var}; optional "__{axes}"
    @known_pattern(r'div_(.*?[^_]+?)(__[xyz]{1,3})?', deps=[0], ignores_dims=['component'])
    def get_div(self, var, *, _match=None):
        '''divergence. 'div_{var}' --> div(var), i.e. du_x/dx + du_y/dy + du_z/dz.
        if component(s) is provided, only include that component(s) during the calculation.
            e.g. div_u__xy --> du_x/dx + du_y/dy.

        if self.slices nonempty, self.deriv_before_slice controls whether slicing occurs before or after div.
        '''
        var, axes = _match.groups()
        axes = 'xyz' if (axes is None) else axes[len('__'):]  # remove '__'. e.g. '__x' --> 'x'
        pre_slices, post_slices = self._pre_and_post_deriv_slices(list(axes))
        with self.using(slices=pre_slices):
            value = self(f'{var}_{axes}')   # [EFF] get all components at once, instead of one at a time.
            # [TODO][EFF] is it better to get one at a time, if using self.deriv_before_slice != False?
        comps = self.take_components(value, drop_labels=True)  # e.g. [var_x, var_y, var_z]
        diffs = [xarray_differentiate(val, str(x)) for val, x in zip(comps, axes)]
        if post_slices:
            diffs = [xarray_isel(diff, **post_slices) for diff in diffs]
        return sum(diffs)

    # grad_{var}
    @known_pattern(r'grad_(.+)', deps=[0])
    def get_grad(self, var, *, _match=None):
        '''gradient. 'grad_{var}' --> grad(var), i.e. (dn/dx, dn/dy, dn/dz).
        returned components are determined by self.component.
            (see also: the get_xyz pattern. E.g., 'grad_n_x' --> x component of grad(n).
            to get grad of a vector's component instead, use parentheses, e.g. 'grad_(u_x)')

        if self.slices nonempty, self.deriv_before_slice controls whether slicing occurs before or after div.
        '''
        var, = _match.groups()
        pre_slices, post_slices = self._pre_and_post_deriv_slices([str(c) for c in self.component_list()])
        with self.using(slices=pre_slices):
            value = self(var)   # for grad, var is a scalar.
        result = self.gradient(value, components=self.component_list(), _post_slices=post_slices)
        return result

    gradient = staticmethod(gradient)  # makes it available as VectorDerivativeLoader.gradient()
    grad = alias('gradient')

    def curl_component(self, v, x, *, yz=None):
        '''return x component of curl(v).

        v: xarray.DataArray
            vector to take curl of.
            spatial derivatives will apply to dimensions ('x', 'y', 'z') (if they exist, else give 0).
            must include 'components' dimension including coordinates y and z.
        x: int, str, or Component
            tells component to get. if int or str, use self.components to get corresponding Component
        yz: None or iterable of two (int, str, or Component) objects
            the other two components; (x,y,z) should form a right-handed coordinate system.
            if not provided, infer from x.
        '''
        if yz is None: yz = YZ_FROM_X[x]
        y, z = yz
        vy, vz = self.take_components(v, yz)
        ddy_vz = xarray_differentiate(vz, str(y))
        ddz_vy = xarray_differentiate(vy, str(z))
        return self.assign_component_coord(ddy_vz - ddz_vy, x)

    # curl_{var}
    @known_pattern(r'curl_(.+)', deps=[0])
    def get_curl(self, var, *, _match=None):
        '''curl. 'curl_{var}' --> curl(var), i.e. (du_z/dy - du_y/dz, du_x/dz - du_z/dx, du_y/dx - du_x/dy).
        returned components are determined by self.component.
            (see also: the get_xyz pattern. E.g., curl_u_x --> x component of curl(u))

        if self.slices nonempty, self.deriv_before_slice controls whether slicing occurs before or after div.
        '''
        var, = _match.groups()
        if not self.component_is_iterable():  # single component of result,
            # so we only need some of the components of var
            x = self.component
            y, z = yz = YZ_FROM_X[x]
            pre_slices, post_slices = self._pre_and_post_deriv_slices([y, z])
            with self.using(slices=pre_slices):
                v = self(f'{var}_{y}{z}')
            result = self.curl_component(v, x, yz=yz)
            if post_slices:
                result = xarray_isel(result, **post_slices)
            return result
        # else: multiple components of result -- we do need all the components of var.
        pre_slices, post_slices = self._pre_and_post_deriv_slices(['x', 'y', 'z'])
        with self.using(slices=pre_slices):
            v = self(f'{var}_xyz')
        result = [self.curl_component(v, x) for x in self.component]
        if post_slices:
            result = [xarray_isel(diff, **post_slices) for diff in result]
        return self.join_components(result)
