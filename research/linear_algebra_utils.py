import numpy as np
import scipy.linalg as linalg





# Construct standard bases of vector spaces with given dimension(s)
def construct_standard_basis(dim):
    basematrix = np.eye(dim)
    return [basematrix[i][:,np.newaxis] for i in range(dim)]
# Input
def construct_standard_bases(dims: dict):
    bases = {}
    for node in list(dims.keys()):
        bases[node] = construct_standard_basis(dims[node])
    return bases



# Orthogonal complement of a subspace. Both input and output subspaces are given as bases, namely, lists of column vectors.
def orthogonal_complement(A):
    A = np.concatenate(A, axis=1).T
    Aperp = linalg.null_space(A)
    if Aperp.shape[1] == 0:
        return [
            np.zeros(len(A[0]))[:,np.newaxis]
        ]
        
    Aperp = Aperp.T
    Aperp_cols = [np.array(Aperp[i])[:,np.newaxis] for i in range(len(Aperp))]

    return Aperp_cols


# Give a basis for the maximal subspace on which the listed linear maps are equal
def equalizer_subspace(lmap_collection, basis_res=None):
    lmap_collection = np.stack(lmap_collection, axis = 0)

    # Take differences of maps to generate the subspace orthogonal to the equalizer
    lmap_diffs = np.diff(lmap_collection, axis = 0)
    lmap_diffs = np.unstack(lmap_diffs)

    # If a (basis of a) subspace is specified for the domain, express the linear maps in this basis. (The codomain is not restricted.)
    if basis_res is not None:
        restricted_diffs = []
        for M in lmap_diffs:
            imgs = [M.dot(b) for b in basis_res]
            M_res = np.concatenate(imgs, axis=1)
            restricted_diffs.append(M_res)
        lmap_diffs = restricted_diffs.copy()

    # Concatenate differences to express the kernel as the null space of a single matrix
    if len(lmap_diffs) == 0:
        lmap_diffs = [np.zeros(lmap_collection[0].shape)]
    lmap_diffs = np.concatenate(lmap_diffs)

    eq = linalg.null_space(lmap_diffs).T
    eq_basis = [np.array(eq[i])[:,np.newaxis] for i in range(len(eq))]
    
    # Writes null space basis in the standard basis, if written in the basis of a subspace
    if basis_res is not None:
        eq_basis = [np.array(
            [v[i]*basis_res[i] for i in range(len(v))]
        ).sum(
            axis = 0
        ) for v in eq_basis].copy()
    
    return eq_basis





# Using (U \cap V)^\perp = (U^\perp + V^\perp)^\perp
def subspace_intersection(basis_list):
    complement_spanning_set = []
    for A in basis_list:
        B = orthogonal_complement(A)
        complement_spanning_set.extend(B)
    intersection = orthogonal_complement(complement_spanning_set)
    if len(intersection) == 0:
        return np.zeros(len(basis_list[0][0]))[:,np.newaxis]
    else:
        return intersection



# Construct new basis for a direct sum of vector spaces, along with projection maps
def direct_sum(bases):
    basis_dimensions = np.array([ len(bases[k]) for k in range(len(bases)) ]) 
    direct_sum_indices = np.cumsum(basis_dimensions) - basis_dimensions[0]
    direct_sum_dimension = np.sum(basis_dimensions)

    # Embed basis vectors in direct sum
    direct_sum_basis = []
    for k in range(len(bases)):
        basis = bases[k]
        starting_index = direct_sum_indices[k]
        for i in range(len(basis)):
            dim = len(basis[0])
            v = np.zeros(direct_sum_dimension)[:,np.newaxis]
            for j in range(dim):
                v[starting_index+j][0] = basis[i][j][0]
            direct_sum_basis.append(v)

    # Construct projection maps
    projection_maps = []
    id_mat = np.eye(direct_sum_dimension)
    for k in range(len(bases)):
        node = bases[k]
        dim = len(bases[k][0])
        proj = id_mat[direct_sum_indices[k] : direct_sum_indices[k] + dim].copy()
        projection_maps.append(proj)

    return direct_sum_basis, projection_maps