# NR-population-mobility

Database of New Rochelle, NY, US and code for its conversion into an agent-based computational model

## Code structure

Details about the code and usage examples can be found in the documentation, and the manual.

The directories are as follows: 
- `src` - python source files
- `tools` - python scripts for general use throughout the repository
- `tests` and `input_verification` - tests developed for this code
- `NewRochelle` - town database and Census data 
- `created_communities` - final populations to be used in ABM 
	- `covid_model` - final population used in the ABM code  
  
In the `src` and `tests` the subdirectories `mobility` contain the code used for ABMs with human mobility. 

## Database

The database, located in `NewRochelle` directory consists of Census data and manually collected information on all the public and residential buildings in New Rochelle, NY, US. The building information, original and preprocessed for converting into an ABM is located in the `database` directory. Preprocessed relevant census data is in the `census_data` directory. 

## Running the code

The code is fully written in Python, and was ran with Python 3.6 and 3.8. Other 3.X versions should work as well.  

The code was developed and tested on MacOS and Linux, some of its parts may not be compatible with Windows.

## Tests

Tests consisted of checking generated community structure with Python and MATLAB scripts. Visual verification was also part of the process. Some of the tests are now automated.

## Documentation

Documentation and a user manual will soon be provided. 

## Notes

We encourage the users and developers to report any issues, including platform incompatibility and failed tests on our GitHub page or directly, by sending us an email.

## Citation

If you find this software useful, consider citing

*Truszkowska, A., Thakore, M., Zino, L., Butail, S., Caroppo, E., Jiang, Z.P., Rizzo, A. and Porfiri, M., 2021. Designing the Safe Reopening of US Towns Through High‐Resolution Agent‐Based Modeling. Advanced theory and simulations, 4(9) p.2100157.*
