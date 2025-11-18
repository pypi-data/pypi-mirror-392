#!/usr/bin/env python
# coding: utf-8

# In[47]:


def RCA_vectorized(ref_point, distances):
    import numpy as np

    """
    Fully vectorized implementation of N-reference-point, N-dimensional multilateration.

    reference points: (N, N) Reduced-coordinate cooridnates of the N reference points.
    distances: (num_points, N) Distances from each unknown point to the N reference points.

    Returns: (num_points, N) Reconstructed coordinates of all unknown points in the projected space.
    """
    N = ref_point.shape[0] # How many reference points?
    num_points = distances.shape[0] # How many unknown points?

    # Step 1: Subtract first reference point → linear system
    M = 2 * (ref_point[0] - ref_point[1:])        # Computes the coefficient matrix of x in the linearized distance eq.
    A = M[:, :-1]                              # Treat the first N−1 coordinates of the unknown point separately
    M_last_col = M[:, -1]                      # The vector that multiplies the last coordinate 

    A_inv = np.linalg.inv(A)                   # Computes the inverse of A

    alpha = -A_inv @ M_last_col                # Computes alpha

    # Step 2: Compute beta for all points at once
    ref_point_diff_sq = np.sum(ref_point[1:]**2 - ref_point[0]**2, axis=1)   # Computes the squared-coordinate difference
    D = distances[:, 1:]**2 - distances[:, :1]**2 + ref_point_diff_sq[None, :]  # Right-hand side term of the linear system for all unknown points
    beta = D @ A_inv.T  # Solves the linear system for the beta vector

    # Step 3: Quadratic coefficients for x_N
    diff = beta - ref_point[0, :-1]              # Offsets between the projected coordinates and reference point 0
    A_quad = np.sum(alpha**2) + 1
    B_quad = 2 * np.sum(diff * alpha, axis=1) - 2 * ref_point[0, -1]
    C_quad = np.sum(diff**2, axis=1) + ref_point[0, -1]**2 - distances[:, 0]**2 # Constant terms in the quadratic

    x_N = -B_quad / (2 * A_quad)              # Discriminant = 0 (Tangency assumption)

    # Step 4: Back-substitute to get first N-1 coordinates
    x_rest = alpha[None, :] * x_N[:, None] + beta

    # Combine all coordinates
    points = np.hstack([x_rest, x_N[:, None]])      # Attaches the last coordinate to the rest

    return points


# In[48]:


def RCA_reference_projection(original_array, ref_array=None, k=None):
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA

    """
    Provides the input required for RCA_vectorised.

    original_array : input ndarray (n_samples, d)
    ref_array : ndarray (n_ref, d) or None. If None, reference points will be obtained using KMeans
    k : int or None. If ref_array is None, number of clusters for KMeans

    Returns: ref_array_red : ndarray (n_ref, d_reduced). PCA-reduced reference coordinates
    D : ndarray (n_samples, n_ref). Pairwise distances between original_array and ref_array
    """
    # Determine reference points
    if ref_array is None:
        if k is None:
            raise ValueError("Must specify either ref_array or k")
        # Finding cluster centroids
        kmeans = KMeans(n_clusters=k, n_init='auto')
        kmeans.fit(original_array)
        ref_array = kmeans.cluster_centers_

    # Ensure same dimensionality between original_array and ref_array
    dA, dB = original_array.shape[1], ref_array.shape[1]
    if dA != dB:
        max_d = max(dA, dB)
        if dA < max_d:
            original_array = np.pad(original_array, ((0,0),(0,max_d-dA)), mode='constant')
        if dB < max_d:
            ref_array = np.pad(ref_array, ((0,0),(0,max_d-dB)), mode='constant')

    # Compute pairwise distances
    A = original_array
    B = ref_array
    D = np.sqrt( ((A[:,None,:] - B[None,:,:]) ** 2).sum(axis=2) )

    # PCA reduce the reference coordinates
    pca = PCA(n_components=min(ref_array.shape))  # fully reduced
    ref_array_red = pca.fit_transform(ref_array)

    return ref_array_red, D

