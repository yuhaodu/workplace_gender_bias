# Introduction

This is the beginnings of the gender simulation in the workplace code

# Running the model

- The model runs using python 2.7 and requires only standard libraries, pandas and numpy

- To run the model from the command line, you need to provide several arguments:

```
python model.py [path to experiment file] [path to default params file] [path to desired output folder] [n_replications_per_condition] [n_cores] [random seed]
```

- ```path to experiment file``` - Path to a file describing experimental parameters.  There is an example in ```experiment.yaml```
- ```path to default params file``` - Path to the default parameters for the model. An example is ```default_params.yaml```
- ```path to desired output folder``` - Where the output is located. See ```R/plot_results.R``` for an example of how to plot the results
- ```n_replications_per_condition``` - How many replications per simulation?
- ```n_cores``` - how many cores you want to use to run the simulation (1 if you're not sure)
- ```random seed``` - a random seed for the model (using the same seed over and over again should replicate your results)

An example command to run the model and replicate results for the "minimal" condition:

```python model.py minimal_nodownward.yaml default_params.yaml minimal 100 1 14260```

Example to replicate minimal with downward causation:

```python model.py minimal.yaml default_params.yaml minimal 100 1 14260```


# Todo

- Actually give some better documentation on the model and how to change it and what the parameters are
- Better installation and usage code and explanations
- Other potential factors (e.g. the likeability stuff)