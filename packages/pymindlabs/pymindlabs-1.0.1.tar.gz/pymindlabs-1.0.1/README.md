# PyMIND

This implements *MultIscale Nemirowski-Dantzig (MIND)* estimator in nonparametric regression (or denoising). It is a translation of the Matlab package ["MIND"](https://github.com/housenli/MIND). 
MIND minimizes a general regularization term under certain multiscale constraints in terms of dictionaries. It is a collection of methods, includes 
-  Haltmeier, M., Li, H., & Munk, A. (2022). A variational view on statistical multiscale estimation. Annual Review of Statistics and Its Application, [9, 343--372](https://www.annualreviews.org/doi/abs/10.1146/annurev-statistics-040120-030531).
-  del Alamo, M., Li, H., & Munk, A. (2021). Frame-constrained total variation regularization for white noise regression. The Annals of Statistics, [49(3), 1318--1346](https://projecteuclid.org/journals/annals-of-statistics/volume-49/issue-3/Frame-constrained-total-variation-regularization-for-white-noise-regression/10.1214/20-AOS2001.short).
-  Grasmair, M., Li, H., & Munk, A. (2018). Variational multiscale nonparametric regression: Smooth functions. In Annales de l'Institut Henri Poincaré, Probabilités et Statistiques ([Vol. 54, No. 2, pp. 1058-1097](https://projecteuclid.org/euclid.aihp/1524643240)). Institut Henri Poincaré.
- Frick, K., Marnitz, P., & Munk, A. (2013). Statistical multiresolution estimation for variational imaging: with an application in Poisson-biophotonics. Journal of Mathematical Imaging and Vision, [46(3), 370-387](https://link.springer.com/article/10.1007/s10851-012-0368-5).
- Frick, K., Marnitz, P., & Munk, A. (2012). Statistical multiresolution Dantzig estimation in imaging: Fundamental concepts and algorithmic framework. Electronic Journal of Statistics, [6, 231-268](https://projecteuclid.org/euclid.aihp/1524643240).

The implementation works exclusively for 2D grayscale images, and utilizes the [Chambolle-Pock algorithm](https://link.springer.com/article/10.1007/s10851-010-0251-1). For more details, please see 

\[1\] del Alamo, M., Li, H., Munk, A., & Werner, F. (2020). Variational multiscale nonparametric regression: Algorithms and implementation. Algorithms, [13(11), 296](https://doi.org/10.3390/a13110296).

## Installation

To install this package run:

    pip install git+https://github.com/housenli/pyMIND.git

## Example

Examples, as well as experiments in the paper \[1\], can be run with the file [example.py](https://gitlab.gwdg.de/hli1/pymind/-/blob/master/example.py). 

## Copyright

**pyMIND** was written by [Leo Claus Weber](https://github.com/leoc-weber), [Housen Li](https://github.com/housenli) and [Jan Victor Otte](https://github.com/JanVictor-Otte). 
