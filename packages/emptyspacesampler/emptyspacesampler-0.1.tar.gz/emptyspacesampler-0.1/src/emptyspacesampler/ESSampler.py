import math
import optuna
import typing
import logging
import numpy as np
import ess.ess as ess




from optuna.distributions import BaseDistribution
from optuna.study import Study
from optuna.trial import FrozenTrial


logger = logging.getLogger(__name__)


def _generate_scaled_samples(bounds: np.ndarray, n: int) -> np.ndarray:
    """
    Generates 'n' sample points within the given bounds, using
    manual scaling from a 0-1 unit cube.

    This method is useful for custom samplers where you first
    generate points in a unit cube (e.g., LHS, Sobol) and
    then need to scale them.

    Args:
        bounds: A NumPy array of shape (d, 2) where 'd' is the
                number of dimensions. Each row is [low_bound, high_bound].
        n: The number of sample points to generate.

    Returns:
        A NumPy array of shape (n, d) containing the sample points.
    """
    # Get the number of dimensions (d)
    # bounds.shape[0] gives the number of rows (dimensions)
    d = bounds.shape[0]

    # 1. Generate 'n' points in a 'd'-dimensional unit cube (values 0.0 to 1.0)
    # Shape will be (n, d)
    unit_samples = np.random.rand(n, d)

    # 2. Extract the low and high bounds for all dimensions
    # low_bounds will be array([0., 0.])
    # high_bounds will be array([10., 10.])
    low_bounds = bounds[:, 0]
    high_bounds = bounds[:, 1]

    # 3. Scale the unit samples to the target bounds
    # We use broadcasting to scale each column (dimension)
    # Formula: sample = low + (unit_sample * (high - low))
    scaled_samples = low_bounds + unit_samples * (high_bounds - low_bounds)

    return scaled_samples


def _generate_samples_direct(bounds: np.ndarray, n: int) -> np.ndarray:
    """
    Generates 'n' sample points within the given bounds using
    NumPy's built-in `uniform` function.

    This is the most direct and efficient way if you just
    need standard uniformly random points.

    Args:
        bounds: A NumPy array of shape (d, 2) where 'd' is the
                number of dimensions. Each row is [low_bound, high_bound].
        n: The number of sample points to generate.

    Returns:
        A NumPy array of shape (n, d) containing the sample points.
    """
    # Extract low and high bounds
    low_bounds = bounds[:, 0]
    high_bounds = bounds[:, 1]

    # np.random.uniform can take arrays for low/high bounds
    # and will broadcast them correctly to the (n, d) size.
    d = bounds.shape[0]
    return np.random.uniform(low=low_bounds, high=high_bounds, size=(n, d))


def _search_space_to_bounds(search_space):
    bounds = np.zeros(shape=(len(search_space), 2))
    for i, key in enumerate(search_space):
        bd = search_space[key]
        if type(bd) is optuna.distributions.CategoricalDistribution:
            bounds[i][0] = 0
            bounds[i][1] = len(bd.choices)
        if type(bd) is optuna.distributions.FloatDistribution:
            bounds[i][0] = bd.low
            bounds[i][1] = bd.high
        if type(bd) is optuna.distributions.IntDistribution:
            bounds[i][0] = bd.low
            bounds[i][1] = bd.high
    return bounds


def _point_to_distribution(unit_value: float, distribution: optuna.distributions.BaseDistribution):
    """
    Maps a single float value from the [0, 1] unit range to a
    valid value within the given Optuna distribution.

    This function correctly handles log scaling, steps, and
    categorical/integer types.

    Args:
        unit_value: A float between 0.0 and 1.0.
        distribution: The Optuna distribution to map to.

    Returns:
        A valid value from the distribution (float, int, or str/float/int).
    """
    
    if isinstance(distribution, optuna.distributions.CategoricalDistribution):
        # --- Categorical ---
        n_choices = len(distribution.choices)
        # Find index
        index = math.floor(unit_value * n_choices)
        # Clamp index to be safe (for unit_value = 1.0)
        index = min(n_choices - 1, index)
        return distribution.choices[index]

    elif isinstance(distribution, (optuna.distributions.FloatDistribution, optuna.distributions.IntDistribution)):
        # --- Float and Int ---
        low = distribution.low
        high = distribution.high
        # Get 'step' and 'log' attributes, handling None/False defaults
        step = getattr(distribution, 'step', None)
        log = getattr(distribution, 'log', False)

        # 1. Apply Log Scaling (if applicable)
        if log:
            # Handle log=True. Note: Optuna's IntDist.log=True is special
            if isinstance(distribution, optuna.distributions.IntDistribution):
                # For Ints, log-scale the floats, then round.
                log_low = np.log(low - 0.5)
                log_high = np.log(high + 0.5)
                scaled_value = np.exp(log_low + unit_value * (log_high - log_low))
            else:
                # For Floats, scale in log-space
                log_low = np.log(low)
                log_high = np.log(high)
                scaled_value = np.exp(log_low + unit_value * (log_high - log_low))
        else:
            # Scale linearly in the linear-space
            scaled_value = low + unit_value * (high - low)

        # 2. Apply Step (Discretization)
        if isinstance(distribution, optuna.distributions.IntDistribution):
            # For Int, step is 1 by default, but can be other int
            int_step = 1 if step is None else int(step)
            
            if log:
                # For log-int, just round the scaled value
                final_value = int(np.round(scaled_value))
            else:
                # For linear-int, snap to the nearest step
                snapped_value = low + np.round((scaled_value - low) / int_step) * int_step
                final_value = int(np.round(snapped_value))
            
        elif isinstance(distribution, optuna.distributions.FloatDistribution):
            if step is not None:
                # For Float, snap to the nearest float step
                snapped_value = low + np.round((scaled_value - low) / step) * step
                final_value = float(snapped_value)
            else:
                # No step, just use the scaled value
                final_value = float(scaled_value)
        
        # 3. Final Clamping
        # Clamp the final value to be strictly within [low, high]
        final_value = np.clip(final_value, low, high)
        
        # Ensure correct type for IntDistribution
        if isinstance(distribution, optuna.distributions.IntDistribution):
            return int(final_value)
        
        return float(final_value)

    else:
        raise TypeError(f"Unknown distribution type: {type(distribution)}")


def _point_to_sample(point:float, search_space: typing.Dict[str, BaseDistribution]):
    sample =  {}
    for i, var in enumerate(search_space):
        distribution = search_space[var]
        sample[var] = _point_to_distribution(point[i], distribution)
    return sample


class ESSampler(optuna.samplers.BaseSampler):

    def __init__(self, samples:int=10, seed:int = None):
        if seed != None:
            np.random.seed(seed)
        self.samples = samples
        self.anchors = None
        self.points = None
        self.idx = 0

    def infer_relative_search_space(self, study: optuna.study.Study, trial: optuna.trial.FrozenTrial) -> typing.Dict[str, BaseDistribution]:
        return optuna.search_space.intersection_search_space(study.trials)

    def sample_relative(self, study: Study, trial: FrozenTrial, search_space: typing.Dict[str, BaseDistribution]) -> typing.Dict[str, typing.Any]:
        if search_space == {}:
            # The relative search space is empty (it means this is the first trial of a study).
            return {}

        #bounds = utils.search_space_to_bounds(search_space)
        bounds = np.zeros((len(search_space), 2))
        bounds[:, 1] = 1

        if self.anchors is None:
            self.anchors = _generate_samples_direct(bounds, self.samples)
            points = ess.esa(self.anchors, bounds, n=self.samples)
            self.points = np.concatenate((self.anchors, points), axis=0)

        if self.idx == self.points.shape[0]:
            self.anchors = self.points
            points = ess.esa(self.anchors, bounds, n=self.samples)
            self.points = np.concatenate((self.anchors, points), axis=0)

        point = self.points[self.idx]
        self.idx += 1

        return _point_to_sample(point, search_space)

    def sample_independent(self, study, trial, param_name, param_distribution):
        independent_sampler = optuna.samplers.RandomSampler()
        point = independent_sampler.sample_independent(study, trial, param_name, param_distribution)
        return point
