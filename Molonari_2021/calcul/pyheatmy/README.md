# PyHeatMy

This version of pyheatmy is a development version. Some features are not yet implemented or are incomplete.
Some bugs may also appear, do not hesitate if you have any problem.

We do not guarantee any reliability on the resulting values of the calculations, however the data format will remain constant during their full implementation. Think of this code as a template that will remain persistent when the features are reliable in their results.

## Installation :

```sh
pip install -r requirements.txt
pip install -e .
```

## Examples :

In the repository there is a demo file in notebook format : [demo.ipynb](https://github.com/mathisbrdn/pyheatmy/blob/master/demo.ipynb).

We know that the code is not yet documented. Please use this notebook as a basis while we write it.

## Please note :

This library implements in addition to the api of the MOLONARI project property for most results.
We advise you not to use them if you want to use another pyheat library easily.
Each property has its own public getter in *get_nameproperty* format.

To ensure consistent results, a checker is added where the user cannot call results if he has not executed the corresponding methods. In particular, if you run a Bayesian inversion the results of the transient model must be recalculated.

***

## License

MIT

2021 Mathis Bourdin & Youri Tchouboukoff