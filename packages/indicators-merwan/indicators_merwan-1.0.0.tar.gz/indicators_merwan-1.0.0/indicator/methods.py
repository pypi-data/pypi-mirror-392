"""
Composite Indicator Calculation Methods
Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: merwanroudane/indic

This module implements various methods for constructing composite indicators
based on OECD guidelines and academic literature.
"""

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA, FactorAnalysis
from dataclasses import dataclass
from scipy.optimize import minimize
from scipy.linalg import svd
from typing import List, Optional, Tuple
import warnings
from scipy.optimize import OptimizeWarning
warnings.filterwarnings("ignore", category=OptimizeWarning)

import pandas as pd
import numpy as np


@dataclass
class Result:
    """Result dataclass containing weights and composite indicator value"""
    weights: List[float]
    ci: float


def varimax(Phi, gamma=1.0, q=20, tol=1e-6):
    """
    Perform Varimax rotation for factor analysis.
    
    Parameters:
        Phi: Factor loading matrix
        gamma: Varimax parameter
        q: Maximum iterations
        tol: Convergence tolerance
    
    Returns:
        Rotated factor loading matrix
    """
    p, k = Phi.shape
    R = np.eye(k)
    d = 0
    for i in range(q):
        d_old = d
        Lambda = np.dot(Phi, R)
        u, s, vh = svd(np.dot(Phi.T, Lambda**3 - (gamma / p) * np.dot(Lambda, np.diag(np.sum(Lambda**2, axis=0)))))
        R = np.dot(u, vh)
        d = np.sum(s)
        if d_old != 0 and d / d_old < 1 + tol:
            break
    return np.dot(Phi, R)


def normalizar_dados(dados, orientacao="Min"):
    """
    Normalize data using Min-Max method.
    
    Parameters:
        dados: List or array of numerical values
        orientacao: "Min" for standard normalization (0-1), "Max" for inverse
    
    Returns:
        Normalized data as list
    """
    if not dados:
        raise ValueError("Data list cannot be empty.")
    
    minimo = min(dados)
    maximo = max(dados)
    intervalo = maximo - minimo
    
    if intervalo == 0:
        return [0.5] * len(dados)
    
    if orientacao == "Min":
        return [(valor - minimo) / intervalo for valor in dados]
    elif orientacao == "Max":
        return [(maximo - valor) / intervalo for valor in dados]
    else:
        raise ValueError('Orientation must be "Min" or "Max".')


class EqualWeights:
    """
    Equal Weights method for composite indicators.
    Simple arithmetic mean with equal weights for all indicators.
    """
    
    def __init__(self, data, aggregation_function=np.dot):
        self.data = np.array(data)
        self.regs, self.n = self.data.shape
        self.aggregation_function = aggregation_function
    
    def compute_weights(self):
        """Compute equal weights"""
        return [1 / self.n] * self.n
    
    def composite_indicator(self, data, weights, aggregation_function):
        """Calculate composite indicator using aggregation function"""
        return aggregation_function(data, weights) / np.sum(weights)
    
    def run(self):
        """Execute the equal weights method"""
        weights = self.compute_weights()
        results_ci = self.composite_indicator(self.data, weights, self.aggregation_function)
        results = []
        for idx in results_ci:
            results.append(Result(weights=weights, ci=idx))
        return results


class GeometricMean:
    """
    Geometric Mean aggregation method.
    Less compensatory than arithmetic mean - low values in one indicator 
    are only partially compensated by high values in others.
    """
    
    def __init__(self, data):
        self.data = np.array(data)
        # Ensure all values are positive for geometric mean
        if np.any(self.data <= 0):
            raise ValueError("Geometric mean requires all positive values. Please normalize data to (0,1] range.")
        self.regs, self.n = self.data.shape
    
    def compute_weights(self):
        """Compute equal weights for geometric mean"""
        return np.array([1 / self.n] * self.n)
    
    def composite_indicator(self, data, weights):
        """Calculate composite indicator using geometric mean"""
        # Geometric mean: (product of x_i^w_i)^(1/sum(w_i))
        product = np.prod(data ** weights, axis=1)
        return product ** (1 / np.sum(weights))
    
    def run(self):
        """Execute the geometric mean method"""
        weights = self.compute_weights()
        results_ci = self.composite_indicator(self.data, weights)
        results = []
        for idx in results_ci:
            results.append(Result(weights=weights.tolist(), ci=float(idx)))
        return results


class HarmonicMean:
    """
    Harmonic Mean aggregation method.
    Least compensatory of the Pythagorean means - gives more weight to lower values.
    Useful when you want to penalize units with poor performance in any indicator.
    """
    
    def __init__(self, data):
        self.data = np.array(data)
        # Ensure no zero values for harmonic mean
        if np.any(self.data == 0):
            raise ValueError("Harmonic mean requires all non-zero values. Please normalize data appropriately.")
        self.regs, self.n = self.data.shape
    
    def compute_weights(self):
        """Compute equal weights for harmonic mean"""
        return np.array([1 / self.n] * self.n)
    
    def composite_indicator(self, data, weights):
        """Calculate composite indicator using harmonic mean"""
        # Harmonic mean: sum(w_i) / sum(w_i/x_i)
        return np.sum(weights) / np.sum(weights / data, axis=1)
    
    def run(self):
        """Execute the harmonic mean method"""
        weights = self.compute_weights()
        results_ci = self.composite_indicator(self.data, weights)
        results = []
        for idx in results_ci:
            results.append(Result(weights=weights.tolist(), ci=float(idx)))
        return results


class BOD_Calculation:
    """
    Benefit of the Doubt (BoD) method.
    Data-driven approach that assigns optimal weights to maximize each unit's performance.
    Based on Data Envelopment Analysis (DEA) methodology.
    """
    
    def __init__(self, data, aggregation_function=np.dot, bounds=None):
        self.data = np.array(data)
        self.regs, self.n = self.data.shape
        self.aggregation_function = aggregation_function
        
        if bounds is None:
            self.bounds = [(0, 1)] * self.n
        else:
            self.bounds = bounds
    
    def objective(self, x, idx):
        """Objective function to maximize (returns negative for minimization)"""
        return -self.aggregation_function(self.data[idx], x)
    
    def constraints(self, data):
        """Define constraints for optimization"""
        cons = []
        # Constraint: all composite indicators <= 1
        for row in data:
            cons.append({'type': 'ineq', 'fun': lambda x, row=row: 1 - self.aggregation_function(row, x)})
        # Constraint: sum of weights = 1
        cons.append({'type': 'eq', 'fun': lambda x: 1 - np.sum(x)})
        return cons
    
    def optimizer(self, idx):
        """Optimize weights for a specific unit"""
        x0 = np.full(self.n, 1 / self.n)
        cons = self.constraints(self.data)
        
        result = minimize(lambda x: self.objective(x, idx), x0, 
                         constraints=cons, bounds=self.bounds, method='SLSQP')
        
        if result.success:
            return result.x, -result.fun
        else:
            raise ValueError(f"Optimization failure: {result.message}")
    
    def composite_indicator(self, idx, weights):
        """Calculate composite indicator with normalization"""
        if idx >= self.regs or idx < 0:
            raise IndexError("Index outside data limits.")
        
        # Benchmark normalization
        best_ci = 0
        for i in self.data:
            best_ci = max(self.aggregation_function(i, weights), best_ci)
        
        return self.aggregation_function(self.data[idx], weights) / best_ci
    
    def run(self):
        """Execute the BoD method for all units"""
        result = []
        for idx in range(self.regs):
            weights, _ = self.optimizer(idx)
            ci = self.composite_indicator(idx, weights)
            result.append(Result(weights=weights.tolist(), ci=ci))
        return result


class Entropy_Calculation:
    """
    Shannon's Entropy method for weight determination.
    Assigns higher weights to indicators with higher discriminatory power.
    """
    
    def __init__(self, data, aggregation_function=np.dot):
        self.data = np.array(data)
        self.regs, self.n = self.data.shape
        self.aggregation_function = aggregation_function
    
    def compute_weights(self, data):
        """Compute weights based on Shannon entropy"""
        # Calculate probabilities
        probability = data / np.sum(data, axis=0, keepdims=True)
        
        # Calculate entropy
        entropy = -np.sum(probability * np.log(probability + np.finfo(float).eps), axis=0) / np.log(data.shape[0])
        
        # Calculate degrees of importance
        degrees_of_importance = 1 - entropy
        
        # Calculate weights
        weights = degrees_of_importance / np.sum(degrees_of_importance)
        return weights
    
    def composite_indicator(self, data, weights, aggregation_function):
        """Calculate composite indicator"""
        return aggregation_function(data, weights) / np.sum(weights)
    
    def run(self):
        """Execute the entropy method"""
        weights = self.compute_weights(self.data)
        results_ci = self.composite_indicator(self.data, weights, self.aggregation_function)
        results = []
        for idx in results_ci:
            results.append(Result(weights=weights.tolist(), ci=idx))
        return results


class PCA_Calculation:
    """
    Principal Component Analysis (PCA) method.
    Statistical approach for weight determination based on variance explained.
    Includes Varimax rotation for interpretability.
    """
    
    def __init__(self, data, aggregation_function=np.dot):
        self.data = np.array(data)
        self.regs, self.n = self.data.shape
        self.aggregation_function = aggregation_function
    
    def _standardize_data(self, data):
        """Standardize data using z-score"""
        scaler = StandardScaler()
        return scaler.fit_transform(data)
    
    def compute_weights(self, data):
        """Compute weights based on PCA with Varimax rotation"""
        # Fit PCA
        pca = PCA(n_components=self.n)
        pca.fit(self._standardize_data(data))
        
        # Extract variance metrics
        variance = pca.explained_variance_ratio_
        eigenvalues = pca.explained_variance_
        cumulative_variance = np.cumsum(variance)
        
        # Filter principal components based on OECD criteria
        valid_pcs = (np.round(eigenvalues) >= 1) & (variance >= 0.1)
        selected_components = pca.components_[valid_pcs, :]
        selected_eigenvalues = eigenvalues[valid_pcs]
        
        # Ensure cumulative variance > 0.6
        last_true_index = np.where(valid_pcs)[0][-1]
        for i in range(last_true_index, len(cumulative_variance)):
            if cumulative_variance[i] >= 0.6:
                break
            else:
                valid_pcs[i] = False
        
        # Compute factor loadings
        loadings = selected_components.T * np.sqrt(selected_eigenvalues)
        
        # Apply Varimax rotation
        rotated_loadings = varimax(loadings)
        
        # Compute squared loadings
        squared_loadings = rotated_loadings**2
        scaled_squared_loadings = squared_loadings / np.sum(squared_loadings, axis=0, keepdims=True)
        
        # Calculate variance explained by factors
        variance_explained_by_factors = np.sum(squared_loadings, axis=0)
        expl_tot = variance_explained_by_factors / np.sum(variance_explained_by_factors)
        
        # Determine final weights
        factor_weights = np.max(scaled_squared_loadings, axis=1)
        indices_max = np.argmax(scaled_squared_loadings, axis=1)
        
        weights = factor_weights * expl_tot[indices_max]
        weights = weights / np.sum(weights)
        
        return weights
    
    def composite_indicator(self, data, weights, aggregation_function):
        """Calculate composite indicator"""
        return aggregation_function(data, weights) / np.sum(weights)
    
    def run(self):
        """Execute the PCA method"""
        weights = self.compute_weights(self.data)
        results_ci = self.composite_indicator(self.data, weights, self.aggregation_function)
        results = []
        for idx in results_ci:
            results.append(Result(weights=weights.tolist(), ci=idx))
        return results


class FactorAnalysis_Calculation:
    """
    Factor Analysis method for weight determination.
    Alternative to PCA that assumes underlying latent factors.
    """
    
    def __init__(self, data, n_factors=None, aggregation_function=np.dot):
        self.data = np.array(data)
        self.regs, self.n = self.data.shape
        self.n_factors = n_factors if n_factors else min(self.n, 3)
        self.aggregation_function = aggregation_function
    
    def _standardize_data(self, data):
        """Standardize data"""
        scaler = StandardScaler()
        return scaler.fit_transform(data)
    
    def compute_weights(self, data):
        """Compute weights using Factor Analysis"""
        # Fit Factor Analysis
        fa = FactorAnalysis(n_components=self.n_factors, random_state=42)
        fa.fit(self._standardize_data(data))
        
        # Get loadings
        loadings = fa.components_.T
        
        # Apply Varimax rotation
        rotated_loadings = varimax(loadings)
        
        # Compute weights from squared loadings
        squared_loadings = rotated_loadings**2
        weights = np.max(squared_loadings, axis=1)
        weights = weights / np.sum(weights)
        
        return weights
    
    def composite_indicator(self, data, weights, aggregation_function):
        """Calculate composite indicator"""
        return aggregation_function(data, weights) / np.sum(weights)
    
    def run(self):
        """Execute Factor Analysis method"""
        weights = self.compute_weights(self.data)
        results_ci = self.composite_indicator(self.data, weights, self.aggregation_function)
        results = []
        for idx in results_ci:
            results.append(Result(weights=weights.tolist(), ci=idx))
        return results


class CorrelationWeights:
    """
    Correlation-based weighting method.
    Assigns weights based on correlation with a reference indicator or average.
    """
    
    def __init__(self, data, reference_idx=None, aggregation_function=np.dot):
        self.data = np.array(data)
        self.regs, self.n = self.data.shape
        self.reference_idx = reference_idx
        self.aggregation_function = aggregation_function
    
    def compute_weights(self, data):
        """Compute weights based on correlation"""
        if self.reference_idx is not None:
            # Use specified indicator as reference
            reference = data[:, self.reference_idx]
        else:
            # Use average of all indicators as reference
            reference = np.mean(data, axis=1)
        
        # Calculate correlations
        correlations = np.array([np.corrcoef(data[:, i], reference)[0, 1] 
                                for i in range(self.n)])
        
        # Convert to absolute values and normalize
        abs_correlations = np.abs(correlations)
        weights = abs_correlations / np.sum(abs_correlations)
        
        return weights
    
    def composite_indicator(self, data, weights, aggregation_function):
        """Calculate composite indicator"""
        return aggregation_function(data, weights) / np.sum(weights)
    
    def run(self):
        """Execute correlation-based weighting"""
        weights = self.compute_weights(self.data)
        results_ci = self.composite_indicator(self.data, weights, self.aggregation_function)
        results = []
        for idx in results_ci:
            results.append(Result(weights=weights.tolist(), ci=idx))
        return results


class Minimal_Uncertainty:
    """
    Minimal Uncertainty method.
    Optimizes weights to minimize ranking uncertainty across different methods.
    """
    
    def __init__(self, data, ranking_indicators, aggregation_function=np.dot, bounds=None):
        self.data = np.array(data)
        self.regs, self.n = self.data.shape
        self.ranking_indicators = np.array(ranking_indicators)
        self.ranking_regs, self.ranking_n = self.ranking_indicators.shape
        self.aggregation_function = aggregation_function
        
        if bounds is None:
            self.bounds = [(0, 1)] * self.n
        else:
            self.bounds = bounds
    
    def objective(self, x):
        """Objective function: minimize ranking uncertainty"""
        result_ic = self.aggregation_function(self.data, x)
        ranking_ic = pd.Series(result_ic).rank(method='min').to_numpy()
        result_uncertainty = np.abs(self.ranking_indicators - ranking_ic)
        return np.mean(result_uncertainty)
    
    def constraints(self, data):
        """Define optimization constraints"""
        cons = []
        # All composite indicators <= 1
        for row in data:
            cons.append({'type': 'ineq', 'fun': lambda x, row=row: 1 - self.aggregation_function(row, x)})
        # Sum of weights = 1
        cons.append({'type': 'eq', 'fun': lambda x: 1 - np.sum(x)})
        return cons
    
    def optimizer(self):
        """Optimize weights to minimize uncertainty"""
        x0 = np.random.rand(self.n)
        x0 = x0 / np.sum(x0)
        
        cons = self.constraints(self.data)
        
        result = minimize(lambda x: self.objective(x), x0, 
                         constraints=cons, bounds=self.bounds, method='SLSQP',
                         options={'ftol': 1e-6, 'maxiter': 5000})
        
        if result.success:
            return result.x, result.fun
        else:
            raise ValueError(f"Optimization failure: {result.message}")
    
    def composite_indicator(self, idx, weights):
        """Calculate composite indicator"""
        return self.aggregation_function(self.data[idx], weights)
    
    def run(self):
        """Execute minimal uncertainty method"""
        result = []
        weights, _ = self.optimizer()
        for idx in range(self.regs):
            ci = self.composite_indicator(idx, weights)
            result.append(Result(weights=weights.tolist(), ci=ci))
        return result
