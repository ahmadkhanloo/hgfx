# Bayesian Workflow for Generative Modeling in Computational Psychiatry

This project contains the analysis pipeline of the SPIRL study. The individual steps of the analysis are outlined in detail in the corresponding analysis plan available at <https://doi.org/10.5281/zenodo.10669944>. The data from the SPIRL study are available on Zenodo (<https://doi.org/10.5281/zenodo.10663643>). The corresponding paper is entitled 'Bayesian Workflow for Generative Modeling in Computational Psychiatry' and is available at <https://doi.org/10.5334/cpsy.116>.


# Contributors / Roles
|                               |                                             |
| ----------------------------- | ------------------------------------------- |
| Project lead / analysis:      | Alex J. Hess                                |
| Code review:                  | Jakob Heinzle                               |
| Abbreviation:                 | SPIRL (study acronym)                       |
| Date:                         | 16.02.2024                                  |
| License:                      | GNU General Public License v3.0             |


# Summary

In this project, we present a novel set of response models for Hierarchical Gaussian Filter (HGF) models that allow for simultaneous inference from two different data modalities. Using both simulations and empirical data from a speed-incentivised associative learning (SPIRL) task, we show that harnessing information from two different data streams (binary responses and response times) improves the accuracy of inference. Our analysis follows and highlights the general steps of a Bayesian workflow for generative modelling applications in Computational Psychiatry that includes the specification of an initial model space, prior elicitation and prior predictive checking, the choice of a Bayesian inference algorithm and concurrent validation of computation, model inversion diagnostics, model comparison procedures and model evaluation.

This project was conducted at the Translational Neuromodeling Unit (TNU) in Zurich by the project lead (AJH), in collaboration with colleagues from ETH Zurich, University of Zurich, the University of Otago, the Max Planck Institute for Metabolism Research in Cologne and the Aarhus University.

# Getting started

## 0. Requirements

The analysis pipeline was designed to run on the Euler cluster at ETH Zurich which allows to run computationally expensive parts of the analysis in a parallelized fashion (for details, see <https://scicomp.ethz.ch/wiki/Euler>).

You will need [MATLAB](https://www.mathworks.com/products/matlab.html) installed to run this code. The code was developed and tested using MATLAB R2019b. Plots are generated differently depending on your MATLAB version.

The analysis pipeline relies on the following open-source third party software which is integrated in this repository as submodules:
- [TAPAS](https://translationalneuromodeling.github.io/tapas/) (commit 604c568)
- [VBA Toolbox](https://mbb-team.github.io/VBA-toolbox/) (commit aa46573)
- [RainCloudPlots](https://github.com/RainCloudPlots/RainCloudPlots) (commit d5085be)

## 1. Install repository

Create a local version of this repository including all submodules using the commands (ssh protocol used for communication with the ETH GitLab and github.com):

```
git clone git@gitlab.ethz.ch:tnu/code/hessetal_spirl_analysis.git
cd hessetal_spirl_analysis/
git submodule update --init
```

## 2. Get data

The data set is freely available on Zenodo (<https://doi.org/10.5281/zenodo.10663643>). Download and save the files `SPIRL_main_59sub_preprocessed_IncludedInAnalysis.mat` and `SPIRL_pilot_20sub_preprocessed_IncludedInAnalysis.mat` within the `data` folder of the code repository.

**Note**: The available data set is already preprocessed. This means that the data were checked for meeting our criteria for inclusion into the analysis as pre-specified in sections 5 and 7 of the [analysis plan](https://doi.org/10.5281/zenodo.10669944).

## 3. Run the analysis

### Euler cluster

To run the code and generate the figures, you need to run the `main.sh` script. Navigate to the directory of the analysis pipeline and submit the job request using the following command:

```
bsub < main
```

All the results and figures will be saved into the `results` and the `figures` folder. If you wish to display the results from the statistical analyses in a compact way, run the function `job_runner_print_stats.m` from the main directory of the git repo. Likewise for the function `job_runner_paper_figs.m` to create the figures used for the paper.

### local workstation

Alternatively, you can run the entire analysis on a local workstation. However, to reduce the computational demand of the analysis, it is recommended to switch from a multistart to a singlestart optimization regime for model inversion. This can be achieved by modifying the field `options.opt_config.nRandInit` in line 75 of the `spirl_setspecs.m` file. Additionally, the number of simulations runs for the family level recovery analyses should be reduced by modifying the field `n_jobs_sim` in line 54 of the `spirl_setspecs.m` file. The script `main_local_serial.m` can then be used to run the analysis pipeline, create figures and display the results from statistical analyses. This script makes use of MATLAB's Parallel Computing Toolbox. The number of local cores used by default is 4. If you wish to use a different number of clusters, change the variable 'local_cores' in line 37 of the `main_local_serial.m` script. In case you wish to run the script without using the Parallel Computing Toolbox (not recommended), the script needs to be adapted manually.

**Note**: Reducing the computational complexity of the model inversion step comes at the expense of being able to reproduce the results and figures exactly as reported in the original publication. This can nonetheless be an instructive exercise in order to get familiar with the individual steps of the analysis.

# License information
This software is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This software is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You can find the details of the GNU General Public License v3.0 in the file `LICENSE` or under <https://www.gnu.org/licenses/>.

# Contact information

Suggestions and feedback are always welcome and should be directed to the project lead (AJH) via e-mail: <hess@biomed.ee.ethz.ch>

# Reference

Hess, A.J., Iglesias, S., Köchli, L., Marino, S., Müller-Schrader, M., Rigoux, L., Mathys, C., Harrison, O.K., Heinzle, J., Frässle, S. and Stephan, K.E. (2025) ‘Bayesian Workflow for Generative Modeling in Computational Psychiatry’, <i>Computational Psychiatry</i>, 9(1), p. 76–99. Available at: <https://doi.org/10.5334/cpsy.116>.
