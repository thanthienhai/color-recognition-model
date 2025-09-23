"""
Color mixing formula calculation using Kubelka-Munk theory and optimization
Implements physical color mixing models and optimization algorithms
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Union
import matplotlib.pyplot as plt
from scipy.optimize import minimize, least_squares, differential_evolution
from scipy.interpolate import interp1d
import pandas as pd
from dataclasses import dataclass
import warnings

from .utils import ColorSpaceConverter, ColorDifferenceCalculator


@dataclass
class Pigment:
    """Pigment data structure"""
    name: str
    cost_per_unit: float
    density: float
    absorption_spectrum: np.ndarray  # K values at different wavelengths
    scattering_spectrum: np.ndarray  # S values at different wavelengths
    wavelengths: np.ndarray  # Wavelength points
    max_concentration: float = 1.0  # Maximum allowable concentration


class KubelkaMunkModel:
    """Kubelka-Munk color mixing model"""
    
    def __init__(self, wavelengths: np.ndarray = None):
        """
        Initialize Kubelka-Munk model
        
        Args:
            wavelengths: Wavelength points for spectral calculations (nm)
        """
        if wavelengths is None:
            # Standard visible spectrum 380-780nm with 10nm intervals
            self.wavelengths = np.arange(380, 781, 10)
        else:
            self.wavelengths = wavelengths
        
        self.pigments = {}
        self.substrate_reflectance = None
        
        # CIE standard observer data (simplified - use colorspacious for full implementation)
        self._load_observer_data()
    
    def _load_observer_data(self):
        """Load CIE standard observer color matching functions (simplified)"""
        # This is a simplified version - use actual CIE data for production
        wavelengths = self.wavelengths
        
        # Simplified Gaussian approximations for CMF
        x_bar = np.exp(-0.5 * ((wavelengths - 598.8) / 37.9) ** 2) + \
                0.362 * np.exp(-0.5 * ((wavelengths - 442.0) / 16.4) ** 2)
        
        y_bar = np.exp(-0.5 * ((wavelengths - 556.3) / 46.9) ** 2)
        
        z_bar = 1.056 * np.exp(-0.5 * ((wavelengths - 464.3) / 16.3) ** 2)
        
        # Normalize
        self.cmf_x = x_bar / np.max(x_bar)
        self.cmf_y = y_bar / np.max(y_bar)
        self.cmf_z = z_bar / np.max(z_bar)
    
    def add_pigment(self, pigment: Pigment) -> None:
        """Add pigment to the model"""
        # Interpolate pigment spectra to model wavelengths
        if len(pigment.wavelengths) != len(self.wavelengths):
            k_interp = interp1d(pigment.wavelengths, pigment.absorption_spectrum,
                              kind='linear', fill_value='extrapolate')
            s_interp = interp1d(pigment.wavelengths, pigment.scattering_spectrum,
                              kind='linear', fill_value='extrapolate')
            
            pigment.absorption_spectrum = k_interp(self.wavelengths)
            pigment.scattering_spectrum = s_interp(self.wavelengths)
            pigment.wavelengths = self.wavelengths.copy()
        
        self.pigments[pigment.name] = pigment
        print(f"Added pigment: {pigment.name}")
    
    def set_substrate(self, reflectance: np.ndarray) -> None:
        """Set substrate reflectance spectrum"""
        if len(reflectance) != len(self.wavelengths):
            raise ValueError("Substrate reflectance length must match wavelengths")
        self.substrate_reflectance = reflectance
    
    def calculate_mixed_reflectance(self, concentrations: Dict[str, float]) -> np.ndarray:
        """
        Calculate reflectance spectrum of pigment mixture using Kubelka-Munk theory
        
        Args:
            concentrations: Dictionary of pigment concentrations {pigment_name: concentration}
            
        Returns:
            Reflectance spectrum of the mixture
        """
        if not self.pigments:
            raise ValueError("No pigments added to model")
        
        # Initialize total K and S
        total_k = np.zeros(len(self.wavelengths))
        total_s = np.zeros(len(self.wavelengths))
        
        # Add substrate contribution (if specified)
        if self.substrate_reflectance is not None:
            # Convert substrate reflectance to K/S using inverse Kubelka-Munk
            substrate_ks = (1 - self.substrate_reflectance) ** 2 / (2 * self.substrate_reflectance)
            # Assume substrate has minimal scattering
            substrate_k = substrate_ks * 0.1
            substrate_s = np.full_like(substrate_k, 0.1)
            
            total_k += substrate_k
            total_s += substrate_s
        
        # Add pigment contributions
        for pigment_name, concentration in concentrations.items():
            if pigment_name not in self.pigments:
                raise ValueError(f"Unknown pigment: {pigment_name}")
            
            pigment = self.pigments[pigment_name]
            
            # Linear mixing of K and S values weighted by concentration
            total_k += concentration * pigment.absorption_spectrum
            total_s += concentration * pigment.scattering_spectrum
        
        # Apply Kubelka-Munk equation: R = 1 + K/S - sqrt((K/S)^2 + 2*K/S)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            ks_ratio = np.divide(total_k, total_s, out=np.zeros_like(total_k), where=total_s!=0)
            reflectance = 1 + ks_ratio - np.sqrt(ks_ratio**2 + 2*ks_ratio)
        
        # Ensure reflectance is in valid range [0, 1]
        reflectance = np.clip(reflectance, 0, 1)
        
        return reflectance
    
    def reflectance_to_xyz(self, reflectance: np.ndarray) -> np.ndarray:
        """Convert reflectance spectrum to CIE XYZ"""
        # Simplified conversion (use proper illuminant for production)
        # Assume D65 illuminant (simplified as constant)
        illuminant = np.ones_like(self.wavelengths)
        
        # Calculate tristimulus values
        X = np.trapz(reflectance * illuminant * self.cmf_x, self.wavelengths)
        Y = np.trapz(reflectance * illuminant * self.cmf_y, self.wavelengths)
        Z = np.trapz(reflectance * illuminant * self.cmf_z, self.wavelengths)
        
        # Normalize by illuminant
        Y_n = np.trapz(illuminant * self.cmf_y, self.wavelengths)
        
        return np.array([X/Y_n, Y/Y_n, Z/Y_n]) * 100
    
    def xyz_to_lab(self, xyz: np.ndarray) -> np.ndarray:
        """Convert XYZ to Lab (simplified)"""
        # Standard illuminant D65
        Xn, Yn, Zn = 95.047, 100.000, 108.883
        
        x = xyz[0] / Xn
        y = xyz[1] / Yn
        z = xyz[2] / Zn
        
        # Apply cube root transformation
        fx = np.cbrt(x) if x > 0.008856 else (7.787 * x + 16/116)
        fy = np.cbrt(y) if y > 0.008856 else (7.787 * y + 16/116)
        fz = np.cbrt(z) if z > 0.008856 else (7.787 * z + 16/116)
        
        L = 116 * fy - 16
        a = 500 * (fx - fy)
        b = 200 * (fy - fz)
        
        return np.array([L, a, b])
    
    def predict_color(self, concentrations: Dict[str, float]) -> np.ndarray:
        """
        Predict Lab color from pigment concentrations
        
        Args:
            concentrations: Pigment concentrations
            
        Returns:
            Lab color values [L, a, b]
        """
        reflectance = self.calculate_mixed_reflectance(concentrations)
        xyz = self.reflectance_to_xyz(reflectance)
        lab = self.xyz_to_lab(xyz)
        return lab


class MixingOptimizer:
    """Optimize pigment mixing formulas"""
    
    def __init__(self, kubelka_munk_model: KubelkaMunkModel):
        self.km_model = kubelka_munk_model
        self.pigment_names = list(kubelka_munk_model.pigments.keys())
        self.optimization_history = []
    
    def _objective_function(self, concentrations: np.ndarray, 
                          target_lab: np.ndarray,
                          cost_weight: float = 0.1,
                          complexity_weight: float = 0.05) -> float:
        """
        Multi-objective function for optimization
        
        Args:
            concentrations: Pigment concentrations array
            target_lab: Target Lab color
            cost_weight: Weight for cost minimization
            complexity_weight: Weight for formula complexity minimization
            
        Returns:
            Objective function value
        """
        # Convert array to concentration dictionary
        conc_dict = {name: conc for name, conc in zip(self.pigment_names, concentrations)}
        
        # Predict color
        try:
            predicted_lab = self.km_model.predict_color(conc_dict)
        except:
            return 1e6  # Large penalty for invalid predictions
        
        # Color difference (primary objective)
        delta_e = ColorDifferenceCalculator.delta_e_cie76(predicted_lab, target_lab)
        
        # Cost objective
        total_cost = sum(
            conc * self.km_model.pigments[name].cost_per_unit
            for name, conc in zip(self.pigment_names, concentrations)
        )
        
        # Complexity objective (number of pigments used)
        complexity = np.sum(concentrations > 0.001)  # Count non-zero concentrations
        
        # Combined objective
        objective = delta_e + cost_weight * total_cost + complexity_weight * complexity
        
        # Store for analysis
        self.optimization_history.append({
            'concentrations': concentrations.copy(),
            'delta_e': delta_e,
            'cost': total_cost,
            'complexity': complexity,
            'objective': objective
        })
        
        return objective
    
    def optimize_formula(self, target_lab: np.ndarray,
                        method: str = 'differential_evolution',
                        max_total_concentration: float = 1.0,
                        cost_weight: float = 0.1,
                        complexity_weight: float = 0.05,
                        max_iterations: int = 1000) -> Dict:
        """
        Optimize pigment mixing formula
        
        Args:
            target_lab: Target Lab color
            method: Optimization method ('least_squares', 'minimize', 'differential_evolution')
            max_total_concentration: Maximum total pigment concentration
            cost_weight: Weight for cost minimization
            complexity_weight: Weight for complexity minimization
            max_iterations: Maximum optimization iterations
            
        Returns:
            Optimization results dictionary
        """
        self.optimization_history = []
        n_pigments = len(self.pigment_names)
        
        # Define bounds for each pigment
        bounds = [(0, pigment.max_concentration) for pigment in self.km_model.pigments.values()]
        
        # Constraints
        constraints = []
        
        # Total concentration constraint
        if max_total_concentration:
            constraints.append({
                'type': 'ineq',
                'fun': lambda x: max_total_concentration - np.sum(x)
            })
        
        # Initial guess (equal distribution)
        x0 = np.full(n_pigments, max_total_concentration / n_pigments)
        
        if method == 'differential_evolution':
            # Global optimization with differential evolution
            result = differential_evolution(
                lambda x: self._objective_function(x, target_lab, cost_weight, complexity_weight),
                bounds,
                maxiter=max_iterations,
                popsize=15,
                seed=42
            )
            
        elif method == 'minimize':
            # Local optimization
            result = minimize(
                lambda x: self._objective_function(x, target_lab, cost_weight, complexity_weight),
                x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': max_iterations}
            )
            
        elif method == 'least_squares':
            # Least squares optimization (color difference only)
            def residual_function(x):
                conc_dict = {name: conc for name, conc in zip(self.pigment_names, x)}
                try:
                    predicted_lab = self.km_model.predict_color(conc_dict)
                    return predicted_lab - target_lab
                except:
                    return np.array([1e6, 1e6, 1e6])
            
            result = least_squares(
                residual_function,
                x0,
                bounds=([b[0] for b in bounds], [b[1] for b in bounds]),
                max_nfev=max_iterations
            )
            
        else:
            raise ValueError(f"Unknown optimization method: {method}")
        
        # Process results
        optimal_concentrations = result.x if hasattr(result, 'x') else result.x
        conc_dict = {name: conc for name, conc in zip(self.pigment_names, optimal_concentrations)}
        
        # Calculate final metrics
        predicted_lab = self.km_model.predict_color(conc_dict)
        final_delta_e = ColorDifferenceCalculator.delta_e_cie76(predicted_lab, target_lab)
        
        total_cost = sum(
            conc * self.km_model.pigments[name].cost_per_unit
            for name, conc in conc_dict.items()
        )
        
        return {
            'success': result.success if hasattr(result, 'success') else True,
            'concentrations': conc_dict,
            'predicted_lab': predicted_lab,
            'target_lab': target_lab,
            'delta_e': final_delta_e,
            'total_cost': total_cost,
            'total_concentration': np.sum(optimal_concentrations),
            'num_pigments_used': np.sum(optimal_concentrations > 0.001),
            'optimization_result': result,
            'history': self.optimization_history
        }
    
    def batch_optimize(self, target_colors: List[np.ndarray],
                      color_names: Optional[List[str]] = None,
                      **optimization_kwargs) -> pd.DataFrame:
        """
        Optimize formulas for multiple colors
        
        Args:
            target_colors: List of target Lab colors
            color_names: Optional color names
            **optimization_kwargs: Arguments for optimize_formula
            
        Returns:
            DataFrame with optimization results
        """
        results = []
        
        if color_names is None:
            color_names = [f"Color_{i}" for i in range(len(target_colors))]
        
        for i, (target_lab, name) in enumerate(zip(target_colors, color_names)):
            print(f"Optimizing formula for {name} ({i+1}/{len(target_colors)})...")
            
            result = self.optimize_formula(target_lab, **optimization_kwargs)
            
            # Flatten results for DataFrame
            row = {
                'color_name': name,
                'target_L': target_lab[0],
                'target_a': target_lab[1],
                'target_b': target_lab[2],
                'predicted_L': result['predicted_lab'][0],
                'predicted_a': result['predicted_lab'][1],
                'predicted_b': result['predicted_lab'][2],
                'delta_e': result['delta_e'],
                'total_cost': result['total_cost'],
                'total_concentration': result['total_concentration'],
                'num_pigments': result['num_pigments_used'],
                'success': result['success']
            }
            
            # Add concentration for each pigment
            for pigment_name in self.pigment_names:
                row[f'conc_{pigment_name}'] = result['concentrations'][pigment_name]
            
            results.append(row)
        
        return pd.DataFrame(results)


class FormulationDatabase:
    """Database for storing and retrieving color formulations"""
    
    def __init__(self):
        self.formulations = pd.DataFrame()
        self.color_tree = None  # For nearest neighbor search
    
    def add_formulation(self, color_name: str, lab_color: np.ndarray,
                       concentrations: Dict[str, float], 
                       delta_e: float, cost: float,
                       metadata: Optional[Dict] = None) -> None:
        """Add formulation to database"""
        formulation = {
            'color_name': color_name,
            'L': lab_color[0],
            'a': lab_color[1],
            'b': lab_color[2],
            'delta_e': delta_e,
            'cost': cost,
            'timestamp': pd.Timestamp.now()
        }
        
        # Add concentrations
        for pigment, conc in concentrations.items():
            formulation[f'conc_{pigment}'] = conc
        
        # Add metadata
        if metadata:
            formulation.update(metadata)
        
        # Add to dataframe
        self.formulations = pd.concat([
            self.formulations, 
            pd.DataFrame([formulation])
        ], ignore_index=True)
    
    def find_similar_colors(self, target_lab: np.ndarray, 
                          max_delta_e: float = 5.0,
                          top_k: int = 5) -> pd.DataFrame:
        """Find similar colors in database"""
        if self.formulations.empty:
            return pd.DataFrame()
        
        # Calculate delta E for all formulations
        lab_columns = ['L', 'a', 'b']
        lab_data = self.formulations[lab_columns].values
        
        delta_es = []
        for lab in lab_data:
            delta_e = ColorDifferenceCalculator.delta_e_cie76(target_lab, lab)
            delta_es.append(delta_e)
        
        self.formulations['search_delta_e'] = delta_es
        
        # Filter and sort
        similar = self.formulations[self.formulations['search_delta_e'] <= max_delta_e]
        similar = similar.sort_values('search_delta_e').head(top_k)
        
        return similar
    
    def save_database(self, filepath: str) -> None:
        """Save database to file"""
        self.formulations.to_csv(filepath, index=False)
        print(f"Database saved to {filepath}")
    
    def load_database(self, filepath: str) -> None:
        """Load database from file"""
        self.formulations = pd.read_csv(filepath)
        print(f"Database loaded from {filepath}")


def create_standard_pigments() -> List[Pigment]:
    """Create standard pigment set for testing"""
    wavelengths = np.arange(380, 781, 10)
    
    pigments = []
    
    # Titanium White
    white_k = np.full_like(wavelengths, 0.1, dtype=float)
    white_s = np.full_like(wavelengths, 10.0, dtype=float)
    pigments.append(Pigment("Titanium_White", 1.0, 4.2, white_k, white_s, wavelengths))
    
    # Carbon Black
    black_k = np.full_like(wavelengths, 50.0, dtype=float)
    black_s = np.full_like(wavelengths, 1.0, dtype=float)
    pigments.append(Pigment("Carbon_Black", 2.0, 1.8, black_k, black_s, wavelengths))
    
    # Chrome Yellow (simplified spectrum)
    yellow_k = np.where(wavelengths < 500, 20.0, 0.5)
    yellow_s = np.full_like(wavelengths, 2.0, dtype=float)
    pigments.append(Pigment("Chrome_Yellow", 3.0, 5.1, yellow_k, yellow_s, wavelengths))
    
    # Ultramarine Blue
    blue_k = np.where((wavelengths > 500) & (wavelengths < 650), 0.5, 25.0)
    blue_s = np.full_like(wavelengths, 3.0, dtype=float)
    pigments.append(Pigment("Ultramarine_Blue", 4.0, 2.3, blue_k, blue_s, wavelengths))
    
    # Cadmium Red
    red_k = np.where(wavelengths < 600, 15.0, 0.8)
    red_s = np.full_like(wavelengths, 2.5, dtype=float)
    pigments.append(Pigment("Cadmium_Red", 8.0, 6.0, red_k, red_s, wavelengths))
    
    return pigments


def create_mixing_calculator(pigments: Optional[List[Pigment]] = None) -> Tuple[KubelkaMunkModel, MixingOptimizer]:
    """
    Create a complete mixing calculation system
    
    Args:
        pigments: List of pigments (uses standard set if None)
        
    Returns:
        (KubelkaMunkModel, MixingOptimizer)
    """
    if pigments is None:
        pigments = create_standard_pigments()
    
    # Create model and add pigments
    km_model = KubelkaMunkModel()
    for pigment in pigments:
        km_model.add_pigment(pigment)
    
    # Create optimizer
    optimizer = MixingOptimizer(km_model)
    
    return km_model, optimizer


def visualize_optimization_results(results: Dict) -> None:
    """Visualize optimization results"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Color comparison
    target_lab = results['target_lab']
    predicted_lab = results['predicted_lab']
    
    target_rgb = ColorSpaceConverter.lab_to_rgb(target_lab)
    predicted_rgb = ColorSpaceConverter.lab_to_rgb(predicted_lab)
    
    axes[0, 0].imshow([[target_rgb, predicted_rgb]])
    axes[0, 0].set_title(f'Target vs Predicted (ΔE: {results["delta_e"]:.2f})')
    axes[0, 0].set_xticks([0, 1])
    axes[0, 0].set_xticklabels(['Target', 'Predicted'])
    axes[0, 0].set_yticks([])
    
    # Concentration pie chart
    concentrations = results['concentrations']
    nonzero_conc = {k: v for k, v in concentrations.items() if v > 0.001}
    
    if nonzero_conc:
        axes[0, 1].pie(nonzero_conc.values(), labels=nonzero_conc.keys(), autopct='%1.1f%%')
        axes[0, 1].set_title('Pigment Concentrations')
    
    # Optimization history
    if results.get('history'):
        history = results['history']
        iterations = range(len(history))
        delta_es = [h['delta_e'] for h in history]
        costs = [h['cost'] for h in history]
        
        ax1 = axes[1, 0]
        ax2 = ax1.twinx()
        
        line1 = ax1.plot(iterations, delta_es, 'b-', label='ΔE')
        line2 = ax2.plot(iterations, costs, 'r-', label='Cost')
        
        ax1.set_xlabel('Iteration')
        ax1.set_ylabel('ΔE', color='b')
        ax2.set_ylabel('Cost', color='r')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper right')
        ax1.set_title('Optimization History')
    
    # Cost breakdown
    pigment_costs = []
    pigment_names = []
    for name, conc in concentrations.items():
        if conc > 0.001:
            # Get pigment cost (simplified)
            cost = conc * 5.0  # Placeholder cost
            pigment_costs.append(cost)
            pigment_names.append(name)
    
    if pigment_costs:
        axes[1, 1].bar(pigment_names, pigment_costs)
        axes[1, 1].set_title('Cost Breakdown')
        axes[1, 1].set_ylabel('Cost')
        plt.setp(axes[1, 1].xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.show()