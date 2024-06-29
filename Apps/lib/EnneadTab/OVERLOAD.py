"""example on overload handling

import System.Collections.Generic.IEnumerable as IEnumerable


for srf in srfs:
    splitBrep = srf.Split.Overloads[IEnumerable[Rhino.Geometry.Curve], System.Double](cutters, tol)

"""

import os