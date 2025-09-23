"""
Optimization module for color mixing and system performance
Implements multi-objective optimization, genetic algorithms, and parameter tuning
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Callable, Any, Union
import matplotlib.pyplot as plt
from scipy.optimize import minimize, differential_evolution, dual_annealing
from scipy.stats import uniform, randint
import optuna
from dataclasses import dataclass
import time
import pandas as pd
import warnings

from .utils import ColorDifferenceCalculator
from .mixing_formula import KubelkaMunkModel, MixingOptimizer


@dataclass
class OptimizationConfig:
    """Configuration for optimization algorithms"""
    max_iterations: int = 1000
    population_size: int = 50
    tolerance: float = 1e-6
    seed: int = 42
    parallel: bool = False
    verbose: bool = True


class MultiObjectiveOptimizer:
    """Multi-objective optimization for color mixing"""
    
    def __init__(self, km_model: KubelkaMunkModel):
        self.km_model = km_model
        self.pigment_names = list(km_model.pigments.keys())
        self.pareto_front = []
        self.optimization_history = []
    
    def _calculate_objectives(self, concentrations: np.ndarray,
                            target_lab: np.ndarray) -> Tuple[float, float, float]:
        """
        Calculate multiple objectives
        
        Args:
            concentrations: Pigment concentrations
            target_lab: Target Lab color
            
        Returns:
            (delta_e, cost, complexity)
        """
        conc_dict = {name: conc for name, conc in zip(self.pigment_names, concentrations)}
        
        try:
            predicted_lab = self.km_model.predict_color(conc_dict)
            delta_e = ColorDifferenceCalculator.delta_e_cie76(predicted_lab, target_lab)
        except:
            delta_e = 1000.0  # Large penalty
        
        # Cost objective
        cost = sum(
            conc * self.km_model.pigments[name].cost_per_unit
            for name, conc in zip(self.pigment_names, concentrations)
        )
        
        # Complexity objective (number of pigments + concentration variance)
        num_pigments = np.sum(concentrations > 0.001)
        concentration_variance = np.var(concentrations[concentrations > 0.001]) if num_pigments > 0 else 0
        complexity = num_pigments + concentration_variance
        
        return delta_e, cost, complexity
    
    def nsga2_optimization(self, target_lab: np.ndarray,
                          population_size: int = 100,
                          generations: int = 500,
                          crossover_prob: float = 0.9,
                          mutation_prob: float = 0.1) -> List[Dict]:
        """
        NSGA-II multi-objective optimization
        
        Args:
            target_lab: Target Lab color
            population_size: Population size
            generations: Number of generations
            crossover_prob: Crossover probability
            mutation_prob: Mutation probability
            
        Returns:
            Pareto optimal solutions
        """
        n_vars = len(self.pigment_names)
        bounds = [(0, self.km_model.pigments[name].max_concentration) 
                 for name in self.pigment_names]
        
        # Initialize population
        population = []
        for _ in range(population_size):
            individual = np.array([np.random.uniform(b[0], b[1]) for b in bounds])
            population.append(individual)
        
        # Evolution loop
        for generation in range(generations):
            # Evaluate objectives for all individuals
            objectives = []
            for individual in population:
                obj = self._calculate_objectives(individual, target_lab)
                objectives.append(obj)
            
            # Non-dominated sorting and crowding distance
            fronts = self._non_dominated_sort(objectives)
            crowding_distances = self._calculate_crowding_distance(objectives, fronts)
            
            # Selection
            new_population = []
            
            # Elite selection from non-dominated fronts
            for front in fronts:
                if len(new_population) + len(front) <= population_size:
                    new_population.extend([population[i] for i in front])
                else:
                    # Sort by crowding distance and take best
                    front_distances = [(i, crowding_distances[i]) for i in front]
                    front_distances.sort(key=lambda x: x[1], reverse=True)
                    
                    remaining = population_size - len(new_population)
                    for i, _ in front_distances[:remaining]:
                        new_population.append(population[i])
                    break
            
            # Genetic operations
            offspring = []
            while len(offspring) < population_size:
                # Tournament selection
                parent1 = self._tournament_selection(population, objectives, fronts, crowding_distances)
                parent2 = self._tournament_selection(population, objectives, fronts, crowding_distances)
                
                # Crossover
                if np.random.random() < crossover_prob:
                    child1, child2 = self._sbx_crossover(parent1, parent2, bounds)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                # Mutation
                if np.random.random() < mutation_prob:
                    child1 = self._polynomial_mutation(child1, bounds)
                if np.random.random() < mutation_prob:
                    child2 = self._polynomial_mutation(child2, bounds)
                
                offspring.extend([child1, child2])
            
            # Replace population
            population = offspring[:population_size]
            
            if generation % 50 == 0:
                print(f"Generation {generation}/{generations}")
        
        # Extract final Pareto front
        final_objectives = [self._calculate_objectives(ind, target_lab) for ind in population]
        final_fronts = self._non_dominated_sort(final_objectives)
        
        pareto_solutions = []
        for i in final_fronts[0]:  # First front is Pareto optimal
            conc_dict = {name: conc for name, conc in zip(self.pigment_names, population[i])}
            pareto_solutions.append({
                'concentrations': conc_dict,
                'objectives': final_objectives[i],
                'delta_e': final_objectives[i][0],
                'cost': final_objectives[i][1],
                'complexity': final_objectives[i][2]
            })
        
        self.pareto_front = pareto_solutions
        return pareto_solutions
    
    def _non_dominated_sort(self, objectives: List[Tuple]) -> List[List[int]]:
        """Non-dominated sorting for NSGA-II"""
        n = len(objectives)
        fronts = []
        domination_count = [0] * n
        dominated_solutions = [[] for _ in range(n)]
        
        # First front
        front = []
        for i in range(n):
            for j in range(n):
                if i != j:
                    if self._dominates(objectives[i], objectives[j]):
                        dominated_solutions[i].append(j)
                    elif self._dominates(objectives[j], objectives[i]):
                        domination_count[i] += 1
            
            if domination_count[i] == 0:
                front.append(i)
        
        fronts.append(front)
        
        # Subsequent fronts
        while len(fronts[-1]) > 0:
            next_front = []
            for i in fronts[-1]:
                for j in dominated_solutions[i]:
                    domination_count[j] -= 1
                    if domination_count[j] == 0:
                        next_front.append(j)
            
            if len(next_front) > 0:
                fronts.append(next_front)
            else:
                break
        
        return fronts[:-1] if not fronts[-1] else fronts
    
    def _dominates(self, obj1: Tuple, obj2: Tuple) -> bool:
        """Check if obj1 dominates obj2 (minimization)"""
        return all(o1 <= o2 for o1, o2 in zip(obj1, obj2)) and any(o1 < o2 for o1, o2 in zip(obj1, obj2))
    
    def _calculate_crowding_distance(self, objectives: List[Tuple], fronts: List[List[int]]) -> List[float]:
        """Calculate crowding distance for each solution"""
        n = len(objectives)
        distances = [0.0] * n
        
        for front in fronts:
            if len(front) <= 2:
                for i in front:
                    distances[i] = float('inf')
                continue
            
            # For each objective
            for obj_idx in range(len(objectives[0])):
                # Sort by objective value
                front_objectives = [(i, objectives[i][obj_idx]) for i in front]
                front_objectives.sort(key=lambda x: x[1])
                
                # Boundary points get infinite distance
                distances[front_objectives[0][0]] = float('inf')
                distances[front_objectives[-1][0]] = float('inf')
                
                # Calculate distance for intermediate points
                obj_range = front_objectives[-1][1] - front_objectives[0][1]
                if obj_range > 0:
                    for j in range(1, len(front_objectives) - 1):
                        distance = (front_objectives[j+1][1] - front_objectives[j-1][1]) / obj_range
                        distances[front_objectives[j][0]] += distance
        
        return distances
    
    def _tournament_selection(self, population: List[np.ndarray], 
                            objectives: List[Tuple],
                            fronts: List[List[int]], 
                            crowding_distances: List[float],
                            tournament_size: int = 2) -> np.ndarray:
        """Tournament selection for NSGA-II"""
        tournament = np.random.choice(len(population), tournament_size, replace=False)
        
        best = tournament[0]
        best_front = None
        
        # Find front of best individual
        for front_idx, front in enumerate(fronts):
            if best in front:
                best_front = front_idx
                break
        
        for i in tournament[1:]:
            # Find front of current individual
            current_front = None
            for front_idx, front in enumerate(fronts):
                if i in front:
                    current_front = front_idx
                    break
            
            # Compare individuals
            if current_front < best_front:
                best = i
                best_front = current_front
            elif current_front == best_front and crowding_distances[i] > crowding_distances[best]:
                best = i
        
        return population[best].copy()
    
    def _sbx_crossover(self, parent1: np.ndarray, parent2: np.ndarray, 
                      bounds: List[Tuple], eta: float = 20.0) -> Tuple[np.ndarray, np.ndarray]:
        """Simulated Binary Crossover (SBX)"""
        child1 = parent1.copy()
        child2 = parent2.copy()
        
        for i in range(len(parent1)):
            if np.random.random() <= 0.5:
                if abs(parent1[i] - parent2[i]) > 1e-14:
                    x_min, x_max = bounds[i]
                    
                    # Calculate beta
                    u = np.random.random()
                    if u <= 0.5:
                        beta = (2 * u) ** (1 / (eta + 1))
                    else:
                        beta = (1 / (2 * (1 - u))) ** (1 / (eta + 1))
                    
                    # Generate offspring
                    child1[i] = 0.5 * ((1 + beta) * parent1[i] + (1 - beta) * parent2[i])
                    child2[i] = 0.5 * ((1 - beta) * parent1[i] + (1 + beta) * parent2[i])
                    
                    # Apply bounds
                    child1[i] = np.clip(child1[i], x_min, x_max)
                    child2[i] = np.clip(child2[i], x_min, x_max)
        
        return child1, child2
    
    def _polynomial_mutation(self, individual: np.ndarray, bounds: List[Tuple], 
                           eta: float = 20.0, prob: float = 0.1) -> np.ndarray:
        """Polynomial mutation"""
        mutated = individual.copy()
        
        for i in range(len(individual)):
            if np.random.random() <= prob:
                x_min, x_max = bounds[i]
                delta_max = x_max - x_min
                
                u = np.random.random()
                if u < 0.5:
                    delta = (2 * u) ** (1 / (eta + 1)) - 1
                else:
                    delta = 1 - (2 * (1 - u)) ** (1 / (eta + 1))
                
                mutated[i] += delta * delta_max
                mutated[i] = np.clip(mutated[i], x_min, x_max)
        
        return mutated


class HyperparameterOptimizer:
    """Optimize hyperparameters using Optuna"""
    
    def __init__(self, model_trainer: Callable):
        self.model_trainer = model_trainer
        self.study = None
        self.best_params = None
    
    def optimize_svm_parameters(self, X_train: np.ndarray, y_train: np.ndarray,
                              X_val: np.ndarray, y_val: np.ndarray,
                              n_trials: int = 100) -> Dict:
        """Optimize SVM hyperparameters"""
        
        def objective(trial):
            # Suggest hyperparameters
            C = trial.suggest_float('C', 0.1, 100, log=True)
            kernel = trial.suggest_categorical('kernel', ['linear', 'rbf', 'poly'])
            
            if kernel == 'rbf':
                gamma = trial.suggest_float('gamma', 1e-4, 1, log=True)
                params = {'C': C, 'kernel': kernel, 'gamma': gamma}
            elif kernel == 'poly':
                gamma = trial.suggest_float('gamma', 1e-4, 1, log=True)
                degree = trial.suggest_int('degree', 2, 5)
                params = {'C': C, 'kernel': kernel, 'gamma': gamma, 'degree': degree}
            else:
                params = {'C': C, 'kernel': kernel}
            
            # Train model and return validation accuracy
            accuracy = self.model_trainer(X_train, y_train, X_val, y_val, params)
            return accuracy
        
        # Create study
        self.study = optuna.create_study(direction='maximize')
        self.study.optimize(objective, n_trials=n_trials)
        
        self.best_params = self.study.best_params
        
        return {
            'best_params': self.best_params,
            'best_score': self.study.best_value,
            'study': self.study
        }
    
    def optimize_cnn_parameters(self, train_data: Any, val_data: Any,
                              n_trials: int = 50) -> Dict:
        """Optimize CNN hyperparameters"""
        
        def objective(trial):
            # Suggest hyperparameters
            lr = trial.suggest_float('learning_rate', 1e-4, 1e-2, log=True)
            batch_size = trial.suggest_categorical('batch_size', [16, 32, 64, 128])
            hidden_size = trial.suggest_categorical('hidden_size', [128, 256, 512, 1024])
            dropout_rate = trial.suggest_float('dropout_rate', 0.1, 0.5)
            
            params = {
                'learning_rate': lr,
                'batch_size': batch_size,
                'hidden_size': hidden_size,
                'dropout_rate': dropout_rate
            }
            
            # Train model and return validation accuracy
            accuracy = self.model_trainer(train_data, val_data, params)
            return accuracy
        
        # Create study
        self.study = optuna.create_study(direction='maximize')
        self.study.optimize(objective, n_trials=n_trials)
        
        self.best_params = self.study.best_params
        
        return {
            'best_params': self.best_params,
            'best_score': self.study.best_value,
            'study': self.study
        }


class AdaptiveOptimizer:
    """Adaptive optimization that learns from previous solutions"""
    
    def __init__(self, km_model: KubelkaMunkModel):
        self.km_model = km_model
        self.solution_history = []
        self.performance_history = []
        self.learned_patterns = {}
    
    def add_solution(self, target_lab: np.ndarray, 
                    concentrations: Dict[str, float],
                    delta_e: float, cost: float) -> None:
        """Add successful solution to history"""
        self.solution_history.append({
            'target_lab': target_lab.copy(),
            'concentrations': concentrations.copy(),
            'delta_e': delta_e,
            'cost': cost,
            'timestamp': time.time()
        })
        
        self.performance_history.append(delta_e)
        self._update_learned_patterns()
    
    def _update_learned_patterns(self) -> None:
        """Update learned patterns from solution history"""
        if len(self.solution_history) < 5:
            return
        
        # Analyze color regions and preferred pigment combinations
        recent_solutions = self.solution_history[-10:]  # Last 10 solutions
        
        for solution in recent_solutions:
            lab = solution['target_lab']
            conc = solution['concentrations']
            
            # Categorize by color region (simplified)
            if lab[0] > 70:  # Light colors
                region = 'light'
            elif lab[0] < 30:  # Dark colors
                region = 'dark'
            else:
                region = 'medium'
            
            # Track successful pigment combinations
            active_pigments = [name for name, c in conc.items() if c > 0.01]
            
            if region not in self.learned_patterns:
                self.learned_patterns[region] = {
                    'common_pigments': {},
                    'avg_concentrations': {},
                    'success_rate': 0
                }
            
            # Update pattern statistics
            for pigment in active_pigments:
                if pigment not in self.learned_patterns[region]['common_pigments']:
                    self.learned_patterns[region]['common_pigments'][pigment] = 0
                self.learned_patterns[region]['common_pigments'][pigment] += 1
    
    def suggest_initial_guess(self, target_lab: np.ndarray) -> np.ndarray:
        """Suggest initial guess based on learned patterns"""
        # Determine color region
        if target_lab[0] > 70:
            region = 'light'
        elif target_lab[0] < 30:
            region = 'dark'
        else:
            region = 'medium'
        
        pigment_names = list(self.km_model.pigments.keys())
        initial_guess = np.zeros(len(pigment_names))
        
        if region in self.learned_patterns:
            patterns = self.learned_patterns[region]
            
            # Use most common pigments for this region
            total_count = sum(patterns['common_pigments'].values())
            for i, pigment in enumerate(pigment_names):
                if pigment in patterns['common_pigments']:
                    frequency = patterns['common_pigments'][pigment] / total_count
                    initial_guess[i] = min(frequency * 0.5, 0.3)  # Scale down
        else:
            # Default initialization
            initial_guess = np.full(len(pigment_names), 0.1)
        
        return initial_guess
    
    def adaptive_optimize(self, target_lab: np.ndarray,
                         max_iterations: int = 1000,
                         learning_rate: float = 0.1) -> Dict:
        """Optimize using adaptive approach"""
        # Get intelligent initial guess
        initial_guess = self.suggest_initial_guess(target_lab)
        
        # Use differential evolution with adaptive parameters
        bounds = [(0, self.km_model.pigments[name].max_concentration) 
                 for name in self.km_model.pigments.keys()]
        
        # Adaptive population size based on problem difficulty
        base_popsize = 15
        if len(self.solution_history) > 10:
            recent_performance = np.mean(self.performance_history[-10:])
            if recent_performance > 3.0:  # Poor recent performance
                popsize = base_popsize * 2
            else:
                popsize = base_popsize
        else:
            popsize = base_popsize
        
        def objective(x):
            conc_dict = {name: conc for name, conc in zip(self.km_model.pigments.keys(), x)}
            try:
                predicted_lab = self.km_model.predict_color(conc_dict)
                delta_e = ColorDifferenceCalculator.delta_e_cie76(predicted_lab, target_lab)
                
                # Add cost penalty (adaptive weight)
                cost_weight = 0.05 + learning_rate * len(self.solution_history) * 0.01
                cost = sum(conc * self.km_model.pigments[name].cost_per_unit 
                          for name, conc in conc_dict.items())
                
                return delta_e + cost_weight * cost
            except:
                return 1000.0
        
        # Optimize
        result = differential_evolution(
            objective,
            bounds,
            maxiter=max_iterations,
            popsize=popsize,
            seed=42,
            init='latinhypercube'
        )
        
        # Process results
        optimal_concentrations = result.x
        conc_dict = {name: conc for name, conc in zip(self.km_model.pigments.keys(), optimal_concentrations)}
        
        predicted_lab = self.km_model.predict_color(conc_dict)
        delta_e = ColorDifferenceCalculator.delta_e_cie76(predicted_lab, target_lab)
        cost = sum(conc * self.km_model.pigments[name].cost_per_unit 
                  for name, conc in conc_dict.items())
        
        # Add to history if successful
        if delta_e < 5.0:  # Reasonable threshold
            self.add_solution(target_lab, conc_dict, delta_e, cost)
        
        return {
            'concentrations': conc_dict,
            'predicted_lab': predicted_lab,
            'delta_e': delta_e,
            'cost': cost,
            'optimization_result': result,
            'used_adaptive_guess': True
        }


class PerformanceProfiler:
    """Profile and analyze optimization performance"""
    
    def __init__(self):
        self.profiles = []
    
    def profile_optimization(self, optimizer_func: Callable, 
                           test_colors: List[np.ndarray],
                           **optimizer_kwargs) -> Dict:
        """Profile optimization performance on test colors"""
        results = {
            'delta_es': [],
            'costs': [],
            'times': [],
            'success_rate': 0,
            'avg_delta_e': 0,
            'avg_cost': 0,
            'avg_time': 0
        }
        
        successful = 0
        
        for i, target_lab in enumerate(test_colors):
            start_time = time.time()
            
            try:
                result = optimizer_func(target_lab, **optimizer_kwargs)
                end_time = time.time()
                
                delta_e = result['delta_e']
                cost = result['cost']
                duration = end_time - start_time
                
                results['delta_es'].append(delta_e)
                results['costs'].append(cost)
                results['times'].append(duration)
                
                if delta_e <= 2.0:  # Success threshold
                    successful += 1
                
                print(f"Color {i+1}/{len(test_colors)}: ΔE={delta_e:.2f}, Cost={cost:.2f}, Time={duration:.2f}s")
                
            except Exception as e:
                print(f"Error optimizing color {i+1}: {e}")
                results['delta_es'].append(float('inf'))
                results['costs'].append(float('inf'))
                results['times'].append(0)
        
        # Calculate summary statistics
        valid_delta_es = [de for de in results['delta_es'] if de != float('inf')]
        valid_costs = [c for c in results['costs'] if c != float('inf')]
        valid_times = [t for t in results['times'] if t > 0]
        
        results['success_rate'] = successful / len(test_colors)
        results['avg_delta_e'] = np.mean(valid_delta_es) if valid_delta_es else float('inf')
        results['avg_cost'] = np.mean(valid_costs) if valid_costs else float('inf')
        results['avg_time'] = np.mean(valid_times) if valid_times else 0
        
        return results
    
    def compare_optimizers(self, optimizers: Dict[str, Callable],
                          test_colors: List[np.ndarray]) -> pd.DataFrame:
        """Compare multiple optimizers"""
        comparison_results = []
        
        for name, optimizer_func in optimizers.items():
            print(f"\nTesting optimizer: {name}")
            profile = self.profile_optimization(optimizer_func, test_colors)
            
            comparison_results.append({
                'optimizer': name,
                'success_rate': profile['success_rate'],
                'avg_delta_e': profile['avg_delta_e'],
                'avg_cost': profile['avg_cost'],
                'avg_time': profile['avg_time'],
                'std_delta_e': np.std([de for de in profile['delta_es'] if de != float('inf')]),
                'std_cost': np.std([c for c in profile['costs'] if c != float('inf')]),
                'std_time': np.std([t for t in profile['times'] if t > 0])
            })
        
        return pd.DataFrame(comparison_results)


def create_optimization_pipeline(km_model: KubelkaMunkModel,
                               optimization_method: str = 'adaptive') -> object:
    """
    Create complete optimization pipeline
    
    Args:
        km_model: Kubelka-Munk model
        optimization_method: Optimization method ('basic', 'multi_objective', 'adaptive')
        
    Returns:
        Configured optimization pipeline
    """
    if optimization_method == 'basic':
        return MixingOptimizer(km_model)
    elif optimization_method == 'multi_objective':
        return MultiObjectiveOptimizer(km_model)
    elif optimization_method == 'adaptive':
        return AdaptiveOptimizer(km_model)
    else:
        raise ValueError(f"Unknown optimization method: {optimization_method}")


def visualize_pareto_front(pareto_solutions: List[Dict]) -> None:
    """Visualize Pareto front from multi-objective optimization"""
    if not pareto_solutions:
        print("No Pareto solutions to visualize")
        return
    
    delta_es = [sol['delta_e'] for sol in pareto_solutions]
    costs = [sol['cost'] for sol in pareto_solutions]
    complexities = [sol['complexity'] for sol in pareto_solutions]
    
    fig = plt.figure(figsize=(15, 5))
    
    # ΔE vs Cost
    ax1 = fig.add_subplot(131)
    scatter = ax1.scatter(delta_es, costs, c=complexities, cmap='viridis', alpha=0.7)
    ax1.set_xlabel('ΔE')
    ax1.set_ylabel('Cost')
    ax1.set_title('Pareto Front: ΔE vs Cost')
    plt.colorbar(scatter, ax=ax1, label='Complexity')
    
    # ΔE vs Complexity
    ax2 = fig.add_subplot(132)
    scatter = ax2.scatter(delta_es, complexities, c=costs, cmap='plasma', alpha=0.7)
    ax2.set_xlabel('ΔE')
    ax2.set_ylabel('Complexity')
    ax2.set_title('Pareto Front: ΔE vs Complexity')
    plt.colorbar(scatter, ax=ax2, label='Cost')
    
    # Cost vs Complexity
    ax3 = fig.add_subplot(133)
    scatter = ax3.scatter(costs, complexities, c=delta_es, cmap='coolwarm', alpha=0.7)
    ax3.set_xlabel('Cost')
    ax3.set_ylabel('Complexity')
    ax3.set_title('Pareto Front: Cost vs Complexity')
    plt.colorbar(scatter, ax=ax3, label='ΔE')
    
    plt.tight_layout()
    plt.show()


def optimize_system_parameters(km_model: KubelkaMunkModel,
                             validation_colors: List[np.ndarray],
                             n_trials: int = 100) -> Dict:
    """
    Optimize entire system parameters using validation set
    
    Args:
        km_model: Kubelka-Munk model
        validation_colors: Colors for validation
        n_trials: Number of optimization trials
        
    Returns:
        Best system parameters
    """
    def objective(trial):
        # Suggest system parameters
        cost_weight = trial.suggest_float('cost_weight', 0.01, 0.5, log=True)
        complexity_weight = trial.suggest_float('complexity_weight', 0.01, 0.2, log=True)
        max_iterations = trial.suggest_int('max_iterations', 500, 2000)
        population_size = trial.suggest_int('population_size', 10, 50)
        
        # Test on validation colors
        optimizer = MixingOptimizer(km_model)
        total_score = 0
        
        for target_lab in validation_colors:
            try:
                result = optimizer.optimize_formula(
                    target_lab,
                    cost_weight=cost_weight,
                    complexity_weight=complexity_weight,
                    max_iterations=max_iterations
                )
                
                # Scoring function (lower is better)
                score = result['delta_e'] + 0.1 * result['total_cost']
                total_score += score
                
            except:
                total_score += 100  # Penalty for failed optimization
        
        return total_score / len(validation_colors)
    
    # Run optimization
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=n_trials)
    
    return {
        'best_params': study.best_params,
        'best_score': study.best_value,
        'study': study
    }