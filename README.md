This repository contains nearly all the data and notebooks that were used throughout my PhD thesis. Most of them are in
the [dahu](dahu) directory (the Grid'5000 cluster that I used the most). This is then organized by experiment type (e.g.
[dahu/blas](dahu/blas) contains the `dgemm` calibrations while [dahu/hpl](dahu/hpl) contains the real HPL runs).

The data is quasi-exclusively stored as [peanut](https://github.com/Ezibenroc/peanut) archives. These are `.zip` files
containing the experiment data and meta-data.

The jupyter notebooks are the analyses of the experiments. Very often I repeated several times a same experiment, so I
re-executed a same notebook and applied some modifications. The different versions of a notebook can be accessed through
git history. Copies are also directly available in my laboratory journal.
