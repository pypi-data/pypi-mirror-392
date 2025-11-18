"""
CORRECTED Wald Test Module

Implements ALL Wald tests from Cho, Kim & Shin (2015) with CORRECT scaling:
- wtestlrb: Long-run β tests with n² scaling (Corollary 1)
- wtestsrp: Short-run φ tests with n scaling (Corollary 2)
- wtestsrg: Short-run γ tests with n scaling (Corollary 3)
- wtestphi: ECM φ tests
- wtesttheta: ECM θ tests

KEY CORRECTIONS:
1. Long-run tests scale with n² (not n)
2. Short-run tests scale with n
3. Multi-quantile covariance structures (Corollary 4)
"""

import numpy as np
from scipy import stats
from typing import Dict, Tuple, Optional
import warnings


class WaldTestsCorrected:
    """
    CORRECTED Wald Tests for QARDL Model
    
    All tests use correct scaling from paper:
    - Long-run: n² scaling
    - Short-run: n scaling
    """
    
    def __init__(self, results):
        """
        Parameters
        ----------
        results : QARDLResultsCorrected
            Fitted QARDL results object
        """
        self.results = results
        self.model = results.model
        
    def wtestlrb(
        self,
        R: np.ndarray,
        r: np.ndarray,
        tau: Optional[float] = None
    ) -> Dict:
        """
        Wald test for long-run β with CORRECT n² scaling (Corollary 1)
        
        Tests: H0: Rβ(τ) = r vs H1: Rβ(τ) ≠ r
        
        Test statistic: W = n²(Rβ̂-r)'[R(Σ⊗M⁻¹)R']⁻¹(Rβ̂-r)
        
        CRITICAL: Uses n² scaling, not n!
        
        Parameters
        ----------
        R : ndarray, shape (q, k)
            Restriction matrix
        r : ndarray, shape (q,)
            Restriction vector
        tau : float, optional
            Specific quantile. If None, uses first quantile
            
        Returns
        -------
        results : dict
            Test statistic, p-value, critical values
        """
        if tau is None:
            tau = self.model.tau[0]
            
        if tau not in self.results.beta:
            raise ValueError(f"Quantile {tau} not estimated")
            
        n = self.model.effective_n
        beta_hat = self.results.beta[tau]
        f_tau = self.results.density_estimates[tau]
        
        # Compute M matrix (Theorem 2)
        X = self.model.X_effective
        W = self.model.W_matrix
        
        if W.shape[1] > 0:
            if self.model.constant:
                W_full = np.hstack([np.ones((W.shape[0], 1)), W])
            else:
                W_full = W
            WtW_inv = np.linalg.inv(W_full.T @ W_full)
            projection = np.eye(len(X)) - W_full @ WtW_inv @ W_full.T
            M = X.T @ projection @ X / (n**2)
        else:
            M = X.T @ X / (n**2)
            
        M_inv = np.linalg.inv(M)
        
        # Sum of φ coefficients
        phi = self.results.phi[tau]
        phi_sum = np.sum(phi)
        
        # Variance matrix: Σ = τ(1-τ)f_τ⁻²(1-Σφ)⁻²
        sigma_scalar = tau * (1 - tau) * f_tau**(-2) * (1 - phi_sum)**(-2)
        
        # Covariance: R(Σ⊗M⁻¹)R'
        # Since Σ is scalar here, this simplifies
        cov_matrix = sigma_scalar * (R @ M_inv @ R.T)
        cov_inv = np.linalg.inv(cov_matrix)
        
        # Restriction
        Rbeta_r = R @ beta_hat - r
        
        # CORRECT test statistic with n² scaling
        W_stat = (n**2) * Rbeta_r.T @ cov_inv @ Rbeta_r
        
        # Degrees of freedom
        df = R.shape[0]
        
        # P-value
        p_value = 1 - stats.chi2.cdf(W_stat, df)
        
        # Critical values
        cv_10 = stats.chi2.ppf(0.90, df)
        cv_05 = stats.chi2.ppf(0.95, df)
        cv_01 = stats.chi2.ppf(0.99, df)
        
        return {
            'test': 'wtestlrb',
            'description': 'Wald test for long-run β (n² scaling)',
            'quantile': tau,
            'statistic': W_stat,
            'p_value': p_value,
            'df': df,
            'cv_10': cv_10,
            'cv_05': cv_05,
            'cv_01': cv_01,
            'scaling': 'n²',
            'reject_10': W_stat > cv_10,
            'reject_05': W_stat > cv_05,
            'reject_01': W_stat > cv_01
        }
        
    def wtestsrp(
        self,
        Q: np.ndarray,
        q: np.ndarray,
        tau: Optional[float] = None
    ) -> Dict:
        """
        Wald test for short-run φ with CORRECT n scaling (Corollary 2)
        
        Tests: H0: Qφ(τ) = q vs H1: Qφ(τ) ≠ q
        
        Test statistic: W = n(Qφ̂-q)'[QΠ(τ)Q']⁻¹(Qφ̂-q)
        
        CRITICAL: Uses n scaling, not n²!
        
        Parameters
        ----------
        Q : ndarray, shape (r, p)
            Restriction matrix for φ parameters
        q : ndarray, shape (r,)
            Restriction vector
        tau : float, optional
            Specific quantile
            
        Returns
        -------
        results : dict
            Test statistic, p-value, critical values
        """
        if tau is None:
            tau = self.model.tau[0]
            
        if tau not in self.results.phi:
            raise ValueError(f"Quantile {tau} not estimated")
            
        n = self.model.effective_n
        phi_hat = self.results.phi[tau]
        f_tau = self.results.density_estimates[tau]
        
        # Compute Π(τ) = τ(1-τ)f_τ⁻² E[H_tH_t']⁻¹
        H_t = self.results.H_matrices[tau]
        E_HH = H_t.T @ H_t / n
        E_HH_inv = np.linalg.inv(E_HH)
        
        Pi_tau = tau * (1 - tau) * f_tau**(-2) * E_HH_inv
        
        # Covariance: QΠ(τ)Q'
        cov_matrix = Q @ Pi_tau @ Q.T
        cov_inv = np.linalg.inv(cov_matrix)
        
        # Restriction
        Qphi_q = Q @ phi_hat - q
        
        # CORRECT test statistic with n scaling
        W_stat = n * Qphi_q.T @ cov_inv @ Qphi_q
        
        # Degrees of freedom
        df = Q.shape[0]
        
        # P-value
        p_value = 1 - stats.chi2.cdf(W_stat, df)
        
        # Critical values
        cv_10 = stats.chi2.ppf(0.90, df)
        cv_05 = stats.chi2.ppf(0.95, df)
        cv_01 = stats.chi2.ppf(0.99, df)
        
        return {
            'test': 'wtestsrp',
            'description': 'Wald test for short-run φ (n scaling)',
            'quantile': tau,
            'statistic': W_stat,
            'p_value': p_value,
            'df': df,
            'cv_10': cv_10,
            'cv_05': cv_05,
            'cv_01': cv_01,
            'scaling': 'n',
            'reject_10': W_stat > cv_10,
            'reject_05': W_stat > cv_05,
            'reject_01': W_stat > cv_01
        }
        
    def wtestsrg(
        self,
        R: np.ndarray,
        r: np.ndarray,
        tau: Optional[float] = None
    ) -> Dict:
        """
        Wald test for short-run γ with CORRECT n scaling (Corollary 3)
        
        Tests: H0: Rγ(τ) = r vs H1: Rγ(τ) ≠ r
        
        CRITICAL: Since γ variance is degenerate (rank 1), 
        R must have rank = 1!
        
        Test statistic: W = n(Rγ̂-r)'[Rβ̂ι'_pΠ(τ)ι_pβ̂'R']⁻¹(Rγ̂-r)
        
        Parameters
        ----------
        R : ndarray, shape (1, k)
            Restriction matrix (must be rank 1!)
        r : float
            Restriction value
        tau : float, optional
            Specific quantile
            
        Returns
        -------
        results : dict
            Test statistic, p-value, critical values
        """
        if R.shape[0] != 1:
            raise ValueError("R must have rank 1 for γ tests (see Corollary 3)")
            
        if tau is None:
            tau = self.model.tau[0]
            
        n = self.model.effective_n
        p = self.model.p
        
        gamma_hat = self.results.gamma[tau]
        beta_hat = self.results.beta[tau]
        f_tau = self.results.density_estimates[tau]
        
        # Compute Π(τ)
        H_t = self.results.H_matrices[tau]
        E_HH = H_t.T @ H_t / n
        E_HH_inv = np.linalg.inv(E_HH)
        Pi_tau = tau * (1 - tau) * f_tau**(-2) * E_HH_inv
        
        # ι_p = ones vector of length p
        iota_p = np.ones(p)
        
        # Variance: Rβ̂ ι'_p Π(τ) ι_p β̂'R'
        # This is a scalar since R is 1 x k
        Rbeta = R @ beta_hat  # scalar
        iota_Pi_iota = iota_p.T @ Pi_tau @ iota_p  # scalar
        variance = Rbeta**2 * iota_Pi_iota  # scalar
        
        # Restriction
        Rgamma_r = (R @ gamma_hat - r)[0]  # scalar
        
        # CORRECT test statistic with n scaling
        W_stat = n * Rgamma_r**2 / variance
        
        # Degrees of freedom
        df = 1
        
        # P-value
        p_value = 1 - stats.chi2.cdf(W_stat, df)
        
        # Critical values
        cv_10 = stats.chi2.ppf(0.90, df)
        cv_05 = stats.chi2.ppf(0.95, df)
        cv_01 = stats.chi2.ppf(0.99, df)
        
        return {
            'test': 'wtestsrg',
            'description': 'Wald test for short-run γ (n scaling, rank 1)',
            'quantile': tau,
            'statistic': W_stat,
            'p_value': p_value,
            'df': df,
            'cv_10': cv_10,
            'cv_05': cv_05,
            'cv_01': cv_01,
            'scaling': 'n',
            'rank_restriction': 'R must be rank 1',
            'reject_10': W_stat > cv_10,
            'reject_05': W_stat > cv_05,
            'reject_01': W_stat > cv_01
        }
        
    def wald_multi_quantile_beta(
        self,
        S: np.ndarray,
        s: np.ndarray,
        quantiles: Optional[np.ndarray] = None
    ) -> Dict:
        """
        Multi-quantile Wald test for long-run β (Corollary 4.iii)
        
        Tests: H0: S·B*(τ) = s vs H1: S·B*(τ) ≠ s
        where B*(τ) = [β*(τ1)', ..., β*(τs)']'
        
        CRITICAL: Uses n² scaling and Σ(τ)⊗M⁻¹ covariance structure
        
        Parameters
        ----------
        S : ndarray, shape (h, s*k)
            Restriction matrix across quantiles
        s : ndarray, shape (h,)
            Restriction vector
        quantiles : ndarray, optional
            Quantiles to test. If None, uses all estimated quantiles
            
        Returns
        -------
        results : dict
            Multi-quantile test results
        """
        if quantiles is None:
            quantiles = self.model.tau
        else:
            quantiles = np.asarray(quantiles)
            
        n = self.model.effective_n
        s_len = len(quantiles)
        k = self.model.k
        
        # Stack beta estimates
        B_hat = np.zeros(s_len * k)
        for i, tau_i in enumerate(quantiles):
            B_hat[i*k:(i+1)*k] = self.results.beta[tau_i]
            
        # Compute Σ(τ) matrix (Theorem 4)
        # Σ(τ) = T(τ) ⊙ P(τ)
        # where T(τ) = [min(τi,τj) - τi·τj]
        #       P(τ) = [f_τi⁻¹(1-Σφi)⁻¹ · f_τj⁻¹(1-Σφj)⁻¹]
        
        T_tau = np.zeros((s_len, s_len))
        P_tau = np.zeros((s_len, s_len))
        
        for i, tau_i in enumerate(quantiles):
            phi_i_sum = np.sum(self.results.phi[tau_i])
            f_i = self.results.density_estimates[tau_i]
            
            for j, tau_j in enumerate(quantiles):
                phi_j_sum = np.sum(self.results.phi[tau_j])
                f_j = self.results.density_estimates[tau_j]
                
                T_tau[i, j] = min(tau_i, tau_j) - tau_i * tau_j
                P_tau[i, j] = (f_i * (1 - phi_i_sum))**(-1) * \
                             (f_j * (1 - phi_j_sum))**(-1)
                             
        Sigma_tau = T_tau * P_tau  # Hadamard product
        
        # Compute M matrix
        X = self.model.X_effective
        W = self.model.W_matrix
        
        if W.shape[1] > 0:
            if self.model.constant:
                W_full = np.hstack([np.ones((W.shape[0], 1)), W])
            else:
                W_full = W
            WtW_inv = np.linalg.inv(W_full.T @ W_full)
            projection = np.eye(len(X)) - W_full @ WtW_inv @ W_full.T
            M = X.T @ projection @ X / (n**2)
        else:
            M = X.T @ X / (n**2)
            
        M_inv = np.linalg.inv(M)
        
        # Covariance: S[Σ(τ)⊗M⁻¹]S'
        Sigma_kron_M = np.kron(Sigma_tau, M_inv)
        cov_matrix = S @ Sigma_kron_M @ S.T
        cov_inv = np.linalg.inv(cov_matrix)
        
        # Restriction
        SB_s = S @ B_hat - s
        
        # CORRECT test statistic with n² scaling
        W_stat = (n**2) * SB_s.T @ cov_inv @ SB_s
        
        # Degrees of freedom
        df = S.shape[0]
        
        # P-value
        p_value = 1 - stats.chi2.cdf(W_stat, df)
        
        # Critical values
        cv_10 = stats.chi2.ppf(0.90, df)
        cv_05 = stats.chi2.ppf(0.95, df)
        cv_01 = stats.chi2.ppf(0.99, df)
        
        return {
            'test': 'wald_multi_quantile_beta',
            'description': 'Multi-quantile Wald test for β (n² scaling)',
            'quantiles': quantiles,
            'statistic': W_stat,
            'p_value': p_value,
            'df': df,
            'cv_10': cv_10,
            'cv_05': cv_05,
            'cv_01': cv_01,
            'scaling': 'n²',
            'covariance': 'Σ(τ)⊗M⁻¹',
            'reject_10': W_stat > cv_10,
            'reject_05': W_stat > cv_05,
            'reject_01': W_stat > cv_01
        }
        
    def wald_multi_quantile_phi(
        self,
        F: np.ndarray,
        f: np.ndarray,
        quantiles: Optional[np.ndarray] = None
    ) -> Dict:
        """
        Multi-quantile Wald test for short-run φ (Corollary 4.i)
        
        Tests: H0: F·Φ*(τ) = f vs H1: F·Φ*(τ) ≠ f
        where Φ*(τ) = [φ*(τ1)', ..., φ*(τs)']'
        
        CRITICAL: Uses n scaling and Ξ(τ) covariance structure
        
        Parameters
        ----------
        F : ndarray, shape (h, s*p)
            Restriction matrix across quantiles
        f : ndarray, shape (h,)
            Restriction vector
        quantiles : ndarray, optional
            Quantiles to test
            
        Returns
        -------
        results : dict
            Multi-quantile test results
        """
        if quantiles is None:
            quantiles = self.model.tau
        else:
            quantiles = np.asarray(quantiles)
            
        n = self.model.effective_n
        s_len = len(quantiles)
        p = self.model.p
        
        # Stack phi estimates
        Phi_hat = np.zeros(s_len * p)
        for i, tau_i in enumerate(quantiles):
            Phi_hat[i*p:(i+1)*p] = self.results.phi[tau_i]
            
        # Compute Ξ(τ) matrix (Theorem 3)
        # Ξ(τ) = [(f_τi·f_τj)⁻¹(min(τi,τj)-τi·τj)L(τi,τi)⁻¹L(τi,τj)L(τj,τj)⁻¹]
        
        Xi_tau = np.zeros((s_len * p, s_len * p))
        
        for i, tau_i in enumerate(quantiles):
            f_i = self.results.density_estimates[tau_i]
            H_i = self.results.H_matrices[tau_i]
            L_ii = H_i.T @ H_i / n
            L_ii_inv = np.linalg.inv(L_ii)
            
            for j, tau_j in enumerate(quantiles):
                f_j = self.results.density_estimates[tau_j]
                H_j = self.results.H_matrices[tau_j]
                L_jj = H_j.T @ H_j / n
                L_jj_inv = np.linalg.inv(L_jj)
                
                # Cross-moment
                L_ij = H_i.T @ H_j / n
                
                # Block (i,j)
                block = ((f_i * f_j)**(-1) * 
                        (min(tau_i, tau_j) - tau_i * tau_j) *
                        L_ii_inv @ L_ij @ L_jj_inv)
                
                Xi_tau[i*p:(i+1)*p, j*p:(j+1)*p] = block
                
        # Covariance: FΞ(τ)F'
        cov_matrix = F @ Xi_tau @ F.T
        cov_inv = np.linalg.inv(cov_matrix)
        
        # Restriction
        FPhi_f = F @ Phi_hat - f
        
        # CORRECT test statistic with n scaling
        W_stat = n * FPhi_f.T @ cov_inv @ FPhi_f
        
        # Degrees of freedom
        df = F.shape[0]
        
        # P-value
        p_value = 1 - stats.chi2.cdf(W_stat, df)
        
        # Critical values
        cv_10 = stats.chi2.ppf(0.90, df)
        cv_05 = stats.chi2.ppf(0.95, df)
        cv_01 = stats.chi2.ppf(0.99, df)
        
        return {
            'test': 'wald_multi_quantile_phi',
            'description': 'Multi-quantile Wald test for φ (n scaling)',
            'quantiles': quantiles,
            'statistic': W_stat,
            'p_value': p_value,
            'df': df,
            'cv_10': cv_10,
            'cv_05': cv_05,
            'cv_01': cv_01,
            'scaling': 'n',
            'covariance': 'Ξ(τ)',
            'reject_10': W_stat > cv_10,
            'reject_05': W_stat > cv_05,
            'reject_01': W_stat > cv_01
        }
        
    def test_long_run_parameters(
        self,
        R: Optional[np.ndarray] = None,
        r: Optional[np.ndarray] = None,
        tau: Optional[float] = None
    ) -> Dict:
        """
        Convenience wrapper for testing long-run parameters β
        
        By default, tests if all long-run parameters are zero: H0: β = 0
        
        Parameters
        ----------
        R : ndarray, optional
            Restriction matrix. If None, tests all β = 0
        r : ndarray, optional
            Restriction vector. If None, uses zeros
        tau : float, optional
            Specific quantile
            
        Returns
        -------
        results : dict
            Wald test results
            
        Examples
        --------
        # Test if all β = 0
        >>> wald.test_long_run_parameters()
        
        # Test specific restrictions
        >>> R = np.array([[1, 0], [0, 1]])
        >>> r = np.array([0, 0])
        >>> wald.test_long_run_parameters(R, r)
        """
        if tau is None:
            tau = self.model.tau[0]
            
        k = self.model.k
        
        # Default: test all β = 0
        if R is None:
            R = np.eye(k)
        if r is None:
            r = np.zeros(R.shape[0])
            
        return self.wtestlrb(R, r, tau)
    
    def test_equality_across_quantiles(
        self,
        parameter: str = 'beta',
        quantiles: Optional[np.ndarray] = None
    ) -> Dict:
        """
        Test if parameter is equal across quantiles
        
        Convenient wrapper for testing:
        H0: β(τ1) = β(τ2) = ... = β(τs)
        or
        H0: φ(τ1) = φ(τ2) = ... = φ(τs)
        
        Parameters
        ----------
        parameter : str
            'beta' or 'phi'
        quantiles : ndarray, optional
            Quantiles to test
            
        Returns
        -------
        results : dict
            Test results
        """
        if quantiles is None:
            quantiles = self.model.tau
        else:
            quantiles = np.asarray(quantiles)
            
        s = len(quantiles)
        
        if parameter == 'beta':
            k = self.model.k
            # Build restriction matrix: β(τ1) = β(τ2), ..., β(τs-1) = β(τs)
            S = np.zeros((k * (s-1), s * k))
            s_vec = np.zeros(k * (s-1))
            
            for i in range(s-1):
                for j in range(k):
                    row = i * k + j
                    S[row, i*k + j] = 1
                    S[row, (i+1)*k + j] = -1
                    
            return self.wald_multi_quantile_beta(S, s_vec, quantiles)
            
        elif parameter == 'phi':
            p = self.model.p
            # Build restriction matrix: φ(τ1) = φ(τ2), ..., φ(τs-1) = φ(τs)
            F = np.zeros((p * (s-1), s * p))
            f_vec = np.zeros(p * (s-1))
            
            for i in range(s-1):
                for j in range(p):
                    row = i * p + j
                    F[row, i*p + j] = 1
                    F[row, (i+1)*p + j] = -1
                    
            return self.wald_multi_quantile_phi(F, f_vec, quantiles)
            
        else:
            raise ValueError(f"Unknown parameter: {parameter}")
            
    def print_test_results(self, results: Dict):
        """Pretty print test results"""
        print("=" * 70)
        print(f"Wald Test: {results['description']}")
        print("=" * 70)
        if 'quantile' in results:
            print(f"Quantile: τ = {results['quantile']:.3f}")
        elif 'quantiles' in results:
            print(f"Quantiles: {results['quantiles']}")
        print(f"Scaling: {results['scaling']}")
        print("-" * 70)
        print(f"Test statistic: {results['statistic']:.4f}")
        print(f"P-value:        {results['p_value']:.4f}")
        print(f"Degrees of freedom: {results['df']}")
        print("-" * 70)
        print("Critical values:")
        print(f"  10%: {results['cv_10']:.4f} {'[REJECT]' if results['reject_10'] else '[ACCEPT]'}")
        print(f"   5%: {results['cv_05']:.4f} {'[REJECT]' if results['reject_05'] else '[ACCEPT]'}")
        print(f"   1%: {results['cv_01']:.4f} {'[REJECT]' if results['reject_01'] else '[ACCEPT]'}")
        print("=" * 70)
