import numpy as np
import pandas as pd
import scanpy as sc

import SEACells

import os
from glob import glob
import enlighten

class Queue():
    def __init__(self, results_dir):
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
    
    def get_completed_genes(self):
        return [os.path.basename(f).replace('.csv', '') for f in glob(f'{self.results_dir}/*.csv')]

    def get_locked_genes(self):
        return [os.path.basename(f).replace('.lock', '') for f in glob(f'{self.results_dir}/*.lock')]

    def create_lock(self, gene):
        with open(f'{self.results_dir}/{gene}.lock', 'w') as f:
            f.write('')
    
    def delete_lock(self, gene):
        os.remove(f'{self.results_dir}/{gene}.lock')
    
    def get_working_genes(self):
        return set(self.get_locked_genes()) | set(self.get_completed_genes())

class SeaShells(Queue):
    def __init__(self, adata_full, results_dir, cells_per_metacell=75, sample_col='perturbation'):
        super().__init__(results_dir)

        self.adata_full = adata_full
        self.sample_col = sample_col
        self.kos = adata_full.obs[sample_col].unique()
        self.cells_per_metacell = cells_per_metacell
    
    def run(self):
        manager = enlighten.get_manager()
        genes = set(self.kos) - set(self.get_working_genes())

        pbar = manager.counter(
            total=len(self.kos), 
            desc='Running SEACells', 
            unit='gene', 
            color='pink', 
            autorefresh=True
        )
        
        pbar.count = len(self.get_completed_genes())

        for gene in genes:
            completed_genes = self.get_working_genes()
            
            if gene in completed_genes:
                continue
            
            self.create_lock(gene)

            pbar.desc = f'Running SEACells - {gene}'
            pbar.refresh()

            adata = self.adata_full[self.adata_full.obs[self.sample_col] == gene]
            adata = self.run_seacells(adata)
            self.save_metacells(adata, gene)

            self.delete_lock(gene)
            pbar.count = len(self.get_completed_genes())

        pbar.close()


    def run_seacells(self, ad, build_kernel_on = 'X_pca', n_waypoint_eigs = 10):

        n_SEACells = round(ad.n_obs / self.cells_per_metacell)

        if n_SEACells < 3:
            ad.obs['SEACell'] = 0
            return ad

        n_waypoint_eigs = min(n_SEACells, n_waypoint_eigs)

        # Preprocess the data
        sc.pp.pca(ad)
        sc.pp.neighbors(ad, n_neighbors=30, use_rep='X_pca')
        sc.tl.umap(ad)

        # Run SEACells
        model = SEACells.core.SEACells(ad, 
                  build_kernel_on=build_kernel_on, 
                  n_SEACells=n_SEACells, 
                  n_waypoint_eigs=n_waypoint_eigs,
                  convergence_epsilon = 1e-5)
    
        model.construct_kernel_matrix()
        M = model.kernel_matrix

        model.initialize_archetypes()
        model.fit(min_iter=10, max_iter=500)

        return ad

    def save_metacells(self, ad, name):
        assert hasattr(ad.obs, 'SEACell'), f'No SEACell column in adata.obs'

        clusters = ad.obs['SEACell'].unique()
        int_clusters = {c: i for i, c in enumerate(clusters)}
        df = ad.obs['SEACell'].map(int_clusters)
        df.to_csv(f'{self.results_dir}/{name}.csv')
    





        