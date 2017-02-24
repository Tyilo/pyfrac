Arbitrary precision Python REPL
===============================

The Python 3 REPL is a great integer calculator thanks to its built-in
arbitrary precision integers. Python also supports arbitrary precision
decimal floating point, but it is cumbersome to use in the REPL since
you have to wrap all number literals in a constructor call.

The `pyfrac` REPL is a Python REPL that automatically wraps number
literals in the `fractions.Fraction` constructor. Furthermore, results
are printed in decimal expansion whenever this can be done precisely
(i.e. when the denominator of the fraction is a power of twos and fives)
and in fractional form otherwise.

Example:

```
$ pyfrac
Python 3.5.2 (default, Nov 17 2016, 17:05:23) 
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
(FractionalInteractiveConsole)
>>> 1 + 1 + 1
3
>>> 0.4 + 0.3 + 0.2 + 0.1
1
>>> 4/10 + 3/10 + 2/10 + 1/10
1
>>> (1/3) * (4/7)
4/21 ≈ 0.19047619047619047
>>> 0.123 ** 20
0.000000000000000000628206215175202159781085149496179361969201
>>> (1/3) ** 20
1/3486784401 ≈ 2.8679719907924413e-10
>>> from math import sqrt
>>> sqrt(2)
float(1.4142135623730951)
>>> sqrt(2) == float(1.4142135623730951)
True
>>> sqrt(2) == 1.4142135623730951
False
>>> type(sqrt(2))
<class 'float'>
>>> type(1.4142135623730951)
<class 'fractions.Fraction'>
>>> [1/i for i in range(1, 10)]
[1, 0.5, 1/3, 0.25, 0.2, 1/6, 1/7, 0.125, 1/9]
```

Compare the above to the default Python REPL:

```
$ python3
Python 3.5.2 (default, Nov 17 2016, 17:05:23) 
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 1 + 1 + 1
3
>>> 0.4 + 0.3 + 0.2 + 0.1
0.9999999999999999
>>> 4/10 + 3/10 + 2/10 + 1/10
0.9999999999999999
>>> (1/3) * (4/7)
0.19047619047619047
>>> 0.123 ** 20
6.282062151752019e-19
>>> (1/3) ** 20
2.867971990792438e-10
```
