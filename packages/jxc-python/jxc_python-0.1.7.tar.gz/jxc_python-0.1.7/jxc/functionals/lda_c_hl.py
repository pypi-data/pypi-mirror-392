"""Generated from lda_c_hl.mpl."""

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
  params_hl_c_raw = params.hl_c
  if isinstance(params_hl_c_raw, (str, bytes, dict)):
    params_hl_c = params_hl_c_raw
  else:
    try:
      params_hl_c_seq = list(params_hl_c_raw)
    except TypeError:
      params_hl_c = params_hl_c_raw
    else:
      params_hl_c_seq = np.asarray(params_hl_c_seq, dtype=np.float64)
      params_hl_c = np.concatenate((np.array([np.nan], dtype=np.float64), params_hl_c_seq))
  params_hl_r_raw = params.hl_r
  if isinstance(params_hl_r_raw, (str, bytes, dict)):
    params_hl_r = params_hl_r_raw
  else:
    try:
      params_hl_r_seq = list(params_hl_r_raw)
    except TypeError:
      params_hl_r = params_hl_r_raw
    else:
      params_hl_r_seq = np.asarray(params_hl_r_seq, dtype=np.float64)
      params_hl_r = np.concatenate((np.array([np.nan], dtype=np.float64), params_hl_r_seq))

  hl_xx = lambda k, rs: rs / params_hl_r[k]

  hl_f0 = lambda k, rs: -params_hl_c[k] * ((1 + hl_xx(k, rs) ** 3) * jnp.log(1 + 1 / hl_xx(k, rs)) - hl_xx(k, rs) ** 2 + 1 / 2 * hl_xx(k, rs) - 1 / 3)

  hl_f = lambda rs, zeta: hl_f0(1, rs) + f.f_zeta(zeta) * (hl_f0(2, rs) - hl_f0(1, rs))

  functional_body = lambda rs, zeta: hl_f(rs, zeta)

  res = functional_body(
      f.r_ws(f.dens(r0, r1)),
      f.zeta(r0, r1),
  )
  return res


def unpol(p, r, s=None, l=None, tau=None):
  f = funcs(p)
  params = f.params
  r0, s0, l0, tau0 = r, s, l, tau
  params_hl_c_raw = params.hl_c
  if isinstance(params_hl_c_raw, (str, bytes, dict)):
    params_hl_c = params_hl_c_raw
  else:
    try:
      params_hl_c_seq = list(params_hl_c_raw)
    except TypeError:
      params_hl_c = params_hl_c_raw
    else:
      params_hl_c_seq = np.asarray(params_hl_c_seq, dtype=np.float64)
      params_hl_c = np.concatenate((np.array([np.nan], dtype=np.float64), params_hl_c_seq))
  params_hl_r_raw = params.hl_r
  if isinstance(params_hl_r_raw, (str, bytes, dict)):
    params_hl_r = params_hl_r_raw
  else:
    try:
      params_hl_r_seq = list(params_hl_r_raw)
    except TypeError:
      params_hl_r = params_hl_r_raw
    else:
      params_hl_r_seq = np.asarray(params_hl_r_seq, dtype=np.float64)
      params_hl_r = np.concatenate((np.array([np.nan], dtype=np.float64), params_hl_r_seq))

  hl_xx = lambda k, rs: rs / params_hl_r[k]

  hl_f0 = lambda k, rs: -params_hl_c[k] * ((1 + hl_xx(k, rs) ** 3) * jnp.log(1 + 1 / hl_xx(k, rs)) - hl_xx(k, rs) ** 2 + 1 / 2 * hl_xx(k, rs) - 1 / 3)

  hl_f = lambda rs, zeta: hl_f0(1, rs) + f.f_zeta(zeta) * (hl_f0(2, rs) - hl_f0(1, rs))

  functional_body = lambda rs, zeta: hl_f(rs, zeta)

  res = functional_body(
      f.r_ws(f.dens(r0 / 2, r0 / 2)),
      f.zeta(r0 / 2, r0 / 2),
  )
  return res

def pol_vxc(p, r, s=(None, None, None), l=(None, None), tau=(None, None)):
  f = funcs(p)
  params = f.params
  (r0, r1), (s0, s1, s2), (l0, l1), (tau0, tau1) = r, s, l, tau

  t1 = params.hl_c[0]
  t2 = 0.1e1 / jnp.pi
  t3 = r0 + r1
  t4 = 0.1e1 / t3
  t5 = t2 * t4
  t6 = params.hl_r[0]
  t7 = t6 ** 2
  t9 = 0.1e1 / t7 / t6
  t12 = 0.1e1 + 0.3e1 / 0.4e1 * t5 * t9
  t13 = 3 ** (0.1e1 / 0.3e1)
  t14 = t13 ** 2
  t15 = t2 ** (0.1e1 / 0.3e1)
  t16 = 0.1e1 / t15
  t17 = t14 * t16
  t18 = 4 ** (0.1e1 / 0.3e1)
  t19 = t3 ** (0.1e1 / 0.3e1)
  t20 = t18 * t19
  t24 = 0.1e1 + t17 * t20 * t6 / 0.3e1
  t25 = jnp.log(t24)
  t27 = t15 ** 2
  t28 = t14 * t27
  t29 = t19 ** 2
  t31 = t18 / t29
  t32 = 0.1e1 / t7
  t36 = t13 * t15
  t37 = t18 ** 2
  t39 = t37 / t19
  t40 = 0.1e1 / t6
  t45 = t1 * (t12 * t25 - t28 * t31 * t32 / 0.4e1 + t36 * t39 * t40 / 0.8e1 - 0.1e1 / 0.3e1)
  t46 = r0 - r1
  t47 = t46 * t4
  t48 = 0.1e1 + t47
  t49 = t48 <= f.p.zeta_threshold
  t50 = f.p.zeta_threshold ** (0.1e1 / 0.3e1)
  t51 = t50 * f.p.zeta_threshold
  t52 = t48 ** (0.1e1 / 0.3e1)
  t54 = f.my_piecewise3(t49, t51, t52 * t48)
  t55 = 0.1e1 - t47
  t56 = t55 <= f.p.zeta_threshold
  t57 = t55 ** (0.1e1 / 0.3e1)
  t59 = f.my_piecewise3(t56, t51, t57 * t55)
  t61 = 2 ** (0.1e1 / 0.3e1)
  t64 = 0.1e1 / (0.2e1 * t61 - 0.2e1)
  t65 = (t54 + t59 - 0.2e1) * t64
  t66 = params.hl_c[1]
  t67 = params.hl_r[1]
  t68 = t67 ** 2
  t70 = 0.1e1 / t68 / t67
  t73 = 0.1e1 + 0.3e1 / 0.4e1 * t5 * t70
  t77 = 0.1e1 + t17 * t20 * t67 / 0.3e1
  t78 = jnp.log(t77)
  t80 = 0.1e1 / t68
  t84 = 0.1e1 / t67
  t90 = -t66 * (t73 * t78 - t28 * t31 * t80 / 0.4e1 + t36 * t39 * t84 / 0.8e1 - 0.1e1 / 0.3e1) + t45
  t91 = t65 * t90
  t92 = t3 ** 2
  t93 = 0.1e1 / t92
  t94 = t2 * t93
  t107 = t18 / t29 / t3
  t113 = t37 / t19 / t3
  t118 = t1 * (-0.3e1 / 0.4e1 * t94 * t9 * t25 + t12 * t14 * t16 * t31 * t6 / t24 / 0.9e1 + t28 * t107 * t32 / 0.6e1 - t36 * t113 * t40 / 0.24e2)
  t119 = t46 * t93
  t120 = t4 - t119
  t123 = f.my_piecewise3(t49, 0, 0.4e1 / 0.3e1 * t52 * t120)
  t127 = f.my_piecewise3(t56, 0, -0.4e1 / 0.3e1 * t57 * t120)
  t150 = t65 * (-t66 * (-0.3e1 / 0.4e1 * t94 * t70 * t78 + t73 * t14 * t16 * t31 * t67 / t77 / 0.9e1 + t28 * t107 * t80 / 0.6e1 - t36 * t113 * t84 / 0.24e2) + t118)
  vrho_0_ = -t45 + t91 + t3 * (-t118 + (t123 + t127) * t64 * t90 + t150)
  t153 = -t4 - t119
  t156 = f.my_piecewise3(t49, 0, 0.4e1 / 0.3e1 * t52 * t153)
  t160 = f.my_piecewise3(t56, 0, -0.4e1 / 0.3e1 * t57 * t153)
  vrho_1_ = -t45 + t91 + t3 * (-t118 + (t156 + t160) * t64 * t90 + t150)

  res = {'vrho': jnp.stack([vrho_0_, vrho_1_], axis=-1)}
  return res


def unpol_vxc(p, r, s=None, l=None, tau=None):
  f = funcs(p)
  params = f.params
  r0, s0, l0, tau0 = r, s, l, tau

  t1 = params.hl_c[0]
  t2 = 0.1e1 / jnp.pi
  t4 = t2 / r0
  t5 = params.hl_r[0]
  t6 = t5 ** 2
  t8 = 0.1e1 / t6 / t5
  t11 = 0.1e1 + 0.3e1 / 0.4e1 * t4 * t8
  t12 = 3 ** (0.1e1 / 0.3e1)
  t13 = t12 ** 2
  t14 = t2 ** (0.1e1 / 0.3e1)
  t15 = 0.1e1 / t14
  t16 = t13 * t15
  t17 = 4 ** (0.1e1 / 0.3e1)
  t18 = r0 ** (0.1e1 / 0.3e1)
  t19 = t17 * t18
  t23 = 0.1e1 + t16 * t19 * t5 / 0.3e1
  t24 = jnp.log(t23)
  t26 = t14 ** 2
  t27 = t13 * t26
  t28 = t18 ** 2
  t30 = t17 / t28
  t31 = 0.1e1 / t6
  t35 = t12 * t14
  t36 = t17 ** 2
  t38 = t36 / t18
  t39 = 0.1e1 / t5
  t44 = t1 * (t11 * t24 - t27 * t30 * t31 / 0.4e1 + t35 * t38 * t39 / 0.8e1 - 0.1e1 / 0.3e1)
  t46 = f.p.zeta_threshold ** (0.1e1 / 0.3e1)
  t48 = f.my_piecewise3(0.1e1 <= f.p.zeta_threshold, t46 * f.p.zeta_threshold, 1)
  t51 = 2 ** (0.1e1 / 0.3e1)
  t55 = (0.2e1 * t48 - 0.2e1) / (0.2e1 * t51 - 0.2e1)
  t56 = params.hl_c[1]
  t57 = params.hl_r[1]
  t58 = t57 ** 2
  t60 = 0.1e1 / t58 / t57
  t63 = 0.1e1 + 0.3e1 / 0.4e1 * t4 * t60
  t67 = 0.1e1 + t16 * t19 * t57 / 0.3e1
  t68 = jnp.log(t67)
  t70 = 0.1e1 / t58
  t74 = 0.1e1 / t57
  t82 = r0 ** 2
  t84 = t2 / t82
  t97 = t17 / t28 / r0
  t103 = t36 / t18 / r0
  t108 = t1 * (-0.3e1 / 0.4e1 * t84 * t8 * t24 + t11 * t13 * t15 * t30 * t5 / t23 / 0.9e1 + t27 * t97 * t31 / 0.6e1 - t35 * t103 * t39 / 0.24e2)
  vrho_0_ = -t44 + t55 * (-t56 * (t63 * t68 - t27 * t30 * t70 / 0.4e1 + t35 * t38 * t74 / 0.8e1 - 0.1e1 / 0.3e1) + t44) + r0 * (-t108 + t55 * (-t56 * (-0.3e1 / 0.4e1 * t84 * t60 * t68 + t63 * t13 * t15 * t30 * t57 / t67 / 0.9e1 + t27 * t97 * t70 / 0.6e1 - t35 * t103 * t74 / 0.24e2) + t108))

  res = {'vrho': vrho_0_}
  return res
