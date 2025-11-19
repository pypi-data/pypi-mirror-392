import inspect
from typing import List, Optional, Union, Tuple, Callable
from functools import partial
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from sklearn.neighbors import NearestNeighbors
from joblib import Parallel, delayed
import tqdm

from .io import CifReader, CSDReader
from .calculate import AMD, PDD, ADA, PDA, _collapse_into_groups
from .compare import EMD
from .periodicset import PeriodicSet
from ._types import FloatArray, UIntArray
from .globals_ import ATOMIC_NUMBERS_TO_SYMS

_SingleCompareInput = Union[PeriodicSet, str]
CompareInput = Union[_SingleCompareInput, List[_SingleCompareInput]]


def compare(
        crystals: CompareInput,
        crystals_: Optional[CompareInput] = None,
        invariant: Callable = AMD,
        k: int = 100,
        n_neighbors: Optional[int] = None,
        max_dist: float = None, 
        emd_invariant: Optional[Callable] = PDD,
        site_mismatches: bool = True,
        csd_refcodes: bool = False,
        verbose: bool = True,
        n_jobs: Optional[int] = None,
        **kwargs
) -> pd.DataFrame:
    r"""Compare one or two collections of crystals by isometry
    invariants, returning a DataFrame of pairs of crystals.

    The collections `crystals` and `crystals\_` can be given as CIF file
    path(s), directly as `PeriodicSet`s or as CSD refcodes if
    `csd_refcodes` is True.

    Crystals are compared by `invariant` (either `amd.ADA` or `amd.AMD`)
    which return a vector given a PeriodicSet and parameter `k` of
    neighbouring atoms to consider.

    If `n_neighbors` is given, a list of the nearest neighbours for each
    item in `crystals` is returned, the neighbours being from
    `crystals\_` if given and `crystals` otherwise. If `max_dist` is
    given, a list of all pairs whose distance (by `invariant`) is within
    `max_dist` is returned.

    If `emd_invariant` is given (either `amd.PDA` or `amd.PDD`), pairs
    of crystals in the above list are recompared by earth mover's
    distance on `emd_invariant`. If `site_mismatches` is also True,
    a column is returned indicating where atoms paired by EMD atomic types/occupancies of
    did not match, even though atoms
    
    ADA (or the
    unnormalised AMD) and return a pandas DataFrame of comparisons.
    Default is to compare by ADA with k = 100. Accepts any keyword
    arguments accepted by :class:`CifReader <.io.CifReader>`,
    :class:`CSDReader <.io.CSDReader>` and functions from
    :mod:`.compare`.

    Parameters
    ----------
    crystals : list of str or :class:`PeriodicSet <.periodicset.PeriodicSet>`
        First set of PeriodicSets to compare. If `crystals\_` is None,
        items in this collection are compared with each other, otherwise
        items in this set are compared with those in `crystals\_`.
        Accepts a path, :class:`PeriodicSet <.periodicset.PeriodicSet>`
        or list.
    crystals\_ : list of str or :class:`PeriodicSet <.periodicset.PeriodicSet>`, optional
        Second set of PeriodicSets to compare. If given, items in
        `crystals` are compared with those in `crystals\_`. Accepts a
        path, :class:`PeriodicSet <.periodicset.PeriodicSet>` or list.
    invariant : Callable, default 'amd.ADA'
        Invariant to compare by. Can be either `amd.ADA` or `amd.AMD`.
    k : int, default 100
        Parameter for invariants, the number of neighbor atoms to
        consider for each atom in a unit cell.
    n_neighbors : int, deafult None
        Find nearest neighbors in ``crystals\_`` for each item in
        ``crystals``.
    max_dist : float, deafult None
        Find pairs of items from ``crystals`` and ``crystals\_`` with
        distance (by ``invariant``) within ``max_dist``.
    emd_invariant : Callable, default :func:`PDA <.calculate.PDA>`
        After comparing by 
        Use PDD or PDA to recompare all pairs of items.
    site_mismatches : bool
        If True, return a column detailing which sites were aligned by
        EMD on ``emd_invariant`` but did not have the same atomic type
        or occupancy.
    csd_refcodes : bool, csd-python-api only
        Interpret ``crystals`` and ``crystals\_`` as CSD refcodes or
        lists thereof, rather than paths.
    verbose: bool
        If True, prints a progress bar during reading, calculating and
        comparing items.
    **kwargs :
        Any keyword arguments accepted by the ``amd.CifReader``,
        ``amd.CSDReader``, ``amd.PDD`` and functions used to compare:
        ``reader``, ``remove_hydrogens``, ``disorder``,
        ``heaviest_component``, ``molecular_centres``,
        ``show_warnings``, (from class:`CifReader <.io.CifReader>`),
        ``refcode_families`` (from :class:`CSDReader <.io.CSDReader>`),
        ``collapse_tol`` (from :func:`PDD <.calculate.PDD>`),
        ``metric``, ``low_memory``
        (from :func:`AMD_pdist <.compare.AMD_pdist>`), ``metric``,
        ``backend``, ``n_jobs``, ``verbose``,
        (from :func:`PDD_pdist <.compare.PDD_pdist>`), ``algorithm``,
        ``leaf_size``, ``metric``, ``p``, ``metric_params``, ``n_jobs``
        (from :func:`_nearest_items <.compare._nearest_items>` or
        :func:`_pairs_within_tol <.compare._pairs_within_tol>`).

    Returns
    -------
    df : :class:`pandas.DataFrame`
        DataFrame of pairs of crystals, either with distances within a
        tolerance (if ``max_dist`` is given) or a number of nearest
        neighbours (if ``n_neighbors`` is given).

    Raises
    ------
    ValueError, TypeError
        ...

    Examples
    --------
    Find all pairs with ADA distance within 0.01 in a .cif (deafult,
    ADA with k=100)::

        df = amd.compare('data.cif', max_dist=0.01)

    Find 10 nearest neighbours (in a directory of cifs) of all crystals
    in a cif, then recompare with EMD and return misaligned sites
    (ADA, PDA k=50)::

        df = amd.compare('data.cif', 'dir/to/cifs', k=50, n_neighbors=10)
    """

    def _default_kwargs(func: Callable) -> dict:
        """Get the default keyword arguments from ``func``."""
        return {
            k: v.default for k, v in inspect.signature(func).parameters.items()
            if v.default is not inspect.Parameter.empty
        }

    def _unwrap_refcode_list(
            refcodes: List[str], **reader_kwargs
    ) -> List[PeriodicSet]:
        """List of CSD refcodes -> list of ``PeriodicSet``s."""
        if not all(isinstance(refcode, str) for refcode in refcodes):
            raise TypeError(
                f'amd.compare(csd_refcodes=True) expects a string or list of '
                'strings'
            )
        return list(CSDReader(refcodes, **reader_kwargs))

    def _unwrap_pset_list(
            psets: List[Union[str, PeriodicSet]], **reader_kwargs
    ) -> List[PeriodicSet]:
        """List of paths/``PeriodicSet``s -> list of ``PeriodicSet``s."""
        ret = []
        for item in psets:
            if isinstance(item, PeriodicSet):
                ret.append(item)
            else:
                try:
                    path = Path(item)
                except TypeError:
                    raise ValueError(
                        'amd.compare() expects strings or amd.PeriodicSets, '
                        f'got {item.__class__.__name__}'
                    )
                ret.extend(CifReader(path, **reader_kwargs))
        return ret

    # Get default kwargs for all functions, remove kwargs that cannot be used 
    cifreader_kwargs = _default_kwargs(CifReader.__init__)
    csdreader_kwargs = _default_kwargs(CSDReader.__init__)
    csdreader_kwargs.pop('refcodes', None)
    compare_kwargs = _default_kwargs(_nearest_items)
    compare_kwargs.pop('XB', None)
    nns_kwargs = _default_kwargs(NearestNeighbors)
    nns_kwargs.pop('n_neighbors', None)
    nns_kwargs.pop('radius', None)
    for kw in nns_kwargs:
        if kw not in compare_kwargs:
            compare_kwargs[kw] = nns_kwargs[kw]
    emd_invariant_kwargs = _default_kwargs(emd_invariant)
    emd_invariant_kwargs.pop('return_row_groups', None)
    emd_kwargs = _default_kwargs(EMD)
    emd_kwargs.pop('return_transport', None)
    kwargs['verbose'] = verbose

    # Overwrite default kwargs with those given
    unset_kwargs = {kw: True for kw in kwargs}
    for default_kwargs in (
        cifreader_kwargs,
        csdreader_kwargs,
        compare_kwargs,
        emd_invariant_kwargs,
        emd_kwargs
    ):
        for kw in default_kwargs:
            if kw in kwargs:
                default_kwargs[kw] = kwargs[kw]
                unset_kwargs[kw] = False

    # All remaining kwargs passed to EMD, then to scipy.cdist
    for kw in unset_kwargs:
        if unset_kwargs[kw]:
            emd_kwargs[kw] = kwargs[kw]

    # Get list of PeriodicSets from first input
    if not isinstance(crystals, list):
        crystals = [crystals]
    if csd_refcodes:
        crystals = _unwrap_refcode_list(crystals, **csdreader_kwargs)
    else:
        crystals = _unwrap_pset_list(crystals, **cifreader_kwargs)
    if not crystals:
        raise ValueError(
            'First argument passed to compare() contains no valid crystals'
        )
    names = [s.name for s in crystals]

    # Get list of PeriodicSets from second input (if given)
    if crystals_ is None:
        names_ = names
    else:
        if not isinstance(crystals_, list):
            crystals_ = [crystals_]
        if csd_refcodes:
            crystals_ = _unwrap_refcode_list(crystals_, **csdreader_kwargs)
        else:
            crystals_ = _unwrap_pset_list(crystals_, **cifreader_kwargs)
        if not crystals_:
            raise ValueError(
                'Second argument passed to compare() contains no valid '
                'crystals'
            )
        names_ = [s.name for s in crystals_]

    if verbose:
        pbar_wrapper = partial(tqdm.tqdm, delay=2)
    else:
        pbar_wrapper = lambda x: x

    if n_jobs is None:
        amds = np.empty((len(names), k), dtype=np.float64)
        for i, s in enumerate(pbar_wrapper(crystals)):
            amds[i] = invariant(s, k)
    else:
        amds = np.array(Parallel(n_jobs=n_jobs, verbose=0)(
            delayed(invariant)(s, k) for s in pbar_wrapper(crystals)
        ))

    if crystals_ is not None:
        if n_jobs is None:
            amds_ = np.empty((len(names_), k), dtype=np.float64)
            for i, s in enumerate(pbar_wrapper(crystals_)):
                amds_[i] = invariant(s, k)
        else:
            amds_ = np.array(Parallel(n_jobs=n_jobs, verbose=0)(
                delayed(invariant)(s, k) for s in pbar_wrapper(crystals_)
            ))
    else:
        amds_ = None
        crystals_ = crystals

    inv_name = str(invariant.__name__)
    df = _compare(
        amds, amds_,
        n_neighbors=n_neighbors,
        max_dist=max_dist,
        **compare_kwargs
    )
    df.rename(columns={'distance': f'{inv_name}{k} distance'}, inplace=True)

    if emd_invariant is not None:

        emd_inv_func = partial(emd_invariant, k=k, **emd_invariant_kwargs)
        emd_func = partial(EMD, **emd_kwargs)

        if site_mismatches:
            new_data = [
                _EMD_mismatch_data(
                    crystals[n1], crystals_[n2], emd_inv_func, emd_func, as_str=True
                )
                for n1, n2 in zip(pbar_wrapper(df['i1']), df['i2'])
            ]
            emds = [dat[0] for dat in new_data]
            mismatches = [dat[1] for dat in new_data]
            df[f'{emd_invariant.__name__}{k} distance'] = emds
            df[f'Site mismatches'] = mismatches
        else:
            emds = [
                emd_func(emd_inv_func(crystals[n1]), emd_inv_func(crystals_[n2]))
                for n1, n2 in zip(pbar_wrapper(df['i1']), df['i2'])
            ]
            df[f'{emd_invariant.__name__}_EMD{k}'] = emds

    df['i1'] = df['i1'].map(lambda i: crystals[i].name)
    df['i2'] = df['i2'].map(lambda i: crystals_[i].name)
    df.rename(columns={'i1': 'ID1', 'i2': 'ID2'}, inplace=True)

    return df


def _compare(
        XA,
        XB=None,
        n_neighbors=None,
        max_dist=None,
        algorithm: str = 'kd_tree',
        leaf_size: int = 3,
        metric: str = 'chebyshev',
        n_jobs: Optional[int] = None,
        **kwargs
):

    if n_neighbors is not None:
        dists, inds = _nearest_items(
            n_neighbors, XA, XB, 
            algorithm=algorithm,
            leaf_size=leaf_size,
            metric=metric,
            n_jobs=n_jobs,
            **kwargs
        )
        pairs_list = []
        for r_ind, (d_row, i_row) in enumerate(zip(dists, inds)):
            for nn, (d, c_ind) in enumerate(zip(d_row, i_row)):
                if max_dist is None or d <= max_dist:
                    pairs_list.append((r_ind, c_ind, nn + 1, d))
        cols = ['i1', 'i2', 'nn', 'distance']

    elif max_dist is not None:
        dists, inds = _pairs_within_tol(
            max_dist, XA, XB,
            algorithm=algorithm,
            leaf_size=leaf_size,
            metric=metric,
            n_jobs=n_jobs,
            **kwargs
        )
        pairs_list = [
            (i, j, d) 
            for i, (dlist, ilist) in enumerate(zip(dists, inds))
            for d, j in zip(dlist, ilist)
        ]
        cols = ['i1', 'i2', 'distance']

    else:
        raise ValueError('Either n_neighbors or max_dist must be specified')

    return pd.DataFrame(pairs_list, columns=cols, index=None)


def _nearest_items(
        n_neighbors: int,
        XA: FloatArray,
        XB: Optional[FloatArray] = None,
        algorithm: str = 'kd_tree',
        leaf_size: int = 3,
        metric: str = 'chebyshev',
        n_jobs: Optional[int] = None,
        **kwargs
) -> Tuple[FloatArray, UIntArray]:
    """Find nearest neighbor distances and indices between all
    items/observations/rows in ``XA`` and ``XB``. If ``XB`` is None,
    find neighbors in ``XA`` for all items in ``XA``.
    """

    if XB is None:
        XB_ = XA
        n_neighbors_ = n_neighbors + 1
    else:
        XB_ = XB
        n_neighbors_ = n_neighbors

    dists, inds = NearestNeighbors(
        n_neighbors=n_neighbors_,
        algorithm=algorithm,
        leaf_size=leaf_size,
        metric=metric,
        n_jobs=n_jobs,
        **kwargs
    ).fit(XB_).kneighbors(XA)

    if XB is not None:
        return dists, inds

    else:

        # Remove self-neighbours
        final_shape = (dists.shape[0], n_neighbors)
        dists_ = np.empty(final_shape, dtype=np.float64)
        inds_ = np.empty(final_shape, dtype=np.int64)

        for i, (d_row, ind_row) in enumerate(zip(dists, inds)):
            i_ = 0
            for d, j in zip(d_row, ind_row):
                if i == j:
                    continue
                dists_[i, i_] = d
                inds_[i, i_] = j
                i_ += 1
                if i_ == n_neighbors:
                    break

        return dists_, inds_


def _pairs_within_tol(
        tol: float,
        XA: FloatArray,
        XB: Optional[FloatArray] = None,
        algorithm: str = 'kd_tree',
        leaf_size: int = 3,
        metric: str = 'chebyshev',
        n_jobs: Optional[int] = None,
        **kwargs
) -> Tuple[FloatArray, UIntArray]:
    """Find all pairs of items between XA and XB (within XA if XB is
    None). Returns an array of distances and an array of indices of each
    pair.
    """

    XB_ = XA if XB is None else XB
    dists, inds = NearestNeighbors(
        radius=tol,
        algorithm=algorithm,
        leaf_size=leaf_size,
        metric=metric,
        n_jobs=n_jobs,
        **kwargs
    ).fit(XB_).radius_neighbors(XA, sort_results=True)

    if XB is not None:
        return dists, inds

    else:

        # Remove self-neighbours
        done = set()
        dists_, inds_ = [], []
        for i, (d_row, ind_row) in enumerate(zip(dists, inds)):
            d_row_, ind_row_ = [], []
            for d, j in zip(d_row, ind_row):
                if i == j or (j, i) in done:
                    continue
                d_row_.append(d)
                ind_row_.append(j)
                done.add((i, j))
            dists_.append(d_row_)
            inds_.append(ind_row_)

        return dists_, inds_


def _EMD_mismatch_data(pset1, pset2, emd_invariant_func, emd_func, as_str=False):
    """Uses overlapping sites model, where periodicset.types and
    periodicset.occupancies are arrays.
    Return EMD and a list 
    [([types1, occs1, weights1], [types2, occs2, weights2]), ...]
    describing mismatches between sites aligned by EMD.
    ``emd_invariant_func`` should accept only a periodic set, and return
    a PDD-shaped array (2D with weights in the first column). Use
    ``functools.parital`` to create a callable with ``k`` and other
    parameters initialised.
    """

    # Mo1(w=0.167) -> Ta1(w=0.0769) | Mo1(w=0.167) -> Ta3(w=0.0385) | Mo1(w=0.167) -> Ta2(w=0.0385) | Mo1(w=0.167) -> Th3(w=0.0385) | O3(w=0.333) -> Th3(w=0.0385) | La0(w=0.167) -> O11(w=0.0385) | La0(w=0.167) -> Th1(w=0.0769) | La0(w=0.167) -> Th2(w=0.0385) | La0(w=0.167) -> Th3(w=0.0385)
    # For the info arrays, collapse rows where 

    # site_info = types, occs

    def _pdd_with_row_data(pset, emd_invariant_func):
        pdd, pdd_row_grps = emd_invariant_func(pset, return_row_data=True)
        info, inds = [], []
        occs = pset.occupancies
        for grp in pdd_row_grps:
            site_info = np.empty((len(grp), 2), dtype=np.float64)
            site_info[:, 0] = pset.types[grp]
            site_info[:, 1] = occs[grp]
            overlapping = pdist(site_info, metric='chebyshev') <= 1e-10
            groups = _collapse_into_groups(overlapping)
            site_info = np.array([site_info[g[0]] for g in groups])
            lex_ordering = np.lexsort(np.rot90(site_info))
            info.append(site_info[lex_ordering])
            inds.append([[grp[i_] for i_ in groups[i]] for i in lex_ordering])
        return pdd, info, inds 

    pdd1, info1, inds1 = _pdd_with_row_data(pset1, emd_invariant_func)
    pdd2, info2, inds2 = _pdd_with_row_data(pset2, emd_invariant_func)

    emd, plan = emd_func(pdd1, pdd2, return_transport=True)
    misaligned = []
    for i, j in np.argwhere(plan >= 1e-5):
        inf1, inf2 = info1[i], info2[j]
        if inf1.shape[0] != inf2.shape[0] or (np.amax(np.abs(inf1 - inf2)) >= 1e-10):
            misaligned.append((i, j))

    if as_str:

        res = []
        if misaligned:
            
            if pset1.labels is not None:
                labels1 = pset1.labels
            else:
                labels1 = [ATOMIC_NUMBERS_TO_SYMS[n] for n in pset1.types]
            
            if pset2.labels is not None:
                labels2 = pset2.labels
            else:
                labels2 = [ATOMIC_NUMBERS_TO_SYMS[n] for n in pset2.types]
            
            
            for i, j in misaligned:

                # Atom labels
                labs1 = ['/'.join([labels1[i_] for i_ in grp_]) for grp_ in inds1[i]]
                labs2 = ['/'.join([labels2[i_] for i_ in grp_]) for grp_ in inds2[j]]

                # Add occs to each (collection of) labels if they differ
                inf1, inf2 = info1[i], info2[j]
                # if inf1.shape[0] != inf2.shape[0]:
                if np.amax(np.abs(inf1[:, 1] - inf2[:, 1][:, None])) > 1e-10:
                    labs1 = [f'{l}:o={inf1[i_, 1]:.3g}' for i_, l in enumerate(labs1)]
                    labs2 = [f'{l}:o={inf2[i_, 1]:.3g}' for i_, l in enumerate(labs2)]

                s1 = ','.join(labs1)
                s2 = ','.join(labs2)

                # if len(labs1) > 1:
                #     s1 = f'({s1})'
                # if len(labs2) > 1:
                #     s2 = f'({s2})'

                # Add weights to each side if they differ
                if np.amax(np.abs(pdd1[i, 0] - pdd2[j, 0])) >= 1e-10:
                    s1 = f'{s1}(w={pdd1[i, 0]:.3g})'
                    s2 = f'{s2}(w={pdd2[j, 0]:.3g})'

                s = f'{s1} -> {s2}'
                if s not in res:
                    res.append(s)

        return emd, ' | '.join(res)

    else:
        return emd, misaligned


def _nearest_neighbors_dataframe(nn_dm, inds, names, names_=None):
    """Make ``pandas.DataFrame`` from distances to and indices of
    nearest neighbors from one set to another (as returned by
    neighbors_from_distance_matrix() or _nearest_items()).
    DataFrame has columns ID 1, DIST1, ID 2, DIST 2..., and names as
    indices.
    """

    if names_ is None:
        names_ = names
    data = {}
    for i in range(nn_dm.shape[-1]):
        data['ID ' + str(i+1)] = [names_[j] for j in inds[:, i]]
        data['DIST ' + str(i+1)] = nn_dm[:, i]
    return pd.DataFrame(data, index=names)


def _neighbors_from_distance_matrix(
        n: int, dm: FloatArray
) -> Tuple[FloatArray, UIntArray]:
    """Given a distance matrix, find the n nearest neighbors of each
    item.

    Parameters
    ----------
    n : int
        Number of nearest neighbors to find for each item.
    dm : :class:`numpy.ndarray`
        2D distance matrix or 1D condensed distance matrix.

    Returns
    -------
    (nn_dm, inds) : tuple of :class:`numpy.ndarray` s
        ``nn_dm[i][j]`` is the distance from item :math:`i` to its
        :math:`j+1` st nearest neighbor, and ``inds[i][j]`` is the
        index of this neighbor (:math:`j+1` since index 0 is the first
        nearest neighbor).
    """

    inds = None
    if len(dm.shape) == 2:
        inds = np.array(
            [np.argpartition(row, n)[:n] for row in dm], dtype=np.int64
        )
    elif len(dm.shape) == 1:
        dm = squareform(dm)
        inds = []
        for i, row in enumerate(dm):
            inds_row = np.argpartition(row, n+1)[:n+1]
            inds_row = inds_row[inds_row != i][:n]
            inds.append(inds_row)
        inds = np.array(inds, dtype=np.int64)
    else:
        ValueError(
            'Expected a 2D distance matrix or condensed distance matrix'
        )

    nn_dm = np.take_along_axis(dm, inds, axis=-1)
    sorted_inds = np.argsort(nn_dm, axis=-1)
    inds = np.take_along_axis(inds, sorted_inds, axis=-1)
    nn_dm = np.take_along_axis(nn_dm, sorted_inds, axis=-1)
    return nn_dm, inds


def distance_matrix(
        crystals: CompareInput,
        crystals_: Optional[CompareInput] = None,
        by: str = 'AMD',
        k: int = 100,
        csd_refcodes: bool = False,
        verbose: bool = True,
        **kwargs
) -> pd.DataFrame:
    ...

