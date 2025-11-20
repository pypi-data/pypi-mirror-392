"""
CDM reader
"""

import logging
import os
import xarray as xr
from xarray import backends
from pydap.client import open_url
import fileformats.cdm.accessors.dataarray  # register dataarray accessor
import fileformats.cdm.accessors.dataset  # register dataset accessor
from .accessors.dataset import SOURCE_NETCDF, SOURCE_OPENDAP, \
    OPENDAP_BACKEND_NETCDF, OPENDAP_BACKEND_PYDAP


def open_dataset(resource, opendap_backend=None):
    """
    Open dataset using xarray and register the ebas accessors.
    Parameters:
        resource: file path or OPeNDAP url
        opendap_backend: backend to use for OPeNDAP (OPENDAP_BACKEND_NETCDF,
                            OPENDAP_BACKEND_PYDAP or None for auto selection)
    Returns:
        xarray Dataset
    """
    logger = logging.getLogger('ebascdm')
    if os.path.isfile(resource):
        logger.debug("Open local NetCDF file: %s", resource)
        dataset = xr.open_dataset(resource)
        dataset.ebas.setup(
            resource=resource,
            source_type=SOURCE_NETCDF)
        return dataset
    if resource.startswith('http'):
        return _open_opendap(resource, backend=opendap_backend)
    logger.error("Resource %s is not valid.", resource)
    raise ValueError("Resource {resource} is not valid.")

def _open_opendap(url, backend=None):
    """
    Open the OPeNDAP url.

    There is a problem opening an OPeNDAP url with xarray using the
    NetCDF backend for some files/variables (many variables).

    An alternative is to use the pydap backend via xarray, but this is
    slower than the NetCDF backend.

    Caller can either choose a specific backend or use auto selection:
    In this case NetCDF is tried first, then pydap.
    The caller may use EbasCDMReader.backend_type to check which backend was
    used (e.g. for implementing some learning).

    Parameters:
        url: OPeNDAP url
        backend: backend to use (OPENDAP_BACKEND_NETCDF,
                 OPENDAP_BACKEND_PYDAP or None for auto selection)
        Returns:
            None
    """

    def _open_pydap(url):
        # Normaly, one could use xr.backends.PydapDataStore directly with url
        # but this gives warnings about the dap2 protocol.
        # We open a pydap dataset before (we can specify the dap2 protocol
        # version explicitly and get not warnings), and then pass this to
        # PydapDataStore instead of only the url. Additionally it needs to be
        # wrapped in a fake object with a 'ds' attribute.
        # The original code (giving warnings) was:
        # store = backends.PydapDataStore.open(
        #     url, user_charset='UTF-8')
        # return xr.open_dataset(store)
        pydp = open_url(url, protocol='dap2', user_charset='UTF-8')
        fakeobj = type('Wrapper', (object,), {'ds':pydp})
        store = backends.PydapDataStore.open(fakeobj)
        return xr.open_dataset(store)

    logger = logging.getLogger('ebascdm')
    logger.debug("Open OPeNDAP url: %s", url)
    if backend == OPENDAP_BACKEND_PYDAP:
        # force pydap backend
        dataset =_open_pydap(url)
        dataset.ebas.setup(
            resource=url,
            source_type=SOURCE_OPENDAP,
            backend_type=OPENDAP_BACKEND_PYDAP)
        return dataset
    if backend == OPENDAP_BACKEND_NETCDF:
        # force NetCDF backend
        dataset = xr.open_dataset(url)
        dataset.ebas.setup(
            resource=url,
            source_type=SOURCE_OPENDAP,
            backend_type=OPENDAP_BACKEND_NETCDF)
        return dataset
    # auto select backend, try NetCDF first
    try:
        dataset = xr.open_dataset(url)
        dataset.ebas.setup(
            resource=url,
            source_type=SOURCE_OPENDAP,
            backend_type=OPENDAP_BACKEND_NETCDF)
        return dataset
    except RuntimeError:
        # use pydap fallback
        dataset = _open_pydap(url)
        dataset.ebas.setup(
            resource=url,
            source_type=SOURCE_OPENDAP,
            backend_type=OPENDAP_BACKEND_PYDAP)
        return dataset
