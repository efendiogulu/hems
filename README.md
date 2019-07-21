# Home Energy Management System for Small Prosumers Considering Electric Vehicle Load Scheduling

Home Energy Management System (HEMS) is a device which is developed to fulfill
the demands of the industry and the prosumers. The project contains codes for 2 different optimization techniques such as MILP and Stochastic Optimization as well as the scenario generation for the SO and a base scenario which simulates the household behaviour without a HEMS. The implementation is achieved with **Python**.

Each algorithm is created to have different objective functions in order to satisfy the different demands of the users such as energy minimization, cost minimization and profit maximization.


## Installation


In order to run the scripts please make sure **Pyomo**, **Gurobi solver** and **Anaconda** are installed properly on your machine.

You can refer to following manuals for installation:

* Pyomo:
```html
http://www.pyomo.org/installation
```

* Gurobi:
```html
http://www.gurobi.com/registration/download-reg
```

* Anaconda:
```html
https://www.anaconda.com/distribution/
```

## Usage

The repository is organized as 4 different sub-projects. 

To run, simply open the sub-project using Spyder and click Run.

## Important Notice

The project requires four input datasets: **availability of electric vehicle**, **solar power generation**, **power demand of the household**, and **the electricity price**. The full versions of these datasets are not included in this repository due to licensing issues. 

However, these 4 datasets can be replaced with sets containing 15 minutes of resolution for a year.

Feel free to contact the author for further instructions.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## Contact

E-mail: mert.karadeniz@yahoo.com
