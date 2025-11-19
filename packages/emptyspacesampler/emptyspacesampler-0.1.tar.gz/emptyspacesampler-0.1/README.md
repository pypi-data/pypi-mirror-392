# EmptySpaceSampler

An advanced Optuna sampler that uses the `ess` ([EmptySpaceSearch](https://pypi.org/project/EmptySpaceSearch/)) library to iteratively find and sample the largest unexplored "gaps" in the search space.

## The problem

Standard samplers can struggle with coverage:

- `RandomSampler` can create "clumps," leaving large areas unexplored by pure chance.
- `TPESampler` (and other Bayesian methods) quickly focus on "promising" areas. This is good for exploitation but bad for exploration. If the initial samples are poor, the sampler may never find better regions.

## The Solution: EmptySpaceSampler

`ESSampler` is designed to provide maximum coverage by iteratively filling in the largest empty regions of the search space.

## How It Works

1. **Trial 1 (Random):** The sampler lets RandomSampler (via sample_independent) handle the very first trial. This trial's parameters are used to define the boundaries of the full search space.
2. **Sampler Initialization (Trial 2):**
    - `ESSampler` detects the now-defined search space.
    - It generates an initial batch of n (default 10) random "anchor points" in a normalized [0, 1] unit cube.
    - It calls the ess.esa() function, feeding it these anchors. ess.esa() returns n new points that are located in the largest "empty" spaces between the anchors.
    - The sampler creates an internal queue of 2*n points (the anchors + the new points).
3. Iterative Sampling (Trials 2+):
    - For the next 2*n trials, `ESSampler` simply serves one point from its internal queue.
    - Each [0, 1] point is intelligently mapped to the actual parameter values, correctly handling log, step, int, and categorical distributions.
4. Refilling the Queue:
    - Once the queue is empty, the entire set of 2*n points that were just sampled become the new anchors.
    - ess.esa() is called again with these new, denser anchors to find the next n points in the now-smaller gaps.
    - This process repeats, progressively filling the search space with more and more detail.

## Features

* Iterative Gap-Filling: Uses ess.esa to progressively sample the largest unexplored regions.
* Automatic Space Detection: No setup needed. The sampler discovers the search space from the first trial.
* Full Distribution Support: A robust mapping function correctly converts [0, 1] unit values to Float, Int, and Categorical types, including log and step modifiers.
* Configurable Intensity: You can control how many points are generated in each batch with the samples parameter.


## Authors

* [**Mário Antunes**](https://github.com/mariolpantunes)

## License

This project is licensed under the [MIT License](LICENSE).