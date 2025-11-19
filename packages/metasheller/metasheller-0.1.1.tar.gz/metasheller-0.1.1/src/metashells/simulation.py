'''
This script is used to simulate data for the GRN building process.
Since we're not on the same clusters right now, we need to build shared data
'''

import scanpy as sc
import numpy as np
import pandas as pd 

def create_simulated_adata(n_genes=3000, n_cells=100, n_samples=3, seed=7) -> sc.AnnData:
    '''
    Create a simulated adata object with the given number of genes, cells, and clusters.
    Args:
        n_genes: int, number of genes
        n_cells: int, number of cells
        n_clusters: int, number of clusters
        frac_mt: float, fraction of mitochondrial genes
    Returns:
        adata: AnnData object
    '''

    np.random.seed(seed)

    # Generate raw counts
    raw_counts = np.random.normal(loc=20, scale=10, size=(n_cells, n_genes)).astype(np.float32)
    raw_counts = np.round(raw_counts).astype(int)
    raw_counts[raw_counts < 0] = 0 

    adata = sc.AnnData(X=raw_counts)
    adata.obs['sample'] = np.random.choice(n_samples, size=n_cells).astype(str)
    adata.obs['sample'] = 'sample_' + adata.obs['sample']
    adata.var_names = select_gene_names(n_total_genes=n_genes)
    return adata

def select_gene_names(n_total_genes=3000) -> list:
    
    gene_names = ['gene_' + str(i) for i in range(n_total_genes)]
    return gene_names


if __name__ == "__main__":
    pass