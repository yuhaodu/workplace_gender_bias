# Introduction

This is the beginnings of the gender simulation in the workplace code

# Running the model

- The model runs using python 2.7 and requires only standard libraries, pandas and numpy

- To run the model from the command line, you need to provide several arguments:

```
python model.py [path to experiment file] [path to default params file] [path to desired output folder] [n_replications_per_condition] [n_cores]
```

- ```path to experiment file``` - Path to a file describing experimental parameters.  There is an example in ```experiment.yaml```
- ```path to default params file``` - Path to the default parameters for the model. An example is ```default_params.yaml```
- ```path to desired output folder``` - Where the output is located. See ```R/plot_results.R``` for an example of how to plot the results
- ```n_replications_per_condition``` - How many replications per simulation?
- ```n_cores``` - how many cores you want to use to run the simulation (1 if you're not sure)


To replicate the results in Figure 1,2, please run following codes to generate results for simulations without any empirically-validated biases (1), with all of these (2) , or with each individually (3-8):

1. ```python model.py ./parameters/nobias.yaml ./parameters/default_params_fig12.yaml ./results/NoBias 100 1 ```
2. ```python model.py ./parameters/allbias.yaml ./parameters/default_params_fig12.yaml ./results/AllBias 100 1 ```
3. ```python model.py ./parameters/rewardless.yaml ./parameters/default_params_fig12.yaml ./results/RewardLess 100 1 ```
4. ```python model.py ./parameters/penaltymore.yaml ./parameters/default_params_fig12.yaml ./results/PenaltyMore 100 1 ```
5. ```python model.py ./parameters/mixedrewardless.yaml ./parameters/default_params_fig12.yaml ./results/MixedRewardLess 100 1 ```
6. ```python model.py ./parameters/mixedpenaltymore.yaml ./parameters/default_params_fig12.yaml ./results/MixedPenaltyMore 100 1 ```
7. ```python model.py ./parameters/complain.yaml ./parameters/default_params_fig12.yaml ./results/Complain 100 1 ```
8. ```python model.py ./parameters/stretch.yaml ./parameters/default_params_fig12.yaml ./results/Stretch 100 1 ```

To replicate the results in Figure 3, please run the following code to generate results for simulations:

- ```python model.py ./parameters/intervention.yaml ./parameters/default_params_fig3.yaml ./results/weight 100 6 ```

To replicate the results in Figure 4, please run the following code to generate results for simulations:

- ```python model.py ./parameters/intervention.yaml ./parameters/default_params_fig4.yaml ./results/intervention 100 6 ```

To visualize the results, please use plot_paper.ipynb to generate figures of simulations. 


