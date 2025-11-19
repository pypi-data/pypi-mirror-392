"""Generated from lda_c_gombas.mpl."""

import jax
import jax.lax as lax
import jax.numpy as jnp
import jax.scipy.special as jsp_special
import numpy as np
from jax.numpy import array as array
from jax.numpy import int32 as int32
from jax.numpy import nan as nan
from typing import Callable, Optional
from jxc.functionals.utils import *


def pol(p, r, s=(None, None, None), l=(None, None), tau=(None, None)):
  f = funcs(p)
  params = f.params
  (r0, r1), (s0, s1, s2), (l0, l1), (tau0, tau1) = r, s, l, tau
  a1 = -0.0357

  a2 = 0.0562

  b1 = -0.0311

  b2 = 2.39

  functional_body = lambda rs, zeta=None: a1 / (1 + a2 * rs / f.RS_FACTOR) + b1 * jnp.log((rs / f.RS_FACTOR + b2) / (rs / f.RS_FACTOR))

  res = functional_body(
      f.r_ws(f.dens(r0, r1)),
      f.zeta(r0, r1),
  )
  return res


def unpol(p, r, s=None, l=None, tau=None):
  f = funcs(p)
  params = f.params
  r0, s0, l0, tau0 = r, s, l, tau
  a1 = -0.0357

  a2 = 0.0562

  b1 = -0.0311

  b2 = 2.39

  functional_body = lambda rs, zeta=None: a1 / (1 + a2 * rs / f.RS_FACTOR) + b1 * jnp.log((rs / f.RS_FACTOR + b2) / (rs / f.RS_FACTOR))

  res = functional_body(
      f.r_ws(f.dens(r0 / 2, r0 / 2)),
      f.zeta(r0 / 2, r0 / 2),
  )
  return res

def pol_vxc(p, r, s=(None, None, None), l=(None, None), tau=(None, None)):
  f = funcs(p)
  params = f.params
  (r0, r1), (s0, s1, s2), (l0, l1), (tau0, tau1) = r, s, l, tau

  t1 = r0 + r1
  t2 = t1 ** (0.1e1 / 0.3e1)
  t3 = 0.1e1 / t2
  t5 = 0.1e1 + 0.56200000000000000000000000000000000000000000000000e-1 * t3
  t8 = t3 + 0.239e1
  t10 = jnp.log(t8 * t2)
  t12 = t5 ** 2
  t19 = t2 ** 2
  vrho_0_ = -0.357e-1 / t5 - 0.311e-1 * t10 + t1 * (-0.66877999999999999999999999999999999999999999999999e-3 / t12 / t2 / t1 - 0.311e-1 * (-0.1e1 / t1 / 0.3e1 + t8 / t19 / 0.3e1) / t8 * t3)
  vrho_1_ = vrho_0_

  res = {'vrho': jnp.stack([vrho_0_, vrho_1_], axis=-1)}
  return res


def unpol_vxc(p, r, s=None, l=None, tau=None):
  f = funcs(p)
  params = f.params
  r0, s0, l0, tau0 = r, s, l, tau

  t1 = r0 ** (0.1e1 / 0.3e1)
  t2 = 0.1e1 / t1
  t4 = 0.1e1 + 0.56200000000000000000000000000000000000000000000000e-1 * t2
  t7 = t2 + 0.239e1
  t9 = jnp.log(t7 * t1)
  t11 = t4 ** 2
  t18 = t1 ** 2
  vrho_0_ = -0.357e-1 / t4 - 0.311e-1 * t9 + r0 * (-0.66877999999999999999999999999999999999999999999999e-3 / t11 / t1 / r0 - 0.311e-1 * (-0.1e1 / r0 / 0.3e1 + t7 / t18 / 0.3e1) / t7 * t2)

  res = {'vrho': vrho_0_}
  return res
