"""Generated from hyb_gga_xc_wb97.mpl."""

import jax
import jax.lax as lax
import jax.numpy as jnp
import jax.scipy.special as jsp_special
import scipy.special as sp_special
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
  params_c_ab_raw = params.c_ab
  if isinstance(params_c_ab_raw, (str, bytes, dict)):
    params_c_ab = params_c_ab_raw
  else:
    try:
      params_c_ab_seq = list(params_c_ab_raw)
    except TypeError:
      params_c_ab = params_c_ab_raw
    else:
      params_c_ab_seq = np.asarray(params_c_ab_seq, dtype=np.float64)
      params_c_ab = np.concatenate((np.array([np.nan], dtype=np.float64), params_c_ab_seq))
  params_c_ss_raw = params.c_ss
  if isinstance(params_c_ss_raw, (str, bytes, dict)):
    params_c_ss = params_c_ss_raw
  else:
    try:
      params_c_ss_seq = list(params_c_ss_raw)
    except TypeError:
      params_c_ss = params_c_ss_raw
    else:
      params_c_ss_seq = np.asarray(params_c_ss_seq, dtype=np.float64)
      params_c_ss = np.concatenate((np.array([np.nan], dtype=np.float64), params_c_ss_seq))
  params_c_x_raw = params.c_x
  if isinstance(params_c_x_raw, (str, bytes, dict)):
    params_c_x = params_c_x_raw
  else:
    try:
      params_c_x_seq = list(params_c_x_raw)
    except TypeError:
      params_c_x = params_c_x_raw
    else:
      params_c_x_seq = np.asarray(params_c_x_seq, dtype=np.float64)
      params_c_x = np.concatenate((np.array([np.nan], dtype=np.float64), params_c_x_seq))

  params_pp = np.array([np.nan, 1, 1, 1], dtype=np.float64)

  params_a = np.array([np.nan, 0.031091, 0.015545, 0.016887], dtype=np.float64)

  params_alpha1 = np.array([np.nan, 0.2137, 0.20548, 0.11125], dtype=np.float64)

  params_beta1 = np.array([np.nan, 7.5957, 14.1189, 10.357], dtype=np.float64)

  params_beta2 = np.array([np.nan, 3.5876, 6.1977, 3.6231], dtype=np.float64)

  params_beta3 = np.array([np.nan, 1.6382, 3.3662, 0.88026], dtype=np.float64)

  params_beta4 = np.array([np.nan, 0.49294, 0.62517, 0.49671], dtype=np.float64)

  params_fz20 = 1.709921

  att_erf_aux1 = lambda a: jnp.sqrt(jnp.pi) * jax.lax.erf(1 / (2 * a))

  att_erf_aux2 = lambda a: jnp.exp(-1 / (4 * a ** 2)) - 1

  a_cnst = (4 / (9 * jnp.pi)) ** (1 / 3) * f.p.cam_omega / 2

  lda_x_ax = -f.RS_FACTOR * X_FACTOR_C / 2 ** (4 / 3)

  b97_g = lambda gamma, cc, x: jnp.sum(jnp.array([cc[i] * (gamma * x ** 2 / (1 + gamma * x ** 2)) ** (i - 1) for i in range(1, 5 + 1)]), axis=0)

  g_aux = lambda k, rs: params_beta1[k] * jnp.sqrt(rs) + params_beta2[k] * rs + params_beta3[k] * rs ** 1.5 + params_beta4[k] * rs ** (params_pp[k] + 1)

  att_erf_aux3 = lambda a: 2 * a ** 2 * att_erf_aux2(a) + 1 / 2

  b97_fpar = lambda lda_func, mgamma, cc, rs, z, xs0, xs1: +lda_stoll_par(f, params, lda_func, rs, z) * b97_g(mgamma, cc, xs0) + lda_stoll_par(f, params, lda_func, rs, -z) * b97_g(mgamma, cc, xs1)

  b97_fperp = lambda lda_func, mgamma, cc, rs, z, xs0, xs1: lda_stoll_perp(f, params, lda_func, rs, z) * b97_g(mgamma, cc, jnp.sqrt(xs0 ** 2 + xs1 ** 2) / jnp.sqrt(2))

  g = lambda k, rs: -2 * params_a[k] * (1 + params_alpha1[k] * rs) * jnp.log(1 + 1 / (2 * params_a[k] * g_aux(k, rs)))

  attenuation_erf0 = lambda a: 1 - 8 / 3 * a * (att_erf_aux1(a) + 2 * a * (att_erf_aux2(a) - att_erf_aux3(a)))

  b97_f = lambda lda_func, gamma_ss, cc_ss, gamma_ab, cc_ab, rs, z, xs0, xs1: +b97_fpar(lda_func, gamma_ss, cc_ss, rs, z, xs0, xs1) + b97_fperp(lda_func, gamma_ab, cc_ab, rs, z, xs0, xs1)

  f_pw = lambda rs, zeta: g(1, rs) + zeta ** 4 * f.f_zeta(zeta) * (g(2, rs) - g(1, rs) + g(3, rs) / params_fz20) - f.f_zeta(zeta) * g(3, rs) / params_fz20

  attenuation_erf = lambda a: apply_piecewise(a, lambda _aval: _aval >= 1.35, lambda _aval: -1 / 2021444812800 * (1.0 / jnp.maximum(_aval, 1.35)) ** 16 + 1 / 44590694400 * (1.0 / jnp.maximum(_aval, 1.35)) ** 14 - 1 / 1073479680 * (1.0 / jnp.maximum(_aval, 1.35)) ** 12 + 1 / 28385280 * (1.0 / jnp.maximum(_aval, 1.35)) ** 10 - 1 / 829440 * (1.0 / jnp.maximum(_aval, 1.35)) ** 8 + 1 / 26880 * (1.0 / jnp.maximum(_aval, 1.35)) ** 6 - 1 / 960 * (1.0 / jnp.maximum(_aval, 1.35)) ** 4 + 1 / 36 * (1.0 / jnp.maximum(_aval, 1.35)) ** 2, lambda _aval: attenuation_erf0(jnp.minimum(_aval, 1.35)))

  lda_x_erf_spin = lambda rs, z: lda_x_ax * f.opz_pow_n(z, 4 / 3) / rs * attenuation_erf(a_cnst * rs / f.opz_pow_n(z, 1 / 3))

  wb97_x = lambda rs, z, xs0, xs1: f.my_piecewise3(f.screen_dens_zeta(rs, z), 0, (1 + z) / 2 * lda_x_erf_spin(rs * (2 / (1 + z)) ** (1 / 3), 1) * b97_g(0.004, params_c_x, xs0)) + f.my_piecewise3(f.screen_dens_zeta(rs, -z), 0, (1 - z) / 2 * lda_x_erf_spin(rs * (2 / (1 - z)) ** (1 / 3), 1) * b97_g(0.004, params_c_x, xs1))

  functional_body = lambda rs, z, xt, xs0, xs1: wb97_x(rs, z, xs0, xs1) + b97_f(f_pw, 0.2, params_c_ss, 0.006, params_c_ab, rs, z, xs0, xs1)

  res = functional_body(
      f.r_ws(f.dens(r0, r1)),
      f.zeta(r0, r1),
      f.xt(r0, r1, s0, s1, s2),
      f.xs0(r0, r1, s0, s2),
      f.xs1(r0, r1, s0, s2),
  )
  return res

def unpol(p, r, s=None, l=None, tau=None):
  f = funcs(p)
  params = f.params
  r0, s0, l0, tau0 = r, s, l, tau
  params_c_ab_raw = params.c_ab
  if isinstance(params_c_ab_raw, (str, bytes, dict)):
    params_c_ab = params_c_ab_raw
  else:
    try:
      params_c_ab_seq = list(params_c_ab_raw)
    except TypeError:
      params_c_ab = params_c_ab_raw
    else:
      params_c_ab_seq = np.asarray(params_c_ab_seq, dtype=np.float64)
      params_c_ab = np.concatenate((np.array([np.nan], dtype=np.float64), params_c_ab_seq))
  params_c_ss_raw = params.c_ss
  if isinstance(params_c_ss_raw, (str, bytes, dict)):
    params_c_ss = params_c_ss_raw
  else:
    try:
      params_c_ss_seq = list(params_c_ss_raw)
    except TypeError:
      params_c_ss = params_c_ss_raw
    else:
      params_c_ss_seq = np.asarray(params_c_ss_seq, dtype=np.float64)
      params_c_ss = np.concatenate((np.array([np.nan], dtype=np.float64), params_c_ss_seq))
  params_c_x_raw = params.c_x
  if isinstance(params_c_x_raw, (str, bytes, dict)):
    params_c_x = params_c_x_raw
  else:
    try:
      params_c_x_seq = list(params_c_x_raw)
    except TypeError:
      params_c_x = params_c_x_raw
    else:
      params_c_x_seq = np.asarray(params_c_x_seq, dtype=np.float64)
      params_c_x = np.concatenate((np.array([np.nan], dtype=np.float64), params_c_x_seq))

  params_pp = np.array([np.nan, 1, 1, 1], dtype=np.float64)

  params_a = np.array([np.nan, 0.031091, 0.015545, 0.016887], dtype=np.float64)

  params_alpha1 = np.array([np.nan, 0.2137, 0.20548, 0.11125], dtype=np.float64)

  params_beta1 = np.array([np.nan, 7.5957, 14.1189, 10.357], dtype=np.float64)

  params_beta2 = np.array([np.nan, 3.5876, 6.1977, 3.6231], dtype=np.float64)

  params_beta3 = np.array([np.nan, 1.6382, 3.3662, 0.88026], dtype=np.float64)

  params_beta4 = np.array([np.nan, 0.49294, 0.62517, 0.49671], dtype=np.float64)

  params_fz20 = 1.709921

  att_erf_aux1 = lambda a: jnp.sqrt(jnp.pi) * jax.lax.erf(1 / (2 * a))

  att_erf_aux2 = lambda a: jnp.exp(-1 / (4 * a ** 2)) - 1

  a_cnst = (4 / (9 * jnp.pi)) ** (1 / 3) * f.p.cam_omega / 2

  lda_x_ax = -f.RS_FACTOR * X_FACTOR_C / 2 ** (4 / 3)

  b97_g = lambda gamma, cc, x: jnp.sum(jnp.array([cc[i] * (gamma * x ** 2 / (1 + gamma * x ** 2)) ** (i - 1) for i in range(1, 5 + 1)]), axis=0)

  g_aux = lambda k, rs: params_beta1[k] * jnp.sqrt(rs) + params_beta2[k] * rs + params_beta3[k] * rs ** 1.5 + params_beta4[k] * rs ** (params_pp[k] + 1)

  att_erf_aux3 = lambda a: 2 * a ** 2 * att_erf_aux2(a) + 1 / 2

  b97_fpar = lambda lda_func, mgamma, cc, rs, z, xs0, xs1: +lda_stoll_par(f, params, lda_func, rs, z) * b97_g(mgamma, cc, xs0) + lda_stoll_par(f, params, lda_func, rs, -z) * b97_g(mgamma, cc, xs1)

  b97_fperp = lambda lda_func, mgamma, cc, rs, z, xs0, xs1: lda_stoll_perp(f, params, lda_func, rs, z) * b97_g(mgamma, cc, jnp.sqrt(xs0 ** 2 + xs1 ** 2) / jnp.sqrt(2))

  g = lambda k, rs: -2 * params_a[k] * (1 + params_alpha1[k] * rs) * jnp.log(1 + 1 / (2 * params_a[k] * g_aux(k, rs)))

  attenuation_erf0 = lambda a: 1 - 8 / 3 * a * (att_erf_aux1(a) + 2 * a * (att_erf_aux2(a) - att_erf_aux3(a)))

  b97_f = lambda lda_func, gamma_ss, cc_ss, gamma_ab, cc_ab, rs, z, xs0, xs1: +b97_fpar(lda_func, gamma_ss, cc_ss, rs, z, xs0, xs1) + b97_fperp(lda_func, gamma_ab, cc_ab, rs, z, xs0, xs1)

  f_pw = lambda rs, zeta: g(1, rs) + zeta ** 4 * f.f_zeta(zeta) * (g(2, rs) - g(1, rs) + g(3, rs) / params_fz20) - f.f_zeta(zeta) * g(3, rs) / params_fz20

  attenuation_erf = lambda a: apply_piecewise(a, lambda _aval: _aval >= 1.35, lambda _aval: -1 / 2021444812800 * (1.0 / jnp.maximum(_aval, 1.35)) ** 16 + 1 / 44590694400 * (1.0 / jnp.maximum(_aval, 1.35)) ** 14 - 1 / 1073479680 * (1.0 / jnp.maximum(_aval, 1.35)) ** 12 + 1 / 28385280 * (1.0 / jnp.maximum(_aval, 1.35)) ** 10 - 1 / 829440 * (1.0 / jnp.maximum(_aval, 1.35)) ** 8 + 1 / 26880 * (1.0 / jnp.maximum(_aval, 1.35)) ** 6 - 1 / 960 * (1.0 / jnp.maximum(_aval, 1.35)) ** 4 + 1 / 36 * (1.0 / jnp.maximum(_aval, 1.35)) ** 2, lambda _aval: attenuation_erf0(jnp.minimum(_aval, 1.35)))

  lda_x_erf_spin = lambda rs, z: lda_x_ax * f.opz_pow_n(z, 4 / 3) / rs * attenuation_erf(a_cnst * rs / f.opz_pow_n(z, 1 / 3))

  wb97_x = lambda rs, z, xs0, xs1: f.my_piecewise3(f.screen_dens_zeta(rs, z), 0, (1 + z) / 2 * lda_x_erf_spin(rs * (2 / (1 + z)) ** (1 / 3), 1) * b97_g(0.004, params_c_x, xs0)) + f.my_piecewise3(f.screen_dens_zeta(rs, -z), 0, (1 - z) / 2 * lda_x_erf_spin(rs * (2 / (1 - z)) ** (1 / 3), 1) * b97_g(0.004, params_c_x, xs1))

  functional_body = lambda rs, z, xt, xs0, xs1: wb97_x(rs, z, xs0, xs1) + b97_f(f_pw, 0.2, params_c_ss, 0.006, params_c_ab, rs, z, xs0, xs1)

  res = functional_body(
      f.r_ws(f.dens(r0 / 2, r0 / 2)),
      f.zeta(r0 / 2, r0 / 2),
      f.xt(r0 / 2, r0 / 2, s0 / 4, s0 / 4, s0 / 4),
      f.xs0(r0 / 2, r0 / 2, s0 / 4, s0 / 4),
      f.xs1(r0 / 2, r0 / 2, s0 / 4, s0 / 4),
  )
  return res

def pol_vxc(p, r, s=(None, None, None), l=(None, None), tau=(None, None)):
  f = funcs(p)
  params = f.params
  (r0, r1), (s0, s1, s2), (l0, l1), (tau0, tau1) = r, s, l, tau
  params_c_ab_raw = params.c_ab
  if isinstance(params_c_ab_raw, (str, bytes, dict)):
    params_c_ab = params_c_ab_raw
  else:
    try:
      params_c_ab_seq = list(params_c_ab_raw)
    except TypeError:
      params_c_ab = params_c_ab_raw
    else:
      params_c_ab_seq = np.asarray(params_c_ab_seq, dtype=np.float64)
      params_c_ab = np.concatenate((np.array([np.nan], dtype=np.float64), params_c_ab_seq))
  params_c_ss_raw = params.c_ss
  if isinstance(params_c_ss_raw, (str, bytes, dict)):
    params_c_ss = params_c_ss_raw
  else:
    try:
      params_c_ss_seq = list(params_c_ss_raw)
    except TypeError:
      params_c_ss = params_c_ss_raw
    else:
      params_c_ss_seq = np.asarray(params_c_ss_seq, dtype=np.float64)
      params_c_ss = np.concatenate((np.array([np.nan], dtype=np.float64), params_c_ss_seq))
  params_c_x_raw = params.c_x
  if isinstance(params_c_x_raw, (str, bytes, dict)):
    params_c_x = params_c_x_raw
  else:
    try:
      params_c_x_seq = list(params_c_x_raw)
    except TypeError:
      params_c_x = params_c_x_raw
    else:
      params_c_x_seq = np.asarray(params_c_x_seq, dtype=np.float64)
      params_c_x = np.concatenate((np.array([np.nan], dtype=np.float64), params_c_x_seq))

  params_pp = np.array([np.nan, 1, 1, 1], dtype=np.float64)

  params_a = np.array([np.nan, 0.031091, 0.015545, 0.016887], dtype=np.float64)

  params_alpha1 = np.array([np.nan, 0.2137, 0.20548, 0.11125], dtype=np.float64)

  params_beta1 = np.array([np.nan, 7.5957, 14.1189, 10.357], dtype=np.float64)

  params_beta2 = np.array([np.nan, 3.5876, 6.1977, 3.6231], dtype=np.float64)

  params_beta3 = np.array([np.nan, 1.6382, 3.3662, 0.88026], dtype=np.float64)

  params_beta4 = np.array([np.nan, 0.49294, 0.62517, 0.49671], dtype=np.float64)

  params_fz20 = 1.709921

  att_erf_aux1 = lambda a: jnp.sqrt(jnp.pi) * jax.lax.erf(1 / (2 * a))

  att_erf_aux2 = lambda a: jnp.exp(-1 / (4 * a ** 2)) - 1

  a_cnst = (4 / (9 * jnp.pi)) ** (1 / 3) * f.p.cam_omega / 2

  lda_x_ax = -f.RS_FACTOR * X_FACTOR_C / 2 ** (4 / 3)

  b97_g = lambda gamma, cc, x: jnp.sum(jnp.array([cc[i] * (gamma * x ** 2 / (1 + gamma * x ** 2)) ** (i - 1) for i in range(1, 5 + 1)]), axis=0)

  g_aux = lambda k, rs: params_beta1[k] * jnp.sqrt(rs) + params_beta2[k] * rs + params_beta3[k] * rs ** 1.5 + params_beta4[k] * rs ** (params_pp[k] + 1)

  att_erf_aux3 = lambda a: 2 * a ** 2 * att_erf_aux2(a) + 1 / 2

  b97_fpar = lambda lda_func, mgamma, cc, rs, z, xs0, xs1: +lda_stoll_par(f, params, lda_func, rs, z) * b97_g(mgamma, cc, xs0) + lda_stoll_par(f, params, lda_func, rs, -z) * b97_g(mgamma, cc, xs1)

  b97_fperp = lambda lda_func, mgamma, cc, rs, z, xs0, xs1: lda_stoll_perp(f, params, lda_func, rs, z) * b97_g(mgamma, cc, jnp.sqrt(xs0 ** 2 + xs1 ** 2) / jnp.sqrt(2))

  g = lambda k, rs: -2 * params_a[k] * (1 + params_alpha1[k] * rs) * jnp.log(1 + 1 / (2 * params_a[k] * g_aux(k, rs)))

  attenuation_erf0 = lambda a: 1 - 8 / 3 * a * (att_erf_aux1(a) + 2 * a * (att_erf_aux2(a) - att_erf_aux3(a)))

  b97_f = lambda lda_func, gamma_ss, cc_ss, gamma_ab, cc_ab, rs, z, xs0, xs1: +b97_fpar(lda_func, gamma_ss, cc_ss, rs, z, xs0, xs1) + b97_fperp(lda_func, gamma_ab, cc_ab, rs, z, xs0, xs1)

  f_pw = lambda rs, zeta: g(1, rs) + zeta ** 4 * f.f_zeta(zeta) * (g(2, rs) - g(1, rs) + g(3, rs) / params_fz20) - f.f_zeta(zeta) * g(3, rs) / params_fz20

  attenuation_erf = lambda a: apply_piecewise(a, lambda _aval: _aval >= 1.35, lambda _aval: -1 / 2021444812800 * (1.0 / jnp.maximum(_aval, 1.35)) ** 16 + 1 / 44590694400 * (1.0 / jnp.maximum(_aval, 1.35)) ** 14 - 1 / 1073479680 * (1.0 / jnp.maximum(_aval, 1.35)) ** 12 + 1 / 28385280 * (1.0 / jnp.maximum(_aval, 1.35)) ** 10 - 1 / 829440 * (1.0 / jnp.maximum(_aval, 1.35)) ** 8 + 1 / 26880 * (1.0 / jnp.maximum(_aval, 1.35)) ** 6 - 1 / 960 * (1.0 / jnp.maximum(_aval, 1.35)) ** 4 + 1 / 36 * (1.0 / jnp.maximum(_aval, 1.35)) ** 2, lambda _aval: attenuation_erf0(jnp.minimum(_aval, 1.35)))

  lda_x_erf_spin = lambda rs, z: lda_x_ax * f.opz_pow_n(z, 4 / 3) / rs * attenuation_erf(a_cnst * rs / f.opz_pow_n(z, 1 / 3))

  wb97_x = lambda rs, z, xs0, xs1: f.my_piecewise3(f.screen_dens_zeta(rs, z), 0, (1 + z) / 2 * lda_x_erf_spin(rs * (2 / (1 + z)) ** (1 / 3), 1) * b97_g(0.004, params_c_x, xs0)) + f.my_piecewise3(f.screen_dens_zeta(rs, -z), 0, (1 - z) / 2 * lda_x_erf_spin(rs * (2 / (1 - z)) ** (1 / 3), 1) * b97_g(0.004, params_c_x, xs1))

  functional_body = lambda rs, z, xt, xs0, xs1: wb97_x(rs, z, xs0, xs1) + b97_f(f_pw, 0.2, params_c_ss, 0.006, params_c_ab, rs, z, xs0, xs1)

  t2 = r0 - r1
  t3 = r0 + r1
  t4 = 0.1e1 / t3
  t5 = t2 * t4
  t6 = 0.1e1 + t5
  t7 = t6 <= f.p.zeta_threshold
  t8 = r0 <= f.p.dens_threshold or t7
  t10 = 3 ** (0.1e1 / 0.3e1)
  t11 = t6 * t10 / 0.2e1
  t13 = (0.1e1 / jnp.pi) ** (0.1e1 / 0.3e1)
  t14 = 4 ** (0.1e1 / 0.3e1)
  t15 = t14 ** 2
  t16 = t13 * t15
  t17 = 2 ** (0.1e1 / 0.3e1)
  t18 = t16 * t17
  t19 = t11 * t18
  t20 = 0.2e1 <= f.p.zeta_threshold
  t21 = f.p.zeta_threshold ** (0.1e1 / 0.3e1)
  t22 = t21 * f.p.zeta_threshold
  t24 = f.my_piecewise3(t20, t22, 0.2e1 * t17)
  t25 = t3 ** (0.1e1 / 0.3e1)
  t26 = t24 * t25
  t27 = 0.1e1 / t6
  t28 = t27 ** (0.1e1 / 0.3e1)
  t29 = 0.1e1 / t28
  t30 = 9 ** (0.1e1 / 0.3e1)
  t31 = t30 ** 2
  t32 = t13 ** 2
  t33 = t31 * t32
  t34 = f.p.cam_omega * t10
  t35 = t33 * t34
  t36 = 0.1e1 / t25
  t37 = t36 * t17
  t38 = f.my_piecewise3(t20, t21, t17)
  t39 = 0.1e1 / t38
  t40 = t28 * t39
  t43 = t35 * t37 * t40 / 0.18e2
  t44 = 0.135e1 <= t43
  t45 = 0.135e1 < t43
  t46 = f.my_piecewise3(t45, t43, 0.135e1)
  t47 = t46 ** 2
  t50 = t47 ** 2
  t53 = t50 * t47
  t56 = t50 ** 2
  t68 = t56 ** 2
  t72 = f.my_piecewise3(t45, 0.135e1, t43)
  t73 = jnp.sqrt(jnp.pi)
  t74 = 0.1e1 / t72
  t76 = jax.lax.erf(t74 / 0.2e1)
  t78 = t72 ** 2
  t79 = 0.1e1 / t78
  t81 = jnp.exp(-t79 / 0.4e1)
  t82 = t81 - 0.1e1
  t85 = t81 - 0.3e1 / 0.2e1 - 0.2e1 * t78 * t82
  t88 = 0.2e1 * t72 * t85 + t73 * t76
  t92 = f.my_piecewise3(t44, 0.1e1 / t47 / 0.36e2 - 0.1e1 / t50 / 0.960e3 + 0.1e1 / t53 / 0.26880e5 - 0.1e1 / t56 / 0.829440e6 + 0.1e1 / t56 / t47 / 0.28385280e8 - 0.1e1 / t56 / t50 / 0.1073479680e10 + 0.1e1 / t56 / t53 / 0.44590694400e11 - 0.1e1 / t68 / 0.2021444812800e13, 0.1e1 - 0.8e1 / 0.3e1 * t72 * t88)
  t93 = t29 * t92
  t94 = params.c_x[0]
  t95 = params.c_x[1]
  t96 = t95 * s0
  t97 = r0 ** 2
  t98 = r0 ** (0.1e1 / 0.3e1)
  t99 = t98 ** 2
  t101 = 0.1e1 / t99 / t97
  t102 = s0 * t101
  t104 = 0.1e1 + 0.4e-2 * t102
  t105 = 0.1e1 / t104
  t109 = params.c_x[2]
  t110 = s0 ** 2
  t111 = t109 * t110
  t112 = t97 ** 2
  t113 = t112 * r0
  t115 = 0.1e1 / t98 / t113
  t116 = t104 ** 2
  t117 = 0.1e1 / t116
  t118 = t115 * t117
  t121 = params.c_x[3]
  t122 = t110 * s0
  t123 = t121 * t122
  t124 = t112 ** 2
  t125 = 0.1e1 / t124
  t127 = 0.1e1 / t116 / t104
  t128 = t125 * t127
  t131 = params.c_x[4]
  t132 = t110 ** 2
  t133 = t131 * t132
  t136 = 0.1e1 / t99 / t124 / t97
  t137 = t116 ** 2
  t138 = 0.1e1 / t137
  t139 = t136 * t138
  t142 = t94 + 0.4e-2 * t96 * t101 * t105 + 0.16e-4 * t111 * t118 + 0.64e-7 * t123 * t128 + 0.256e-9 * t133 * t139
  t143 = t93 * t142
  t144 = t26 * t143
  t147 = f.my_piecewise3(t8, 0, -0.3e1 / 0.32e2 * t19 * t144)
  t149 = 0.1e1 - t5
  t150 = t149 <= f.p.zeta_threshold
  t151 = r1 <= f.p.dens_threshold or t150
  t153 = t149 * t10 / 0.2e1
  t154 = t153 * t18
  t155 = 0.1e1 / t149
  t156 = t155 ** (0.1e1 / 0.3e1)
  t157 = 0.1e1 / t156
  t158 = t156 * t39
  t161 = t35 * t37 * t158 / 0.18e2
  t162 = 0.135e1 <= t161
  t163 = 0.135e1 < t161
  t164 = f.my_piecewise3(t163, t161, 0.135e1)
  t165 = t164 ** 2
  t168 = t165 ** 2
  t171 = t168 * t165
  t174 = t168 ** 2
  t186 = t174 ** 2
  t190 = f.my_piecewise3(t163, 0.135e1, t161)
  t191 = 0.1e1 / t190
  t193 = jax.lax.erf(t191 / 0.2e1)
  t195 = t190 ** 2
  t196 = 0.1e1 / t195
  t198 = jnp.exp(-t196 / 0.4e1)
  t199 = t198 - 0.1e1
  t202 = t198 - 0.3e1 / 0.2e1 - 0.2e1 * t195 * t199
  t205 = 0.2e1 * t190 * t202 + t73 * t193
  t209 = f.my_piecewise3(t162, 0.1e1 / t165 / 0.36e2 - 0.1e1 / t168 / 0.960e3 + 0.1e1 / t171 / 0.26880e5 - 0.1e1 / t174 / 0.829440e6 + 0.1e1 / t174 / t165 / 0.28385280e8 - 0.1e1 / t174 / t168 / 0.1073479680e10 + 0.1e1 / t174 / t171 / 0.44590694400e11 - 0.1e1 / t186 / 0.2021444812800e13, 0.1e1 - 0.8e1 / 0.3e1 * t190 * t205)
  t210 = t157 * t209
  t211 = t95 * s2
  t212 = r1 ** 2
  t213 = r1 ** (0.1e1 / 0.3e1)
  t214 = t213 ** 2
  t216 = 0.1e1 / t214 / t212
  t217 = s2 * t216
  t219 = 0.1e1 + 0.4e-2 * t217
  t220 = 0.1e1 / t219
  t224 = s2 ** 2
  t225 = t109 * t224
  t226 = t212 ** 2
  t227 = t226 * r1
  t229 = 0.1e1 / t213 / t227
  t230 = t219 ** 2
  t231 = 0.1e1 / t230
  t232 = t229 * t231
  t235 = t224 * s2
  t236 = t121 * t235
  t237 = t226 ** 2
  t238 = 0.1e1 / t237
  t240 = 0.1e1 / t230 / t219
  t241 = t238 * t240
  t244 = t224 ** 2
  t245 = t131 * t244
  t248 = 0.1e1 / t214 / t237 / t212
  t249 = t230 ** 2
  t250 = 0.1e1 / t249
  t251 = t248 * t250
  t254 = t94 + 0.4e-2 * t211 * t216 * t220 + 0.16e-4 * t225 * t232 + 0.64e-7 * t236 * t241 + 0.256e-9 * t245 * t251
  t255 = t210 * t254
  t256 = t26 * t255
  t259 = f.my_piecewise3(t151, 0, -0.3e1 / 0.32e2 * t154 * t256)
  t260 = f.my_piecewise3(t7, f.p.zeta_threshold, t6)
  t261 = t10 * t13
  t262 = t261 * t15
  t263 = 0.1e1 / t21
  t264 = t6 ** (0.1e1 / 0.3e1)
  t266 = f.my_piecewise3(t7, t263, 0.1e1 / t264)
  t268 = t262 * t37 * t266
  t270 = 0.62182e-1 + 0.33220733500000000000000000000000000000000000000000e-2 * t268
  t271 = jnp.sqrt(t268)
  t274 = t268 ** 0.15e1
  t276 = t10 ** 2
  t277 = t276 * t32
  t278 = t277 * t14
  t279 = t25 ** 2
  t280 = 0.1e1 / t279
  t281 = t17 ** 2
  t282 = t280 * t281
  t283 = t266 ** 2
  t285 = t278 * t282 * t283
  t287 = 0.23615790870000000000000000000000000000000000000000e0 * t271 + 0.55771035800000000000000000000000000000000000000000e-1 * t268 + 0.12733319050000000000000000000000000000000000000000e-1 * t274 + 0.76629987700000000000000000000000000000000000000000e-2 * t285
  t289 = 0.1e1 + 0.1e1 / t287
  t290 = jnp.log(t289)
  t291 = t270 * t290
  t293 = f.my_piecewise3(0.0e0 <= f.p.zeta_threshold, t22, 0)
  t297 = 0.1e1 / (0.2e1 * t17 - 0.2e1)
  t298 = (t24 + t293 - 0.2e1) * t297
  t300 = 0.31090e-1 + 0.15970933000000000000000000000000000000000000000000e-2 * t268
  t305 = 0.21947830050000000000000000000000000000000000000000e0 * t271 + 0.48171623250000000000000000000000000000000000000000e-1 * t268 + 0.13081894750000000000000000000000000000000000000000e-1 * t274 + 0.48591338250000000000000000000000000000000000000000e-2 * t285
  t307 = 0.1e1 + 0.1e1 / t305
  t308 = jnp.log(t307)
  t311 = 0.33774e-1 + 0.93933937500000000000000000000000000000000000000000e-3 * t268
  t316 = 0.17489865900000000000000000000000000000000000000000e0 * t271 + 0.30591644850000000000000000000000000000000000000000e-1 * t268 + 0.37162376550000000000000000000000000000000000000000e-2 * t274 + 0.41939708850000000000000000000000000000000000000000e-2 * t285
  t318 = 0.1e1 + 0.1e1 / t316
  t319 = jnp.log(t318)
  t320 = t311 * t319
  t326 = -t291 + t298 * (-t300 * t308 + t291 - 0.58482233974552040708313425006184496242808878304904e0 * t320) + 0.58482233974552040708313425006184496242808878304904e0 * t298 * t320
  t329 = f.my_piecewise3(t8, 0, t260 * t326 / 0.2e1)
  t330 = params.c_ss[0]
  t331 = params.c_ss[1]
  t332 = t331 * s0
  t334 = 0.1e1 + 0.2e0 * t102
  t335 = 0.1e1 / t334
  t339 = params.c_ss[2]
  t340 = t339 * t110
  t341 = t334 ** 2
  t342 = 0.1e1 / t341
  t343 = t115 * t342
  t346 = params.c_ss[3]
  t347 = t346 * t122
  t349 = 0.1e1 / t341 / t334
  t350 = t125 * t349
  t353 = params.c_ss[4]
  t354 = t353 * t132
  t355 = t341 ** 2
  t356 = 0.1e1 / t355
  t357 = t136 * t356
  t360 = t330 + 0.2e0 * t332 * t101 * t335 + 0.4e-1 * t340 * t343 + 0.8e-2 * t347 * t350 + 0.16e-2 * t354 * t357
  t361 = t329 * t360
  t362 = f.my_piecewise3(t150, f.p.zeta_threshold, t149)
  t363 = t149 ** (0.1e1 / 0.3e1)
  t365 = f.my_piecewise3(t150, t263, 0.1e1 / t363)
  t367 = t262 * t37 * t365
  t369 = 0.62182e-1 + 0.33220733500000000000000000000000000000000000000000e-2 * t367
  t370 = jnp.sqrt(t367)
  t373 = t367 ** 0.15e1
  t375 = t365 ** 2
  t377 = t278 * t282 * t375
  t379 = 0.23615790870000000000000000000000000000000000000000e0 * t370 + 0.55771035800000000000000000000000000000000000000000e-1 * t367 + 0.12733319050000000000000000000000000000000000000000e-1 * t373 + 0.76629987700000000000000000000000000000000000000000e-2 * t377
  t381 = 0.1e1 + 0.1e1 / t379
  t382 = jnp.log(t381)
  t383 = t369 * t382
  t385 = 0.31090e-1 + 0.15970933000000000000000000000000000000000000000000e-2 * t367
  t390 = 0.21947830050000000000000000000000000000000000000000e0 * t370 + 0.48171623250000000000000000000000000000000000000000e-1 * t367 + 0.13081894750000000000000000000000000000000000000000e-1 * t373 + 0.48591338250000000000000000000000000000000000000000e-2 * t377
  t392 = 0.1e1 + 0.1e1 / t390
  t393 = jnp.log(t392)
  t396 = 0.33774e-1 + 0.93933937500000000000000000000000000000000000000000e-3 * t367
  t401 = 0.17489865900000000000000000000000000000000000000000e0 * t370 + 0.30591644850000000000000000000000000000000000000000e-1 * t367 + 0.37162376550000000000000000000000000000000000000000e-2 * t373 + 0.41939708850000000000000000000000000000000000000000e-2 * t377
  t403 = 0.1e1 + 0.1e1 / t401
  t404 = jnp.log(t403)
  t405 = t396 * t404
  t411 = -t383 + t298 * (-t385 * t393 + t383 - 0.58482233974552040708313425006184496242808878304904e0 * t405) + 0.58482233974552040708313425006184496242808878304904e0 * t298 * t405
  t414 = f.my_piecewise3(t151, 0, t362 * t411 / 0.2e1)
  t415 = t331 * s2
  t417 = 0.1e1 + 0.2e0 * t217
  t418 = 0.1e1 / t417
  t422 = t339 * t224
  t423 = t417 ** 2
  t424 = 0.1e1 / t423
  t425 = t229 * t424
  t428 = t346 * t235
  t430 = 0.1e1 / t423 / t417
  t431 = t238 * t430
  t434 = t353 * t244
  t435 = t423 ** 2
  t436 = 0.1e1 / t435
  t437 = t248 * t436
  t440 = t330 + 0.2e0 * t415 * t216 * t418 + 0.4e-1 * t422 * t425 + 0.8e-2 * t428 * t431 + 0.16e-2 * t434 * t437
  t441 = t414 * t440
  t443 = t261 * t15 * t36
  t445 = 0.62182e-1 + 0.33220733500000000000000000000000000000000000000000e-2 * t443
  t446 = jnp.sqrt(t443)
  t449 = t443 ** 0.15e1
  t452 = t277 * t14 * t280
  t454 = 0.23615790870000000000000000000000000000000000000000e0 * t446 + 0.55771035800000000000000000000000000000000000000000e-1 * t443 + 0.12733319050000000000000000000000000000000000000000e-1 * t449 + 0.76629987700000000000000000000000000000000000000000e-2 * t452
  t456 = 0.1e1 + 0.1e1 / t454
  t457 = jnp.log(t456)
  t458 = t445 * t457
  t459 = t2 ** 2
  t460 = t459 ** 2
  t461 = t3 ** 2
  t462 = t461 ** 2
  t463 = 0.1e1 / t462
  t464 = t460 * t463
  t465 = t264 * t6
  t466 = f.my_piecewise3(t7, t22, t465)
  t467 = t363 * t149
  t468 = f.my_piecewise3(t150, t22, t467)
  t470 = (t466 + t468 - 0.2e1) * t297
  t472 = 0.31090e-1 + 0.15970933000000000000000000000000000000000000000000e-2 * t443
  t477 = 0.21947830050000000000000000000000000000000000000000e0 * t446 + 0.48171623250000000000000000000000000000000000000000e-1 * t443 + 0.13081894750000000000000000000000000000000000000000e-1 * t449 + 0.48591338250000000000000000000000000000000000000000e-2 * t452
  t479 = 0.1e1 + 0.1e1 / t477
  t480 = jnp.log(t479)
  t483 = 0.33774e-1 + 0.93933937500000000000000000000000000000000000000000e-3 * t443
  t488 = 0.17489865900000000000000000000000000000000000000000e0 * t446 + 0.30591644850000000000000000000000000000000000000000e-1 * t443 + 0.37162376550000000000000000000000000000000000000000e-2 * t449 + 0.41939708850000000000000000000000000000000000000000e-2 * t452
  t490 = 0.1e1 + 0.1e1 / t488
  t491 = jnp.log(t490)
  t492 = t483 * t491
  t494 = -t472 * t480 + t458 - 0.58482233974552040708313425006184496242808878304904e0 * t492
  t495 = t470 * t494
  t499 = -t458 + t464 * t495 + 0.58482233974552040708313425006184496242808878304904e0 * t470 * t492 - t329 - t414
  t501 = params.c_ab[1]
  t502 = 0.30000000000000000000000000000000000000000000000000e-2 * t102
  t503 = 0.30000000000000000000000000000000000000000000000000e-2 * t217
  t504 = t502 + t503
  t505 = t501 * t504
  t506 = 0.1e1 + t502 + t503
  t507 = 0.1e1 / t506
  t509 = params.c_ab[2]
  t510 = t504 ** 2
  t511 = t509 * t510
  t512 = t506 ** 2
  t513 = 0.1e1 / t512
  t515 = params.c_ab[3]
  t516 = t510 * t504
  t517 = t515 * t516
  t519 = 0.1e1 / t512 / t506
  t521 = params.c_ab[4]
  t522 = t510 ** 2
  t523 = t521 * t522
  t524 = t512 ** 2
  t525 = 0.1e1 / t524
  t527 = t505 * t507 + t511 * t513 + t517 * t519 + t523 * t525 + params.c_ab[0]
  t528 = t499 * t527
  t530 = t2 / t461
  t531 = t4 - t530
  t532 = t531 / 0.2e1
  t537 = t24 * t280
  t540 = t19 * t537 * t143 / 0.32e2
  t543 = t15 * t17 * t24
  t544 = t11 * t13 * t543
  t548 = t25 / t28 / t27 * t92
  t549 = t6 ** 2
  t550 = 0.1e1 / t549
  t551 = t142 * t550
  t556 = t47 * t46
  t557 = 0.1e1 / t556
  t559 = 0.1e1 / t25 / t3
  t560 = t559 * t17
  t562 = t35 * t560 * t40
  t564 = t33 * t34 * t36
  t565 = t28 ** 2
  t567 = t17 / t565
  t568 = t39 * t550
  t573 = -t564 * t567 * t568 * t531 / 0.54e2 - t562 / 0.54e2
  t574 = f.my_piecewise3(t45, t573, 0)
  t577 = t50 * t46
  t578 = 0.1e1 / t577
  t581 = t50 * t556
  t582 = 0.1e1 / t581
  t586 = 0.1e1 / t56 / t46
  t590 = 0.1e1 / t56 / t556
  t594 = 0.1e1 / t56 / t577
  t598 = 0.1e1 / t56 / t581
  t602 = 0.1e1 / t68 / t46
  t606 = f.my_piecewise3(t45, 0, t573)
  t608 = t81 * t79
  t613 = 0.1e1 / t78 / t72
  t617 = t72 * t82
  t629 = f.my_piecewise3(t44, -t557 * t574 / 0.18e2 + t578 * t574 / 0.240e3 - t582 * t574 / 0.4480e4 + t586 * t574 / 0.103680e6 - t590 * t574 / 0.2838528e7 + t594 * t574 / 0.89456640e8 - t598 * t574 / 0.3185049600e10 + t602 * t574 / 0.126340300800e12, -0.8e1 / 0.3e1 * t606 * t88 - 0.8e1 / 0.3e1 * t72 * (-t608 * t606 + 0.2e1 * t606 * t85 + 0.2e1 * t72 * (t613 * t606 * t81 / 0.2e1 - 0.4e1 * t617 * t606 - t74 * t606 * t81)))
  t635 = t97 * r0
  t637 = 0.1e1 / t99 / t635
  t642 = t112 * t97
  t644 = 0.1e1 / t98 / t642
  t645 = t644 * t117
  t652 = 0.1e1 / t124 / r0
  t653 = t652 * t127
  t661 = 0.1e1 / t99 / t124 / t635
  t662 = t661 * t138
  t667 = t132 * s0
  t671 = 0.1e1 / t98 / t124 / t642
  t673 = 0.1e1 / t137 / t104
  t683 = f.my_piecewise3(t8, 0, -0.3e1 / 0.32e2 * t532 * t10 * t18 * t144 - t540 - t544 * t548 * t551 * t531 / 0.32e2 - 0.3e1 / 0.32e2 * t19 * t26 * t29 * t629 * t142 - 0.3e1 / 0.32e2 * t19 * t26 * t93 * (-0.10666666666666666666666666666666666666666666666667e-1 * t96 * t637 * t105 + 0.42666666666666666666666666666666666666666666666668e-4 * t95 * t110 * t645 - 0.85333333333333333333333333333333333333333333333333e-4 * t111 * t645 + 0.34133333333333333333333333333333333333333333333334e-6 * t109 * t122 * t653 - 0.512e-6 * t123 * t653 + 0.20480000000000000000000000000000000000000000000001e-8 * t121 * t132 * t662 - 0.27306666666666666666666666666666666666666666666667e-8 * t133 * t662 + 0.10922666666666666666666666666666666666666666666667e-10 * t131 * t667 * t671 * t673))
  t691 = t154 * t537 * t255 / 0.32e2
  t693 = t153 * t13 * t543
  t697 = t25 / t156 / t155 * t209
  t698 = t149 ** 2
  t699 = 0.1e1 / t698
  t700 = t254 * t699
  t701 = -t531
  t706 = t165 * t164
  t707 = 0.1e1 / t706
  t709 = t35 * t560 * t158
  t710 = t156 ** 2
  t712 = t17 / t710
  t713 = t39 * t699
  t718 = -t564 * t712 * t713 * t701 / 0.54e2 - t709 / 0.54e2
  t719 = f.my_piecewise3(t163, t718, 0)
  t722 = t168 * t164
  t723 = 0.1e1 / t722
  t726 = t168 * t706
  t727 = 0.1e1 / t726
  t731 = 0.1e1 / t174 / t164
  t735 = 0.1e1 / t174 / t706
  t739 = 0.1e1 / t174 / t722
  t743 = 0.1e1 / t174 / t726
  t747 = 0.1e1 / t186 / t164
  t751 = f.my_piecewise3(t163, 0, t718)
  t753 = t198 * t196
  t758 = 0.1e1 / t195 / t190
  t762 = t190 * t199
  t774 = f.my_piecewise3(t162, -t707 * t719 / 0.18e2 + t723 * t719 / 0.240e3 - t727 * t719 / 0.4480e4 + t731 * t719 / 0.103680e6 - t735 * t719 / 0.2838528e7 + t739 * t719 / 0.89456640e8 - t743 * t719 / 0.3185049600e10 + t747 * t719 / 0.126340300800e12, -0.8e1 / 0.3e1 * t751 * t205 - 0.8e1 / 0.3e1 * t190 * (-t753 * t751 + 0.2e1 * t751 * t202 + 0.2e1 * t190 * (t758 * t751 * t198 / 0.2e1 - 0.4e1 * t762 * t751 - t191 * t751 * t198)))
  t781 = f.my_piecewise3(t151, 0, 0.3e1 / 0.32e2 * t532 * t10 * t18 * t256 - t691 - t693 * t697 * t700 * t701 / 0.32e2 - 0.3e1 / 0.32e2 * t154 * t26 * t157 * t774 * t254)
  t782 = f.my_piecewise3(t7, 0, t531)
  t785 = t262 * t560 * t266
  t786 = 0.11073577833333333333333333333333333333333333333333e-2 * t785
  t787 = 0.1e1 / t465
  t790 = f.my_piecewise3(t7, 0, -t787 * t531 / 0.3e1)
  t792 = t262 * t37 * t790
  t795 = (-t786 + 0.33220733500000000000000000000000000000000000000000e-2 * t792) * t290
  t796 = t287 ** 2
  t798 = t270 / t796
  t799 = 0.1e1 / t271
  t800 = t785 / 0.3e1
  t801 = -t800 + t792
  t802 = t799 * t801
  t804 = 0.18590345266666666666666666666666666666666666666667e-1 * t785
  t806 = t268 ** 0.5e0
  t807 = t806 * t801
  t810 = 0.1e1 / t279 / t3
  t811 = t810 * t281
  t813 = t278 * t811 * t283
  t814 = 0.51086658466666666666666666666666666666666666666667e-2 * t813
  t817 = t278 * t282 * t266 * t790
  t820 = 0.1e1 / t289
  t822 = t798 * (0.11807895435000000000000000000000000000000000000000e0 * t802 - t804 + 0.55771035800000000000000000000000000000000000000000e-1 * t792 + 0.19099978575000000000000000000000000000000000000000e-1 * t807 - t814 + 0.15325997540000000000000000000000000000000000000000e-1 * t817) * t820
  t823 = 0.53236443333333333333333333333333333333333333333333e-3 * t785
  t827 = t305 ** 2
  t829 = t300 / t827
  t831 = 0.16057207750000000000000000000000000000000000000000e-1 * t785
  t834 = 0.32394225500000000000000000000000000000000000000000e-2 * t813
  t837 = 0.1e1 / t307
  t840 = 0.31311312500000000000000000000000000000000000000000e-3 * t785
  t843 = (-t840 + 0.93933937500000000000000000000000000000000000000000e-3 * t792) * t319
  t845 = t316 ** 2
  t846 = 0.1e1 / t845
  t847 = t311 * t846
  t849 = 0.10197214950000000000000000000000000000000000000000e-1 * t785
  t852 = 0.27959805900000000000000000000000000000000000000000e-2 * t813
  t854 = 0.87449329500000000000000000000000000000000000000000e-1 * t802 - t849 + 0.30591644850000000000000000000000000000000000000000e-1 * t792 + 0.55743564825000000000000000000000000000000000000000e-2 * t807 - t852 + 0.83879417700000000000000000000000000000000000000000e-2 * t817
  t855 = 0.1e1 / t318
  t863 = t298 * t311
  t872 = f.my_piecewise3(t8, 0, t782 * t326 / 0.2e1 + t260 * (-t795 + t822 + t298 * (-(-t823 + 0.15970933000000000000000000000000000000000000000000e-2 * t792) * t308 + t829 * (0.10973915025000000000000000000000000000000000000000e0 * t802 - t831 + 0.48171623250000000000000000000000000000000000000000e-1 * t792 + 0.19622842125000000000000000000000000000000000000000e-1 * t807 - t834 + 0.97182676500000000000000000000000000000000000000000e-2 * t817) * t837 + t795 - t822 - 0.58482233974552040708313425006184496242808878304904e0 * t843 + 0.58482233974552040708313425006184496242808878304904e0 * t847 * t854 * t855) + 0.58482233974552040708313425006184496242808878304904e0 * t298 * t843 - 0.58482233974552040708313425006184496242808878304904e0 * t863 * t846 * t854 * t855) / 0.2e1)
  t878 = t644 * t342
  t884 = t652 * t349
  t890 = t661 * t356
  t897 = 0.1e1 / t355 / t334
  t903 = f.my_piecewise3(t150, 0, t701)
  t906 = t262 * t560 * t365
  t907 = 0.11073577833333333333333333333333333333333333333333e-2 * t906
  t908 = 0.1e1 / t467
  t911 = f.my_piecewise3(t150, 0, -t908 * t701 / 0.3e1)
  t913 = t262 * t37 * t911
  t916 = (-t907 + 0.33220733500000000000000000000000000000000000000000e-2 * t913) * t382
  t917 = t379 ** 2
  t919 = t369 / t917
  t920 = 0.1e1 / t370
  t921 = t906 / 0.3e1
  t922 = -t921 + t913
  t923 = t920 * t922
  t925 = 0.18590345266666666666666666666666666666666666666667e-1 * t906
  t927 = t367 ** 0.5e0
  t928 = t927 * t922
  t931 = t278 * t811 * t375
  t932 = 0.51086658466666666666666666666666666666666666666667e-2 * t931
  t935 = t278 * t282 * t365 * t911
  t938 = 0.1e1 / t381
  t940 = t919 * (0.11807895435000000000000000000000000000000000000000e0 * t923 - t925 + 0.55771035800000000000000000000000000000000000000000e-1 * t913 + 0.19099978575000000000000000000000000000000000000000e-1 * t928 - t932 + 0.15325997540000000000000000000000000000000000000000e-1 * t935) * t938
  t941 = 0.53236443333333333333333333333333333333333333333333e-3 * t906
  t945 = t390 ** 2
  t947 = t385 / t945
  t949 = 0.16057207750000000000000000000000000000000000000000e-1 * t906
  t952 = 0.32394225500000000000000000000000000000000000000000e-2 * t931
  t955 = 0.1e1 / t392
  t958 = 0.31311312500000000000000000000000000000000000000000e-3 * t906
  t961 = (-t958 + 0.93933937500000000000000000000000000000000000000000e-3 * t913) * t404
  t963 = t401 ** 2
  t964 = 0.1e1 / t963
  t965 = t396 * t964
  t967 = 0.10197214950000000000000000000000000000000000000000e-1 * t906
  t970 = 0.27959805900000000000000000000000000000000000000000e-2 * t931
  t972 = 0.87449329500000000000000000000000000000000000000000e-1 * t923 - t967 + 0.30591644850000000000000000000000000000000000000000e-1 * t913 + 0.55743564825000000000000000000000000000000000000000e-2 * t928 - t970 + 0.83879417700000000000000000000000000000000000000000e-2 * t935
  t973 = 0.1e1 / t403
  t981 = t298 * t396
  t990 = f.my_piecewise3(t151, 0, t903 * t411 / 0.2e1 + t362 * (-t916 + t940 + t298 * (-(-t941 + 0.15970933000000000000000000000000000000000000000000e-2 * t913) * t393 + t947 * (0.10973915025000000000000000000000000000000000000000e0 * t923 - t949 + 0.48171623250000000000000000000000000000000000000000e-1 * t913 + 0.19622842125000000000000000000000000000000000000000e-1 * t928 - t952 + 0.97182676500000000000000000000000000000000000000000e-2 * t935) * t955 + t916 - t940 - 0.58482233974552040708313425006184496242808878304904e0 * t961 + 0.58482233974552040708313425006184496242808878304904e0 * t965 * t972 * t973) + 0.58482233974552040708313425006184496242808878304904e0 * t298 * t961 - 0.58482233974552040708313425006184496242808878304904e0 * t981 * t964 * t972 * t973) / 0.2e1)
  t992 = t15 * t559
  t995 = 0.11073577833333333333333333333333333333333333333333e-2 * t261 * t992 * t457
  t996 = t454 ** 2
  t1001 = t16 * t559
  t1002 = 0.1e1 / t446 * t10 * t1001
  t1004 = t261 * t992
  t1006 = t443 ** 0.5e0
  t1008 = t1006 * t10 * t1001
  t1011 = t277 * t14 * t810
  t1016 = t445 / t996 * (-0.39359651450000000000000000000000000000000000000000e-1 * t1002 - 0.18590345266666666666666666666666666666666666666667e-1 * t1004 - 0.63666595250000000000000000000000000000000000000000e-2 * t1008 - 0.51086658466666666666666666666666666666666666666667e-2 * t1011) / t456
  t1020 = 0.4e1 * t459 * t2 * t463 * t495
  t1025 = 0.4e1 * t460 / t462 / t3 * t495
  t1028 = f.my_piecewise3(t7, 0, 0.4e1 / 0.3e1 * t264 * t531)
  t1031 = f.my_piecewise3(t150, 0, 0.4e1 / 0.3e1 * t363 * t701)
  t1033 = (t1028 + t1031) * t297
  t1039 = t477 ** 2
  t1053 = t488 ** 2
  t1054 = 0.1e1 / t1053
  t1060 = -0.29149776500000000000000000000000000000000000000000e-1 * t1002 - 0.10197214950000000000000000000000000000000000000000e-1 * t1004 - 0.18581188275000000000000000000000000000000000000000e-2 * t1008 - 0.27959805900000000000000000000000000000000000000000e-2 * t1011
  t1061 = 0.1e1 / t490
  t1067 = t464 * t470 * (0.53236443333333333333333333333333333333333333333333e-3 * t261 * t992 * t480 + t472 / t1039 * (-0.36579716750000000000000000000000000000000000000000e-1 * t1002 - 0.16057207750000000000000000000000000000000000000000e-1 * t1004 - 0.65409473750000000000000000000000000000000000000000e-2 * t1008 - 0.32394225500000000000000000000000000000000000000000e-2 * t1011) / t479 - t995 - t1016 + 0.18311555036753159941307229983139571945136646663793e-3 * t261 * t992 * t491 + 0.58482233974552040708313425006184496242808878304904e0 * t483 * t1054 * t1060 * t1061)
  t1074 = 0.18311555036753159941307229983139571945136646663793e-3 * t470 * t10 * t16 * t559 * t491
  t1079 = 0.58482233974552040708313425006184496242808878304904e0 * t470 * t483 * t1054 * t1060 * t1061
  t1080 = t995 + t1016 + t1020 - t1025 + t464 * t1033 * t494 + t1067 + 0.58482233974552040708313425006184496242808878304904e0 * t1033 * t492 - t1074 - t1079 - t872 - t990
  t1087 = t513 * s0 * t637
  t1090 = t509 * t504
  t1094 = t519 * s0 * t637
  t1097 = t515 * t510
  t1101 = t525 * s0 * t637
  t1104 = t521 * t516
  t1108 = 0.1e1 / t524 / t506
  vrho_0_ = t147 + t259 + t361 + t441 + t528 + t3 * (t683 + t781 + t872 * t360 + t329 * (-0.53333333333333333333333333333333333333333333333333e0 * t332 * t637 * t335 + 0.10666666666666666666666666666666666666666666666667e0 * t331 * t110 * t878 - 0.21333333333333333333333333333333333333333333333333e0 * t340 * t878 + 0.42666666666666666666666666666666666666666666666668e-1 * t339 * t122 * t884 - 0.64e-1 * t347 * t884 + 0.12800000000000000000000000000000000000000000000000e-1 * t346 * t132 * t890 - 0.17066666666666666666666666666666666666666666666667e-1 * t354 * t890 + 0.34133333333333333333333333333333333333333333333333e-2 * t353 * t667 * t671 * t897) + t990 * t440 + t1080 * t527 + t499 * (-0.80000000000000000000000000000000000000000000000000e-2 * t501 * s0 * t637 * t507 + 0.80000000000000000000000000000000000000000000000000e-2 * t505 * t1087 - 0.16000000000000000000000000000000000000000000000000e-1 * t1090 * t1087 + 0.16000000000000000000000000000000000000000000000000e-1 * t511 * t1094 - 0.24000000000000000000000000000000000000000000000000e-1 * t1097 * t1094 + 0.24000000000000000000000000000000000000000000000000e-1 * t517 * t1101 - 0.32000000000000000000000000000000000000000000000000e-1 * t1104 * t1101 + 0.32000000000000000000000000000000000000000000000000e-1 * t523 * t1108 * s0 * t637))
  t1117 = -t4 - t530
  t1118 = t1117 / 0.2e1
  t1131 = -t564 * t567 * t568 * t1117 / 0.54e2 - t562 / 0.54e2
  t1132 = f.my_piecewise3(t45, t1131, 0)
  t1150 = f.my_piecewise3(t45, 0, t1131)
  t1169 = f.my_piecewise3(t44, -t557 * t1132 / 0.18e2 + t578 * t1132 / 0.240e3 - t582 * t1132 / 0.4480e4 + t586 * t1132 / 0.103680e6 - t590 * t1132 / 0.2838528e7 + t594 * t1132 / 0.89456640e8 - t598 * t1132 / 0.3185049600e10 + t602 * t1132 / 0.126340300800e12, -0.8e1 / 0.3e1 * t1150 * t88 - 0.8e1 / 0.3e1 * t72 * (-t608 * t1150 + 0.2e1 * t1150 * t85 + 0.2e1 * t72 * (t613 * t1150 * t81 / 0.2e1 - 0.4e1 * t617 * t1150 - t74 * t1150 * t81)))
  t1176 = f.my_piecewise3(t8, 0, -0.3e1 / 0.32e2 * t1118 * t10 * t18 * t144 - t540 - t544 * t548 * t551 * t1117 / 0.32e2 - 0.3e1 / 0.32e2 * t19 * t26 * t29 * t1169 * t142)
  t1182 = -t1117
  t1191 = -t564 * t712 * t713 * t1182 / 0.54e2 - t709 / 0.54e2
  t1192 = f.my_piecewise3(t163, t1191, 0)
  t1210 = f.my_piecewise3(t163, 0, t1191)
  t1229 = f.my_piecewise3(t162, -t707 * t1192 / 0.18e2 + t723 * t1192 / 0.240e3 - t727 * t1192 / 0.4480e4 + t731 * t1192 / 0.103680e6 - t735 * t1192 / 0.2838528e7 + t739 * t1192 / 0.89456640e8 - t743 * t1192 / 0.3185049600e10 + t747 * t1192 / 0.126340300800e12, -0.8e1 / 0.3e1 * t1210 * t205 - 0.8e1 / 0.3e1 * t190 * (-t753 * t1210 + 0.2e1 * t1210 * t202 + 0.2e1 * t190 * (t758 * t1210 * t198 / 0.2e1 - 0.4e1 * t762 * t1210 - t191 * t1210 * t198)))
  t1235 = t212 * r1
  t1237 = 0.1e1 / t214 / t1235
  t1242 = t226 * t212
  t1244 = 0.1e1 / t213 / t1242
  t1245 = t1244 * t231
  t1252 = 0.1e1 / t237 / r1
  t1253 = t1252 * t240
  t1261 = 0.1e1 / t214 / t237 / t1235
  t1262 = t1261 * t250
  t1267 = t244 * s2
  t1271 = 0.1e1 / t213 / t237 / t1242
  t1273 = 0.1e1 / t249 / t219
  t1283 = f.my_piecewise3(t151, 0, 0.3e1 / 0.32e2 * t1118 * t10 * t18 * t256 - t691 - t693 * t697 * t700 * t1182 / 0.32e2 - 0.3e1 / 0.32e2 * t154 * t26 * t157 * t1229 * t254 - 0.3e1 / 0.32e2 * t154 * t26 * t210 * (-0.10666666666666666666666666666666666666666666666667e-1 * t211 * t1237 * t220 + 0.42666666666666666666666666666666666666666666666668e-4 * t95 * t224 * t1245 - 0.85333333333333333333333333333333333333333333333333e-4 * t225 * t1245 + 0.34133333333333333333333333333333333333333333333334e-6 * t109 * t235 * t1253 - 0.512e-6 * t236 * t1253 + 0.20480000000000000000000000000000000000000000000001e-8 * t121 * t244 * t1262 - 0.27306666666666666666666666666666666666666666666667e-8 * t245 * t1262 + 0.10922666666666666666666666666666666666666666666667e-10 * t131 * t1267 * t1271 * t1273))
  t1284 = f.my_piecewise3(t7, 0, t1117)
  t1288 = f.my_piecewise3(t7, 0, -t787 * t1117 / 0.3e1)
  t1290 = t262 * t37 * t1288
  t1293 = (-t786 + 0.33220733500000000000000000000000000000000000000000e-2 * t1290) * t290
  t1294 = -t800 + t1290
  t1295 = t799 * t1294
  t1298 = t806 * t1294
  t1302 = t278 * t282 * t266 * t1288
  t1306 = t798 * (0.11807895435000000000000000000000000000000000000000e0 * t1295 - t804 + 0.55771035800000000000000000000000000000000000000000e-1 * t1290 + 0.19099978575000000000000000000000000000000000000000e-1 * t1298 - t814 + 0.15325997540000000000000000000000000000000000000000e-1 * t1302) * t820
  t1319 = (-t840 + 0.93933937500000000000000000000000000000000000000000e-3 * t1290) * t319
  t1325 = 0.87449329500000000000000000000000000000000000000000e-1 * t1295 - t849 + 0.30591644850000000000000000000000000000000000000000e-1 * t1290 + 0.55743564825000000000000000000000000000000000000000e-2 * t1298 - t852 + 0.83879417700000000000000000000000000000000000000000e-2 * t1302
  t1341 = f.my_piecewise3(t8, 0, t1284 * t326 / 0.2e1 + t260 * (-t1293 + t1306 + t298 * (-(-t823 + 0.15970933000000000000000000000000000000000000000000e-2 * t1290) * t308 + t829 * (0.10973915025000000000000000000000000000000000000000e0 * t1295 - t831 + 0.48171623250000000000000000000000000000000000000000e-1 * t1290 + 0.19622842125000000000000000000000000000000000000000e-1 * t1298 - t834 + 0.97182676500000000000000000000000000000000000000000e-2 * t1302) * t837 + t1293 - t1306 - 0.58482233974552040708313425006184496242808878304904e0 * t1319 + 0.58482233974552040708313425006184496242808878304904e0 * t847 * t1325 * t855) + 0.58482233974552040708313425006184496242808878304904e0 * t298 * t1319 - 0.58482233974552040708313425006184496242808878304904e0 * t863 * t846 * t1325 * t855) / 0.2e1)
  t1343 = f.my_piecewise3(t150, 0, t1182)
  t1347 = f.my_piecewise3(t150, 0, -t908 * t1182 / 0.3e1)
  t1349 = t262 * t37 * t1347
  t1352 = (-t907 + 0.33220733500000000000000000000000000000000000000000e-2 * t1349) * t382
  t1353 = -t921 + t1349
  t1354 = t920 * t1353
  t1357 = t927 * t1353
  t1361 = t278 * t282 * t365 * t1347
  t1365 = t919 * (0.11807895435000000000000000000000000000000000000000e0 * t1354 - t925 + 0.55771035800000000000000000000000000000000000000000e-1 * t1349 + 0.19099978575000000000000000000000000000000000000000e-1 * t1357 - t932 + 0.15325997540000000000000000000000000000000000000000e-1 * t1361) * t938
  t1378 = (-t958 + 0.93933937500000000000000000000000000000000000000000e-3 * t1349) * t404
  t1384 = 0.87449329500000000000000000000000000000000000000000e-1 * t1354 - t967 + 0.30591644850000000000000000000000000000000000000000e-1 * t1349 + 0.55743564825000000000000000000000000000000000000000e-2 * t1357 - t970 + 0.83879417700000000000000000000000000000000000000000e-2 * t1361
  t1400 = f.my_piecewise3(t151, 0, t1343 * t411 / 0.2e1 + t362 * (-t1352 + t1365 + t298 * (-(-t941 + 0.15970933000000000000000000000000000000000000000000e-2 * t1349) * t393 + t947 * (0.10973915025000000000000000000000000000000000000000e0 * t1354 - t949 + 0.48171623250000000000000000000000000000000000000000e-1 * t1349 + 0.19622842125000000000000000000000000000000000000000e-1 * t1357 - t952 + 0.97182676500000000000000000000000000000000000000000e-2 * t1361) * t955 + t1352 - t1365 - 0.58482233974552040708313425006184496242808878304904e0 * t1378 + 0.58482233974552040708313425006184496242808878304904e0 * t965 * t1384 * t973) + 0.58482233974552040708313425006184496242808878304904e0 * t298 * t1378 - 0.58482233974552040708313425006184496242808878304904e0 * t981 * t964 * t1384 * t973) / 0.2e1)
  t1406 = t1244 * t424
  t1412 = t1252 * t430
  t1418 = t1261 * t436
  t1425 = 0.1e1 / t435 / t417
  t1433 = f.my_piecewise3(t7, 0, 0.4e1 / 0.3e1 * t264 * t1117)
  t1436 = f.my_piecewise3(t150, 0, 0.4e1 / 0.3e1 * t363 * t1182)
  t1438 = (t1433 + t1436) * t297
  t1443 = t995 + t1016 - t1020 - t1025 + t464 * t1438 * t494 + t1067 + 0.58482233974552040708313425006184496242808878304904e0 * t1438 * t492 - t1074 - t1079 - t1341 - t1400
  t1450 = t513 * s2 * t1237
  t1456 = t519 * s2 * t1237
  t1462 = t525 * s2 * t1237
  vrho_1_ = t147 + t259 + t361 + t441 + t528 + t3 * (t1176 + t1283 + t1341 * t360 + t1400 * t440 + t414 * (-0.53333333333333333333333333333333333333333333333333e0 * t415 * t1237 * t418 + 0.10666666666666666666666666666666666666666666666667e0 * t331 * t224 * t1406 - 0.21333333333333333333333333333333333333333333333333e0 * t422 * t1406 + 0.42666666666666666666666666666666666666666666666668e-1 * t339 * t235 * t1412 - 0.64e-1 * t428 * t1412 + 0.12800000000000000000000000000000000000000000000000e-1 * t346 * t244 * t1418 - 0.17066666666666666666666666666666666666666666666667e-1 * t434 * t1418 + 0.34133333333333333333333333333333333333333333333333e-2 * t353 * t1267 * t1271 * t1425) + t1443 * t527 + t499 * (-0.80000000000000000000000000000000000000000000000000e-2 * t501 * s2 * t1237 * t507 + 0.80000000000000000000000000000000000000000000000000e-2 * t505 * t1450 - 0.16000000000000000000000000000000000000000000000000e-1 * t1090 * t1450 + 0.16000000000000000000000000000000000000000000000000e-1 * t511 * t1456 - 0.24000000000000000000000000000000000000000000000000e-1 * t1097 * t1456 + 0.24000000000000000000000000000000000000000000000000e-1 * t517 * t1462 - 0.32000000000000000000000000000000000000000000000000e-1 * t1104 * t1462 + 0.32000000000000000000000000000000000000000000000000e-1 * t523 * t1108 * s2 * t1237))
  t1495 = 0.1e1 / t98 / t124 / t113
  t1504 = f.my_piecewise3(t8, 0, -0.3e1 / 0.32e2 * t19 * t26 * t93 * (0.4e-2 * t95 * t101 * t105 - 0.16e-4 * t96 * t118 + 0.32e-4 * t109 * s0 * t118 - 0.128e-6 * t111 * t128 + 0.192e-6 * t121 * t110 * t128 - 0.768e-9 * t123 * t139 + 0.1024e-8 * t131 * t122 * t139 - 0.4096e-11 * t133 * t1495 * t673))
  t1531 = t513 * t101
  t1536 = t519 * t101
  t1541 = t525 * t101
  vsigma_0_ = t3 * (t1504 + t329 * (0.2e0 * t331 * t101 * t335 - 0.4e-1 * t332 * t343 + 0.8e-1 * t339 * s0 * t343 - 0.16e-1 * t340 * t350 + 0.24e-1 * t346 * t110 * t350 - 0.48e-2 * t347 * t357 + 0.64e-2 * t353 * t122 * t357 - 0.128e-2 * t354 * t1495 * t897) + t499 * (0.30000000000000000000000000000000000000000000000000e-2 * t501 * t101 * t507 - 0.30000000000000000000000000000000000000000000000000e-2 * t505 * t1531 + 0.60000000000000000000000000000000000000000000000000e-2 * t1090 * t1531 - 0.60000000000000000000000000000000000000000000000000e-2 * t511 * t1536 + 0.90000000000000000000000000000000000000000000000000e-2 * t1097 * t1536 - 0.90000000000000000000000000000000000000000000000000e-2 * t517 * t1541 + 0.12000000000000000000000000000000000000000000000000e-1 * t1104 * t1541 - 0.12000000000000000000000000000000000000000000000000e-1 * t523 * t1108 * t101))
  vsigma_1_ = 0.0e0
  t1572 = 0.1e1 / t213 / t237 / t227
  t1581 = f.my_piecewise3(t151, 0, -0.3e1 / 0.32e2 * t154 * t26 * t210 * (0.4e-2 * t95 * t216 * t220 - 0.16e-4 * t211 * t232 + 0.32e-4 * t109 * s2 * t232 - 0.128e-6 * t225 * t241 + 0.192e-6 * t121 * t224 * t241 - 0.768e-9 * t236 * t251 + 0.1024e-8 * t131 * t235 * t251 - 0.4096e-11 * t245 * t1572 * t1273))
  t1608 = t513 * t216
  t1613 = t519 * t216
  t1618 = t525 * t216
  vsigma_2_ = t3 * (t1581 + t414 * (0.2e0 * t331 * t216 * t418 - 0.4e-1 * t415 * t425 + 0.8e-1 * t339 * s2 * t425 - 0.16e-1 * t422 * t431 + 0.24e-1 * t346 * t224 * t431 - 0.48e-2 * t428 * t437 + 0.64e-2 * t353 * t235 * t437 - 0.128e-2 * t434 * t1572 * t1425) + t499 * (0.30000000000000000000000000000000000000000000000000e-2 * t501 * t216 * t507 - 0.30000000000000000000000000000000000000000000000000e-2 * t505 * t1608 + 0.60000000000000000000000000000000000000000000000000e-2 * t1090 * t1608 - 0.60000000000000000000000000000000000000000000000000e-2 * t511 * t1613 + 0.90000000000000000000000000000000000000000000000000e-2 * t1097 * t1613 - 0.90000000000000000000000000000000000000000000000000e-2 * t517 * t1618 + 0.12000000000000000000000000000000000000000000000000e-1 * t1104 * t1618 - 0.12000000000000000000000000000000000000000000000000e-1 * t523 * t1108 * t216))
  _b = lambda x: (jnp.asarray(x) + jnp.zeros_like(r0))
  vrho_0_ = _b(vrho_0_)
  vrho_1_ = _b(vrho_1_)
  vsigma_0_ = _b(vsigma_0_)
  vsigma_1_ = _b(vsigma_1_)
  vsigma_2_ = _b(vsigma_2_)
  res = {'vrho': jnp.stack([vrho_0_, vrho_1_], axis=-1), 'vsigma': jnp.stack([vsigma_0_, vsigma_1_, vsigma_2_], axis=-1)}
  return res

def unpol_vxc(p, r, s=None, l=None, tau=None):
  f = funcs(p)
  params = f.params
  r0, s0, l0, tau0 = r, s, l, tau
  params_c_ab_raw = params.c_ab
  if isinstance(params_c_ab_raw, (str, bytes, dict)):
    params_c_ab = params_c_ab_raw
  else:
    try:
      params_c_ab_seq = list(params_c_ab_raw)
    except TypeError:
      params_c_ab = params_c_ab_raw
    else:
      params_c_ab_seq = np.asarray(params_c_ab_seq, dtype=np.float64)
      params_c_ab = np.concatenate((np.array([np.nan], dtype=np.float64), params_c_ab_seq))
  params_c_ss_raw = params.c_ss
  if isinstance(params_c_ss_raw, (str, bytes, dict)):
    params_c_ss = params_c_ss_raw
  else:
    try:
      params_c_ss_seq = list(params_c_ss_raw)
    except TypeError:
      params_c_ss = params_c_ss_raw
    else:
      params_c_ss_seq = np.asarray(params_c_ss_seq, dtype=np.float64)
      params_c_ss = np.concatenate((np.array([np.nan], dtype=np.float64), params_c_ss_seq))
  params_c_x_raw = params.c_x
  if isinstance(params_c_x_raw, (str, bytes, dict)):
    params_c_x = params_c_x_raw
  else:
    try:
      params_c_x_seq = list(params_c_x_raw)
    except TypeError:
      params_c_x = params_c_x_raw
    else:
      params_c_x_seq = np.asarray(params_c_x_seq, dtype=np.float64)
      params_c_x = np.concatenate((np.array([np.nan], dtype=np.float64), params_c_x_seq))

  params_pp = np.array([np.nan, 1, 1, 1], dtype=np.float64)

  params_a = np.array([np.nan, 0.031091, 0.015545, 0.016887], dtype=np.float64)

  params_alpha1 = np.array([np.nan, 0.2137, 0.20548, 0.11125], dtype=np.float64)

  params_beta1 = np.array([np.nan, 7.5957, 14.1189, 10.357], dtype=np.float64)

  params_beta2 = np.array([np.nan, 3.5876, 6.1977, 3.6231], dtype=np.float64)

  params_beta3 = np.array([np.nan, 1.6382, 3.3662, 0.88026], dtype=np.float64)

  params_beta4 = np.array([np.nan, 0.49294, 0.62517, 0.49671], dtype=np.float64)

  params_fz20 = 1.709921

  att_erf_aux1 = lambda a: jnp.sqrt(jnp.pi) * jax.lax.erf(1 / (2 * a))

  att_erf_aux2 = lambda a: jnp.exp(-1 / (4 * a ** 2)) - 1

  a_cnst = (4 / (9 * jnp.pi)) ** (1 / 3) * f.p.cam_omega / 2

  lda_x_ax = -f.RS_FACTOR * X_FACTOR_C / 2 ** (4 / 3)

  b97_g = lambda gamma, cc, x: jnp.sum(jnp.array([cc[i] * (gamma * x ** 2 / (1 + gamma * x ** 2)) ** (i - 1) for i in range(1, 5 + 1)]), axis=0)

  g_aux = lambda k, rs: params_beta1[k] * jnp.sqrt(rs) + params_beta2[k] * rs + params_beta3[k] * rs ** 1.5 + params_beta4[k] * rs ** (params_pp[k] + 1)

  att_erf_aux3 = lambda a: 2 * a ** 2 * att_erf_aux2(a) + 1 / 2

  b97_fpar = lambda lda_func, mgamma, cc, rs, z, xs0, xs1: +lda_stoll_par(f, params, lda_func, rs, z) * b97_g(mgamma, cc, xs0) + lda_stoll_par(f, params, lda_func, rs, -z) * b97_g(mgamma, cc, xs1)

  b97_fperp = lambda lda_func, mgamma, cc, rs, z, xs0, xs1: lda_stoll_perp(f, params, lda_func, rs, z) * b97_g(mgamma, cc, jnp.sqrt(xs0 ** 2 + xs1 ** 2) / jnp.sqrt(2))

  g = lambda k, rs: -2 * params_a[k] * (1 + params_alpha1[k] * rs) * jnp.log(1 + 1 / (2 * params_a[k] * g_aux(k, rs)))

  attenuation_erf0 = lambda a: 1 - 8 / 3 * a * (att_erf_aux1(a) + 2 * a * (att_erf_aux2(a) - att_erf_aux3(a)))

  b97_f = lambda lda_func, gamma_ss, cc_ss, gamma_ab, cc_ab, rs, z, xs0, xs1: +b97_fpar(lda_func, gamma_ss, cc_ss, rs, z, xs0, xs1) + b97_fperp(lda_func, gamma_ab, cc_ab, rs, z, xs0, xs1)

  f_pw = lambda rs, zeta: g(1, rs) + zeta ** 4 * f.f_zeta(zeta) * (g(2, rs) - g(1, rs) + g(3, rs) / params_fz20) - f.f_zeta(zeta) * g(3, rs) / params_fz20

  attenuation_erf = lambda a: apply_piecewise(a, lambda _aval: _aval >= 1.35, lambda _aval: -1 / 2021444812800 * (1.0 / jnp.maximum(_aval, 1.35)) ** 16 + 1 / 44590694400 * (1.0 / jnp.maximum(_aval, 1.35)) ** 14 - 1 / 1073479680 * (1.0 / jnp.maximum(_aval, 1.35)) ** 12 + 1 / 28385280 * (1.0 / jnp.maximum(_aval, 1.35)) ** 10 - 1 / 829440 * (1.0 / jnp.maximum(_aval, 1.35)) ** 8 + 1 / 26880 * (1.0 / jnp.maximum(_aval, 1.35)) ** 6 - 1 / 960 * (1.0 / jnp.maximum(_aval, 1.35)) ** 4 + 1 / 36 * (1.0 / jnp.maximum(_aval, 1.35)) ** 2, lambda _aval: attenuation_erf0(jnp.minimum(_aval, 1.35)))

  lda_x_erf_spin = lambda rs, z: lda_x_ax * f.opz_pow_n(z, 4 / 3) / rs * attenuation_erf(a_cnst * rs / f.opz_pow_n(z, 1 / 3))

  wb97_x = lambda rs, z, xs0, xs1: f.my_piecewise3(f.screen_dens_zeta(rs, z), 0, (1 + z) / 2 * lda_x_erf_spin(rs * (2 / (1 + z)) ** (1 / 3), 1) * b97_g(0.004, params_c_x, xs0)) + f.my_piecewise3(f.screen_dens_zeta(rs, -z), 0, (1 - z) / 2 * lda_x_erf_spin(rs * (2 / (1 - z)) ** (1 / 3), 1) * b97_g(0.004, params_c_x, xs1))

  functional_body = lambda rs, z, xt, xs0, xs1: wb97_x(rs, z, xs0, xs1) + b97_f(f_pw, 0.2, params_c_ss, 0.006, params_c_ab, rs, z, xs0, xs1)

  t3 = 0.1e1 <= f.p.zeta_threshold
  t4 = r0 / 0.2e1 <= f.p.dens_threshold or t3
  t5 = 3 ** (0.1e1 / 0.3e1)
  t7 = (0.1e1 / jnp.pi) ** (0.1e1 / 0.3e1)
  t8 = t5 * t7
  t9 = 4 ** (0.1e1 / 0.3e1)
  t10 = t9 ** 2
  t11 = 2 ** (0.1e1 / 0.3e1)
  t13 = t8 * t10 * t11
  t14 = 0.2e1 <= f.p.zeta_threshold
  t15 = f.p.zeta_threshold ** (0.1e1 / 0.3e1)
  t16 = t15 * f.p.zeta_threshold
  t18 = f.my_piecewise3(t14, t16, 0.2e1 * t11)
  t19 = r0 ** (0.1e1 / 0.3e1)
  t20 = t18 * t19
  t21 = 9 ** (0.1e1 / 0.3e1)
  t22 = t21 ** 2
  t23 = t7 ** 2
  t25 = t22 * t23 * f.p.cam_omega
  t26 = 0.1e1 / t19
  t28 = f.my_piecewise3(t14, t15, t11)
  t30 = t11 / t28
  t33 = t25 * t5 * t26 * t30 / 0.18e2
  t34 = 0.135e1 <= t33
  t35 = 0.135e1 < t33
  t36 = f.my_piecewise3(t35, t33, 0.135e1)
  t37 = t36 ** 2
  t40 = t37 ** 2
  t43 = t40 * t37
  t46 = t40 ** 2
  t58 = t46 ** 2
  t62 = f.my_piecewise3(t35, 0.135e1, t33)
  t63 = jnp.sqrt(jnp.pi)
  t64 = 0.1e1 / t62
  t66 = jax.lax.erf(t64 / 0.2e1)
  t68 = t62 ** 2
  t69 = 0.1e1 / t68
  t71 = jnp.exp(-t69 / 0.4e1)
  t72 = t71 - 0.1e1
  t75 = t71 - 0.3e1 / 0.2e1 - 0.2e1 * t68 * t72
  t78 = 0.2e1 * t62 * t75 + t63 * t66
  t82 = f.my_piecewise3(t34, 0.1e1 / t37 / 0.36e2 - 0.1e1 / t40 / 0.960e3 + 0.1e1 / t43 / 0.26880e5 - 0.1e1 / t46 / 0.829440e6 + 0.1e1 / t46 / t37 / 0.28385280e8 - 0.1e1 / t46 / t40 / 0.1073479680e10 + 0.1e1 / t46 / t43 / 0.44590694400e11 - 0.1e1 / t58 / 0.2021444812800e13, 0.1e1 - 0.8e1 / 0.3e1 * t62 * t78)
  t84 = params.c_x[1]
  t85 = t84 * s0
  t86 = t11 ** 2
  t87 = r0 ** 2
  t88 = t19 ** 2
  t90 = 0.1e1 / t88 / t87
  t91 = t86 * t90
  t93 = s0 * t86 * t90
  t95 = 0.1e1 + 0.4e-2 * t93
  t96 = 0.1e1 / t95
  t100 = params.c_x[2]
  t101 = s0 ** 2
  t102 = t100 * t101
  t103 = t87 ** 2
  t104 = t103 * r0
  t107 = t11 / t19 / t104
  t108 = t95 ** 2
  t109 = 0.1e1 / t108
  t110 = t107 * t109
  t113 = params.c_x[3]
  t114 = t101 * s0
  t115 = t113 * t114
  t116 = t103 ** 2
  t117 = 0.1e1 / t116
  t119 = 0.1e1 / t108 / t95
  t120 = t117 * t119
  t123 = params.c_x[4]
  t124 = t101 ** 2
  t125 = t123 * t124
  t129 = t86 / t88 / t116 / t87
  t130 = t108 ** 2
  t131 = 0.1e1 / t130
  t132 = t129 * t131
  t135 = params.c_x[0] + 0.4e-2 * t85 * t91 * t96 + 0.32e-4 * t102 * t110 + 0.256e-6 * t115 * t120 + 0.1024e-8 * t125 * t132
  t136 = t82 * t135
  t140 = f.my_piecewise3(t4, 0, -0.3e1 / 0.64e2 * t13 * t20 * t136)
  t142 = f.my_piecewise3(t3, f.p.zeta_threshold, 1)
  t143 = t8 * t10
  t146 = f.my_piecewise3(t3, 0.1e1 / t15, 1)
  t148 = t143 * t26 * t11 * t146
  t150 = 0.62182e-1 + 0.33220733500000000000000000000000000000000000000000e-2 * t148
  t151 = jnp.sqrt(t148)
  t154 = t148 ** 0.15e1
  t156 = t5 ** 2
  t157 = t156 * t23
  t158 = t157 * t9
  t159 = 0.1e1 / t88
  t161 = t146 ** 2
  t163 = t158 * t159 * t86 * t161
  t165 = 0.23615790870000000000000000000000000000000000000000e0 * t151 + 0.55771035800000000000000000000000000000000000000000e-1 * t148 + 0.12733319050000000000000000000000000000000000000000e-1 * t154 + 0.76629987700000000000000000000000000000000000000000e-2 * t163
  t167 = 0.1e1 + 0.1e1 / t165
  t168 = jnp.log(t167)
  t169 = t150 * t168
  t171 = f.my_piecewise3(0.0e0 <= f.p.zeta_threshold, t16, 0)
  t175 = 0.1e1 / (0.2e1 * t11 - 0.2e1)
  t176 = (t18 + t171 - 0.2e1) * t175
  t178 = 0.31090e-1 + 0.15970933000000000000000000000000000000000000000000e-2 * t148
  t183 = 0.21947830050000000000000000000000000000000000000000e0 * t151 + 0.48171623250000000000000000000000000000000000000000e-1 * t148 + 0.13081894750000000000000000000000000000000000000000e-1 * t154 + 0.48591338250000000000000000000000000000000000000000e-2 * t163
  t185 = 0.1e1 + 0.1e1 / t183
  t186 = jnp.log(t185)
  t189 = 0.33774e-1 + 0.93933937500000000000000000000000000000000000000000e-3 * t148
  t194 = 0.17489865900000000000000000000000000000000000000000e0 * t151 + 0.30591644850000000000000000000000000000000000000000e-1 * t148 + 0.37162376550000000000000000000000000000000000000000e-2 * t154 + 0.41939708850000000000000000000000000000000000000000e-2 * t163
  t196 = 0.1e1 + 0.1e1 / t194
  t197 = jnp.log(t196)
  t198 = t189 * t197
  t207 = f.my_piecewise3(t4, 0, t142 * (-t169 + t176 * (-t178 * t186 + t169 - 0.58482233974552040708313425006184496242808878304904e0 * t198) + 0.58482233974552040708313425006184496242808878304904e0 * t176 * t198) / 0.2e1)
  t209 = params.c_ss[1]
  t210 = t209 * s0
  t212 = 0.1e1 + 0.2e0 * t93
  t213 = 0.1e1 / t212
  t217 = params.c_ss[2]
  t218 = t217 * t101
  t219 = t212 ** 2
  t220 = 0.1e1 / t219
  t221 = t107 * t220
  t224 = params.c_ss[3]
  t225 = t224 * t114
  t227 = 0.1e1 / t219 / t212
  t228 = t117 * t227
  t231 = params.c_ss[4]
  t232 = t231 * t124
  t233 = t219 ** 2
  t234 = 0.1e1 / t233
  t235 = t129 * t234
  t238 = params.c_ss[0] + 0.2e0 * t210 * t91 * t213 + 0.8e-1 * t218 * t221 + 0.32e-1 * t225 * t228 + 0.64e-2 * t232 * t235
  t242 = t8 * t10 * t26
  t244 = 0.62182e-1 + 0.33220733500000000000000000000000000000000000000000e-2 * t242
  t245 = jnp.sqrt(t242)
  t248 = t242 ** 0.15e1
  t251 = t157 * t9 * t159
  t253 = 0.23615790870000000000000000000000000000000000000000e0 * t245 + 0.55771035800000000000000000000000000000000000000000e-1 * t242 + 0.12733319050000000000000000000000000000000000000000e-1 * t248 + 0.76629987700000000000000000000000000000000000000000e-2 * t251
  t255 = 0.1e1 + 0.1e1 / t253
  t256 = jnp.log(t255)
  t258 = f.my_piecewise3(t3, t16, 1)
  t261 = (0.2e1 * t258 - 0.2e1) * t175
  t263 = 0.33774e-1 + 0.93933937500000000000000000000000000000000000000000e-3 * t242
  t268 = 0.17489865900000000000000000000000000000000000000000e0 * t245 + 0.30591644850000000000000000000000000000000000000000e-1 * t242 + 0.37162376550000000000000000000000000000000000000000e-2 * t248 + 0.41939708850000000000000000000000000000000000000000e-2 * t251
  t270 = 0.1e1 + 0.1e1 / t268
  t271 = jnp.log(t270)
  t276 = -t244 * t256 + 0.58482233974552040708313425006184496242808878304904e0 * t261 * t263 * t271 - 0.2e1 * t207
  t278 = params.c_ab[1]
  t279 = t278 * s0
  t281 = 0.1e1 + 0.6e-2 * t93
  t282 = 0.1e1 / t281
  t286 = params.c_ab[2]
  t287 = t286 * t101
  t288 = t281 ** 2
  t289 = 0.1e1 / t288
  t290 = t107 * t289
  t293 = params.c_ab[3]
  t294 = t293 * t114
  t296 = 0.1e1 / t288 / t281
  t297 = t117 * t296
  t300 = params.c_ab[4]
  t301 = t300 * t124
  t302 = t288 ** 2
  t303 = 0.1e1 / t302
  t304 = t129 * t303
  t307 = params.c_ab[0] + 0.6e-2 * t279 * t91 * t282 + 0.72e-4 * t287 * t290 + 0.864e-6 * t294 * t297 + 0.5184e-8 * t301 * t304
  t313 = t37 * t36
  t316 = 0.1e1 / t19 / r0
  t320 = t25 * t5 * t316 * t30 / 0.54e2
  t321 = f.my_piecewise3(t35, -t320, 0)
  t324 = t40 * t36
  t328 = t40 * t313
  t353 = f.my_piecewise3(t35, 0, -t320)
  t376 = f.my_piecewise3(t34, -0.1e1 / t313 * t321 / 0.18e2 + 0.1e1 / t324 * t321 / 0.240e3 - 0.1e1 / t328 * t321 / 0.4480e4 + 0.1e1 / t46 / t36 * t321 / 0.103680e6 - 0.1e1 / t46 / t313 * t321 / 0.2838528e7 + 0.1e1 / t46 / t324 * t321 / 0.89456640e8 - 0.1e1 / t46 / t328 * t321 / 0.3185049600e10 + 0.1e1 / t58 / t36 * t321 / 0.126340300800e12, -0.8e1 / 0.3e1 * t353 * t78 - 0.8e1 / 0.3e1 * t62 * (-t71 * t69 * t353 + 0.2e1 * t353 * t75 + 0.2e1 * t62 * (0.1e1 / t68 / t62 * t353 * t71 / 0.2e1 - 0.4e1 * t62 * t72 * t353 - t64 * t353 * t71)))
  t381 = t87 * r0
  t384 = t86 / t88 / t381
  t389 = t103 * t87
  t392 = t11 / t19 / t389
  t393 = t392 * t109
  t400 = 0.1e1 / t116 / r0
  t401 = t400 * t119
  t409 = 0.1e1 / t88 / t116 / t381
  t411 = t409 * t131 * t86
  t416 = t124 * s0
  t421 = t11 / t19 / t116 / t389
  t423 = 0.1e1 / t130 / t95
  t433 = f.my_piecewise3(t4, 0, -t13 * t18 * t159 * t136 / 0.64e2 - 0.3e1 / 0.64e2 * t13 * t20 * t376 * t135 - 0.3e1 / 0.64e2 * t13 * t20 * t82 * (-0.10666666666666666666666666666666666666666666666667e-1 * t85 * t384 * t96 + 0.85333333333333333333333333333333333333333333333336e-4 * t84 * t101 * t393 - 0.17066666666666666666666666666666666666666666666667e-3 * t102 * t393 + 0.13653333333333333333333333333333333333333333333334e-5 * t100 * t114 * t401 - 0.2048e-5 * t115 * t401 + 0.81920000000000000000000000000000000000000000000003e-8 * t113 * t124 * t411 - 0.10922666666666666666666666666666666666666666666667e-7 * t125 * t411 + 0.87381333333333333333333333333333333333333333333336e-10 * t123 * t416 * t421 * t423))
  t435 = t316 * t11
  t439 = 0.11073577833333333333333333333333333333333333333333e-2 * t143 * t435 * t146 * t168
  t440 = t165 ** 2
  t446 = t10 * t316
  t447 = t11 * t146
  t448 = t446 * t447
  t449 = 0.1e1 / t151 * t5 * t7 * t448
  t452 = t143 * t435 * t146
  t454 = t148 ** 0.5e0
  t457 = t454 * t5 * t7 * t448
  t460 = 0.1e1 / t88 / r0
  t463 = t158 * t460 * t86 * t161
  t468 = t150 / t440 * (-0.39359651450000000000000000000000000000000000000000e-1 * t449 - 0.18590345266666666666666666666666666666666666666667e-1 * t452 - 0.63666595250000000000000000000000000000000000000000e-2 * t457 - 0.51086658466666666666666666666666666666666666666667e-2 * t463) / t167
  t473 = t183 ** 2
  t488 = t194 ** 2
  t489 = 0.1e1 / t488
  t495 = -0.29149776500000000000000000000000000000000000000000e-1 * t449 - 0.10197214950000000000000000000000000000000000000000e-1 * t452 - 0.18581188275000000000000000000000000000000000000000e-2 * t457 - 0.27959805900000000000000000000000000000000000000000e-2 * t463
  t496 = 0.1e1 / t196
  t515 = f.my_piecewise3(t4, 0, t142 * (t439 + t468 + t176 * (0.53236443333333333333333333333333333333333333333333e-3 * t143 * t435 * t146 * t186 + t178 / t473 * (-0.36579716750000000000000000000000000000000000000000e-1 * t449 - 0.16057207750000000000000000000000000000000000000000e-1 * t452 - 0.65409473750000000000000000000000000000000000000000e-2 * t457 - 0.32394225500000000000000000000000000000000000000000e-2 * t463) / t185 - t439 - t468 + 0.18311555036753159941307229983139571945136646663793e-3 * t143 * t435 * t146 * t197 + 0.58482233974552040708313425006184496242808878304904e0 * t189 * t489 * t495 * t496) - 0.18311555036753159941307229983139571945136646663793e-3 * t176 * t8 * t446 * t447 * t197 - 0.58482233974552040708313425006184496242808878304904e0 * t176 * t189 * t489 * t495 * t496) / 0.2e1)
  t522 = t392 * t220
  t528 = t400 * t227
  t535 = t409 * t234 * t86
  t542 = 0.1e1 / t233 / t212
  t552 = t253 ** 2
  t557 = t7 * t10
  t558 = t557 * t316
  t559 = 0.1e1 / t245 * t5 * t558
  t561 = t8 * t446
  t563 = t242 ** 0.5e0
  t565 = t563 * t5 * t558
  t568 = t157 * t9 * t460
  t580 = t268 ** 2
  t599 = t392 * t289
  t605 = t400 * t296
  t612 = t409 * t303 * t86
  t619 = 0.1e1 / t302 / t281
  vrho_0_ = 0.2e1 * t140 + 0.2e1 * t207 * t238 + t276 * t307 + r0 * (0.2e1 * t433 + 0.2e1 * t515 * t238 + 0.2e1 * t207 * (-0.53333333333333333333333333333333333333333333333333e0 * t210 * t384 * t213 + 0.21333333333333333333333333333333333333333333333334e0 * t209 * t101 * t522 - 0.42666666666666666666666666666666666666666666666667e0 * t218 * t522 + 0.17066666666666666666666666666666666666666666666667e0 * t217 * t114 * t528 - 0.256e0 * t225 * t528 + 0.51200000000000000000000000000000000000000000000000e-1 * t224 * t124 * t535 - 0.68266666666666666666666666666666666666666666666667e-1 * t232 * t535 + 0.27306666666666666666666666666666666666666666666668e-1 * t231 * t416 * t421 * t542) + (0.11073577833333333333333333333333333333333333333333e-2 * t8 * t446 * t256 + t244 / t552 * (-0.39359651450000000000000000000000000000000000000000e-1 * t559 - 0.18590345266666666666666666666666666666666666666667e-1 * t561 - 0.63666595250000000000000000000000000000000000000000e-2 * t565 - 0.51086658466666666666666666666666666666666666666667e-2 * t568) / t255 - 0.18311555036753159941307229983139571945136646663793e-3 * t261 * t5 * t557 * t316 * t271 - 0.58482233974552040708313425006184496242808878304904e0 * t261 * t263 / t580 * (-0.29149776500000000000000000000000000000000000000000e-1 * t559 - 0.10197214950000000000000000000000000000000000000000e-1 * t561 - 0.18581188275000000000000000000000000000000000000000e-2 * t565 - 0.27959805900000000000000000000000000000000000000000e-2 * t568) / t270 - 0.2e1 * t515) * t307 + t276 * (-0.16000000000000000000000000000000000000000000000000e-1 * t279 * t384 * t282 + 0.19200000000000000000000000000000000000000000000000e-3 * t278 * t101 * t599 - 0.38400000000000000000000000000000000000000000000000e-3 * t287 * t599 + 0.46080000000000000000000000000000000000000000000000e-5 * t286 * t114 * t605 - 0.6912e-5 * t294 * t605 + 0.41472000000000000000000000000000000000000000000000e-7 * t293 * t124 * t612 - 0.55296000000000000000000000000000000000000000000000e-7 * t301 * t612 + 0.66355200000000000000000000000000000000000000000000e-9 * t300 * t416 * t421 * t619))
  t649 = t11 / t19 / t116 / t104
  t658 = f.my_piecewise3(t4, 0, -0.3e1 / 0.64e2 * t13 * t20 * t82 * (0.4e-2 * t84 * t86 * t90 * t96 - 0.32e-4 * t85 * t110 + 0.64e-4 * t100 * s0 * t110 - 0.512e-6 * t102 * t120 + 0.768e-6 * t113 * t101 * t120 - 0.3072e-8 * t115 * t132 + 0.4096e-8 * t123 * t114 * t132 - 0.32768e-10 * t125 * t649 * t423))
  vsigma_0_ = r0 * (0.2e1 * t658 + 0.2e1 * t207 * (0.2e0 * t209 * t86 * t90 * t213 - 0.8e-1 * t210 * t221 + 0.16e0 * t217 * s0 * t221 - 0.64e-1 * t218 * t228 + 0.96e-1 * t224 * t101 * t228 - 0.192e-1 * t225 * t235 + 0.256e-1 * t231 * t114 * t235 - 0.1024e-1 * t232 * t649 * t542) + t276 * (0.6e-2 * t278 * t86 * t90 * t282 - 0.72e-4 * t279 * t290 + 0.144e-3 * t286 * s0 * t290 - 0.1728e-5 * t287 * t297 + 0.2592e-5 * t293 * t101 * t297 - 0.15552e-7 * t294 * t304 + 0.20736e-7 * t300 * t114 * t304 - 0.248832e-9 * t301 * t649 * t619))
  _b = lambda x: (jnp.asarray(x) + jnp.zeros_like(r0))
  vrho_0_ = _b(vrho_0_)
  vsigma_0_ = _b(vsigma_0_)
  res = {'vrho': vrho_0_, 'vsigma': vsigma_0_}
  return res

def unpol_fxc(p, r, s=None, l=None, tau=None):
  f = funcs(p)
  params = f.params
  r0, s0, l0, tau0 = r, s, l, tau
  
  r0 = r
  pol = pol_fxc(p, (r0/2, r0/2), (s/4 if s is not None else None, s/4 if s is not None else None, s/4 if s is not None else None), (None, None), (None, None))
  res = {}
  # Extract v2rho2 from polarized output
  v2rho2_pol = pol.get('v2rho2', None)
  if v2rho2_pol is not None:
    d11, d12, d22 = v2rho2_pol[..., 0], v2rho2_pol[..., 1], v2rho2_pol[..., 2]
    res['v2rho2'] = 0.25 * (d11 + 2*d12 + d22)
  # Extract v2rhosigma from polarized output
  v2rhosigma_pol = pol.get('v2rhosigma', None)
  if v2rhosigma_pol is not None:
    # Broadcast scalars to match array shape (Maple may emit some derivatives as scalar 0)
    d13 = jnp.asarray(v2rhosigma_pol[..., 0]) + jnp.zeros_like(r0)
    d14 = jnp.asarray(v2rhosigma_pol[..., 1]) + jnp.zeros_like(r0)
    d15 = jnp.asarray(v2rhosigma_pol[..., 2]) + jnp.zeros_like(r0)
    d23 = jnp.asarray(v2rhosigma_pol[..., 3]) + jnp.zeros_like(r0)
    d24 = jnp.asarray(v2rhosigma_pol[..., 4]) + jnp.zeros_like(r0)
    d25 = jnp.asarray(v2rhosigma_pol[..., 5]) + jnp.zeros_like(r0)
    res['v2rhosigma'] = (1/8) * (d13 + d14 + d15 + d23 + d24 + d25)
  # Extract v2sigma2 from polarized output
  v2sigma2_pol = pol.get('v2sigma2', None)
  if v2sigma2_pol is not None:
    # Broadcast scalars to match array shape
    d33 = jnp.asarray(v2sigma2_pol[..., 0]) + jnp.zeros_like(r0)
    d34 = jnp.asarray(v2sigma2_pol[..., 1]) + jnp.zeros_like(r0)
    d35 = jnp.asarray(v2sigma2_pol[..., 2]) + jnp.zeros_like(r0)
    d44 = jnp.asarray(v2sigma2_pol[..., 3]) + jnp.zeros_like(r0)
    d45 = jnp.asarray(v2sigma2_pol[..., 4]) + jnp.zeros_like(r0)
    d55 = jnp.asarray(v2sigma2_pol[..., 5]) + jnp.zeros_like(r0)
    res['v2sigma2'] = (1/16) * (d33 + 2*d34 + 2*d35 + d44 + 2*d45 + d55)
  return res

def unpol_kxc(p, r, s=None, l=None, tau=None):
  f = funcs(p)
  params = f.params
  r0, s0, l0, tau0 = r, s, l, tau

  t3 = 0.1e1 <= f.p.zeta_threshold
  t4 = r0 / 0.2e1 <= f.p.dens_threshold or t3
  t5 = 3 ** (0.1e1 / 0.3e1)
  t6 = 0.1e1 / jnp.pi
  t7 = t6 ** (0.1e1 / 0.3e1)
  t8 = t5 * t7
  t9 = 4 ** (0.1e1 / 0.3e1)
  t10 = t9 ** 2
  t11 = 2 ** (0.1e1 / 0.3e1)
  t13 = t8 * t10 * t11
  t14 = 0.2e1 <= f.p.zeta_threshold
  t15 = f.p.zeta_threshold ** (0.1e1 / 0.3e1)
  t16 = t15 * f.p.zeta_threshold
  t18 = f.my_piecewise3(t14, t16, 0.2e1 * t11)
  t19 = r0 ** (0.1e1 / 0.3e1)
  t20 = t19 ** 2
  t22 = 0.1e1 / t20 / r0
  t23 = t18 * t22
  t24 = 9 ** (0.1e1 / 0.3e1)
  t25 = t24 ** 2
  t26 = t7 ** 2
  t28 = t25 * t26 * f.p.cam_omega
  t29 = 0.1e1 / t19
  t31 = f.my_piecewise3(t14, t15, t11)
  t33 = t11 / t31
  t36 = t28 * t5 * t29 * t33 / 0.18e2
  t37 = 0.135e1 <= t36
  t38 = 0.135e1 < t36
  t39 = f.my_piecewise3(t38, t36, 0.135e1)
  t40 = t39 ** 2
  t43 = t40 ** 2
  t44 = 0.1e1 / t43
  t46 = t43 * t40
  t47 = 0.1e1 / t46
  t49 = t43 ** 2
  t50 = 0.1e1 / t49
  t53 = 0.1e1 / t49 / t40
  t56 = 0.1e1 / t49 / t43
  t59 = 0.1e1 / t49 / t46
  t61 = t49 ** 2
  t62 = 0.1e1 / t61
  t65 = f.my_piecewise3(t38, 0.135e1, t36)
  t66 = jnp.sqrt(jnp.pi)
  t67 = 0.1e1 / t65
  t69 = jnp.erf(t67 / 0.2e1)
  t71 = t65 ** 2
  t72 = 0.1e1 / t71
  t74 = jnp.exp(-t72 / 0.4e1)
  t75 = t74 - 0.1e1
  t78 = t74 - 0.3e1 / 0.2e1 - 0.2e1 * t71 * t75
  t81 = 0.2e1 * t65 * t78 + t66 * t69
  t85 = f.my_piecewise3(t37, 0.1e1 / t40 / 0.36e2 - t44 / 0.960e3 + t47 / 0.26880e5 - t50 / 0.829440e6 + t53 / 0.28385280e8 - t56 / 0.1073479680e10 + t59 / 0.44590694400e11 - t62 / 0.2021444812800e13, 0.1e1 - 0.8e1 / 0.3e1 * t65 * t81)
  t87 = params.c_x[1]
  t88 = t87 * s0
  t89 = t11 ** 2
  t90 = r0 ** 2
  t92 = 0.1e1 / t20 / t90
  t93 = t89 * t92
  t95 = s0 * t89 * t92
  t97 = 0.1e1 + 0.4e-2 * t95
  t98 = 0.1e1 / t97
  t102 = params.c_x[2]
  t103 = s0 ** 2
  t104 = t102 * t103
  t105 = t90 ** 2
  t106 = t105 * r0
  t109 = t11 / t19 / t106
  t110 = t97 ** 2
  t111 = 0.1e1 / t110
  t115 = params.c_x[3]
  t116 = t103 * s0
  t117 = t115 * t116
  t118 = t105 ** 2
  t119 = 0.1e1 / t118
  t120 = t110 * t97
  t121 = 0.1e1 / t120
  t125 = params.c_x[4]
  t126 = t103 ** 2
  t127 = t125 * t126
  t128 = t118 * t90
  t131 = t89 / t20 / t128
  t132 = t110 ** 2
  t133 = 0.1e1 / t132
  t137 = params.c_x[0] + 0.4e-2 * t88 * t93 * t98 + 0.32e-4 * t104 * t109 * t111 + 0.256e-6 * t117 * t119 * t121 + 0.1024e-8 * t127 * t131 * t133
  t138 = t85 * t137
  t142 = 0.1e1 / t20
  t143 = t18 * t142
  t144 = t40 * t39
  t145 = 0.1e1 / t144
  t147 = 0.1e1 / t19 / r0
  t151 = t28 * t5 * t147 * t33 / 0.54e2
  t152 = f.my_piecewise3(t38, -t151, 0)
  t155 = t43 * t39
  t156 = 0.1e1 / t155
  t159 = t43 * t144
  t160 = 0.1e1 / t159
  t164 = 0.1e1 / t49 / t39
  t168 = 0.1e1 / t49 / t144
  t172 = 0.1e1 / t49 / t155
  t176 = 0.1e1 / t49 / t159
  t180 = 0.1e1 / t61 / t39
  t184 = f.my_piecewise3(t38, 0, -t151)
  t186 = t74 * t72
  t190 = t71 * t65
  t191 = 0.1e1 / t190
  t195 = t65 * t75
  t200 = t191 * t184 * t74 / 0.2e1 - 0.4e1 * t195 * t184 - t67 * t184 * t74
  t203 = -t186 * t184 + 0.2e1 * t184 * t78 + 0.2e1 * t65 * t200
  t207 = f.my_piecewise3(t37, -t145 * t152 / 0.18e2 + t156 * t152 / 0.240e3 - t160 * t152 / 0.4480e4 + t164 * t152 / 0.103680e6 - t168 * t152 / 0.2838528e7 + t172 * t152 / 0.89456640e8 - t176 * t152 / 0.3185049600e10 + t180 * t152 / 0.126340300800e12, -0.8e1 / 0.3e1 * t184 * t81 - 0.8e1 / 0.3e1 * t65 * t203)
  t208 = t207 * t137
  t212 = t90 * r0
  t214 = 0.1e1 / t20 / t212
  t215 = t89 * t214
  t219 = t87 * t103
  t220 = t105 * t90
  t223 = t11 / t19 / t220
  t224 = t223 * t111
  t229 = t102 * t116
  t231 = 0.1e1 / t118 / r0
  t232 = t231 * t121
  t237 = t115 * t126
  t238 = t118 * t212
  t240 = 0.1e1 / t20 / t238
  t242 = t240 * t133 * t89
  t247 = t126 * s0
  t248 = t125 * t247
  t252 = t11 / t19 / t118 / t220
  t254 = 0.1e1 / t132 / t97
  t258 = -0.10666666666666666666666666666666666666666666666667e-1 * t88 * t215 * t98 + 0.85333333333333333333333333333333333333333333333336e-4 * t219 * t224 - 0.17066666666666666666666666666666666666666666666667e-3 * t104 * t224 + 0.13653333333333333333333333333333333333333333333334e-5 * t229 * t232 - 0.2048e-5 * t117 * t232 + 0.81920000000000000000000000000000000000000000000003e-8 * t237 * t242 - 0.10922666666666666666666666666666666666666666666667e-7 * t127 * t242 + 0.87381333333333333333333333333333333333333333333336e-10 * t248 * t252 * t254
  t259 = t85 * t258
  t263 = t18 * t19
  t264 = t152 ** 2
  t268 = 0.1e1 / t19 / t90
  t272 = 0.2e1 / 0.81e2 * t28 * t5 * t268 * t33
  t273 = f.my_piecewise3(t38, t272, 0)
  t301 = 0.1e1 / t61 / t40
  t306 = t44 * t264 / 0.6e1 - t145 * t273 / 0.18e2 - t47 * t264 / 0.48e2 + t156 * t273 / 0.240e3 + t50 * t264 / 0.640e3 - t160 * t273 / 0.4480e4 - t53 * t264 / 0.11520e5 + t164 * t273 / 0.103680e6 + t56 * t264 / 0.258048e6 - t168 * t273 / 0.2838528e7 - t59 * t264 / 0.6881280e7 + t172 * t273 / 0.89456640e8 + t62 * t264 / 0.212336640e9 - t176 * t273 / 0.3185049600e10 - t301 * t264 / 0.7431782400e10 + t180 * t273 / 0.126340300800e12
  t307 = f.my_piecewise3(t38, 0, t272)
  t312 = t71 ** 2
  t314 = 0.1e1 / t312 / t65
  t315 = t184 ** 2
  t319 = t74 * t191
  t327 = 0.1e1 / t312
  t335 = 0.1e1 / t312 / t71
  t347 = -0.2e1 * t327 * t315 * t74 + t191 * t307 * t74 / 0.2e1 + t335 * t315 * t74 / 0.4e1 - 0.4e1 * t315 * t75 - t72 * t315 * t74 - 0.4e1 * t195 * t307 - t67 * t307 * t74
  t350 = -t314 * t315 * t74 / 0.2e1 + 0.2e1 * t319 * t315 - t186 * t307 + 0.2e1 * t307 * t78 + 0.4e1 * t184 * t200 + 0.2e1 * t65 * t347
  t354 = f.my_piecewise3(t37, t306, -0.8e1 / 0.3e1 * t307 * t81 - 0.16e2 / 0.3e1 * t184 * t203 - 0.8e1 / 0.3e1 * t65 * t350)
  t355 = t354 * t137
  t359 = t207 * t258
  t365 = t89 / t20 / t105
  t369 = t105 * t212
  t372 = t11 / t19 / t369
  t373 = t372 * t111
  t376 = t87 * t116
  t377 = 0.1e1 / t128
  t378 = t377 * t121
  t385 = t102 * t126
  t388 = 0.1e1 / t20 / t118 / t105
  t390 = t388 * t133 * t89
  t397 = t115 * t247
  t400 = 0.1e1 / t19 / t118 / t369
  t402 = t400 * t254 * t11
  t409 = t126 * t103
  t410 = t125 * t409
  t411 = t118 ** 2
  t413 = 0.1e1 / t411 / t90
  t415 = 0.1e1 / t132 / t110
  t419 = 0.39111111111111111111111111111111111111111111111112e-1 * t88 * t365 * t98 - 0.76800000000000000000000000000000000000000000000003e-3 * t219 * t373 + 0.36408888888888888888888888888888888888888888888891e-5 * t376 * t378 + 0.10808888888888888888888888888888888888888888888889e-2 * t104 * t373 - 0.19569777777777777777777777777777777777777777777779e-4 * t229 * t378 + 0.43690666666666666666666666666666666666666666666670e-7 * t385 * t390 + 0.18432e-4 * t117 * t378 - 0.16110933333333333333333333333333333333333333333334e-6 * t237 * t390 + 0.69905066666666666666666666666666666666666666666671e-9 * t397 * t402 + 0.12743111111111111111111111111111111111111111111112e-6 * t127 * t390 - 0.21845333333333333333333333333333333333333333333334e-8 * t248 * t402 + 0.93206755555555555555555555555555555555555555555561e-11 * t410 * t413 * t415
  t420 = t85 * t419
  t425 = f.my_piecewise3(t4, 0, t13 * t23 * t138 / 0.96e2 - t13 * t143 * t208 / 0.32e2 - t13 * t143 * t259 / 0.32e2 - 0.3e1 / 0.64e2 * t13 * t263 * t355 - 0.3e1 / 0.32e2 * t13 * t263 * t359 - 0.3e1 / 0.64e2 * t13 * t263 * t420)
  t427 = f.my_piecewise3(t3, f.p.zeta_threshold, 1)
  t428 = t8 * t10
  t429 = t268 * t11
  t431 = f.my_piecewise3(t3, 0.1e1 / t15, 1)
  t434 = t428 * t29 * t11 * t431
  t435 = jnp.sqrt(t434)
  t438 = t434 ** 0.15e1
  t440 = t5 ** 2
  t441 = t440 * t26
  t442 = t441 * t9
  t444 = t431 ** 2
  t446 = t442 * t142 * t89 * t444
  t448 = 0.37978500000000000000000000000000000000000000000000e1 * t435 + 0.89690000000000000000000000000000000000000000000000e0 * t434 + 0.20477500000000000000000000000000000000000000000000e0 * t438 + 0.12323500000000000000000000000000000000000000000000e0 * t446
  t451 = 0.1e1 + 0.16081824322151104821330931780901225435013347914188e2 / t448
  t452 = jnp.log(t451)
  t453 = t431 * t452
  t456 = 0.14764770444444444444444444444444444444444444444444e-2 * t428 * t429 * t453
  t457 = t10 * t147
  t458 = t8 * t457
  t459 = t11 * t431
  t460 = t448 ** 2
  t461 = 0.1e1 / t460
  t464 = 0.1e1 / t435 * t5 * t7
  t465 = t457 * t459
  t466 = t464 * t465
  t468 = t147 * t11
  t469 = t468 * t431
  t470 = t428 * t469
  t472 = t434 ** 0.5e0
  t474 = t472 * t5 * t7
  t475 = t474 * t465
  t479 = t442 * t22 * t89 * t444
  t481 = -0.63297500000000000000000000000000000000000000000000e0 * t466 - 0.29896666666666666666666666666666666666666666666667e0 * t470 - 0.10238750000000000000000000000000000000000000000000e0 * t475 - 0.82156666666666666666666666666666666666666666666667e-1 * t479
  t483 = 0.1e1 / t451
  t485 = t459 * t461 * t481 * t483
  t487 = 0.35616666666666666666666666666666666666666666666666e-1 * t458 * t485
  t489 = 0.1e1 + 0.53425000000000000000000000000000000000000000000000e-1 * t434
  t491 = 0.1e1 / t460 / t448
  t492 = t489 * t491
  t493 = t481 ** 2
  t496 = 0.20000000000000000000000000000000000000000000000000e1 * t492 * t493 * t483
  t497 = t489 * t461
  t501 = 0.1e1 / t435 / t434 * t440 * t26
  t502 = t9 * t92
  t503 = t89 * t444
  t504 = t502 * t503
  t505 = t501 * t504
  t507 = t10 * t268
  t508 = t507 * t459
  t509 = t464 * t508
  t511 = t429 * t431
  t512 = t428 * t511
  t514 = t434 ** (-0.5e0)
  t516 = t514 * t440 * t26
  t517 = t516 * t504
  t519 = t474 * t508
  t522 = t442 * t93 * t444
  t524 = -0.42198333333333333333333333333333333333333333333333e0 * t505 + 0.84396666666666666666666666666666666666666666666666e0 * t509 + 0.39862222222222222222222222222222222222222222222223e0 * t512 + 0.68258333333333333333333333333333333333333333333333e-1 * t517 + 0.13651666666666666666666666666666666666666666666667e0 * t519 + 0.13692777777777777777777777777777777777777777777778e0 * t522
  t527 = 0.10000000000000000000000000000000000000000000000000e1 * t497 * t524 * t483
  t528 = t460 ** 2
  t529 = 0.1e1 / t528
  t530 = t489 * t529
  t531 = t451 ** 2
  t532 = 0.1e1 / t531
  t535 = 0.16081824322151104821330931780901225435013347914188e2 * t530 * t493 * t532
  t537 = f.my_piecewise3(0.0e0 <= f.p.zeta_threshold, t16, 0)
  t541 = 0.1e1 / (0.2e1 * t11 - 0.2e1)
  t542 = (t18 + t537 - 0.2e1) * t541
  t547 = 0.70594500000000000000000000000000000000000000000000e1 * t435 + 0.15494250000000000000000000000000000000000000000000e1 * t434 + 0.42077500000000000000000000000000000000000000000000e0 * t438 + 0.15629250000000000000000000000000000000000000000000e0 * t446
  t550 = 0.1e1 + 0.32164683177870697973624959794146027661627532968800e2 / t547
  t551 = jnp.log(t550)
  t552 = t431 * t551
  t556 = t547 ** 2
  t557 = 0.1e1 / t556
  t562 = -0.11765750000000000000000000000000000000000000000000e1 * t466 - 0.51647500000000000000000000000000000000000000000000e0 * t470 - 0.21038750000000000000000000000000000000000000000000e0 * t475 - 0.10419500000000000000000000000000000000000000000000e0 * t479
  t564 = 0.1e1 / t550
  t566 = t459 * t557 * t562 * t564
  t570 = 0.1e1 + 0.51370000000000000000000000000000000000000000000000e-1 * t434
  t572 = 0.1e1 / t556 / t547
  t573 = t570 * t572
  t574 = t562 ** 2
  t578 = t570 * t557
  t585 = -0.78438333333333333333333333333333333333333333333333e0 * t505 + 0.15687666666666666666666666666666666666666666666667e1 * t509 + 0.68863333333333333333333333333333333333333333333333e0 * t512 + 0.14025833333333333333333333333333333333333333333333e0 * t517 + 0.28051666666666666666666666666666666666666666666667e0 * t519 + 0.17365833333333333333333333333333333333333333333333e0 * t522
  t589 = t556 ** 2
  t590 = 0.1e1 / t589
  t591 = t570 * t590
  t592 = t550 ** 2
  t593 = 0.1e1 / t592
  t601 = 0.51785000000000000000000000000000000000000000000000e1 * t435 + 0.90577500000000000000000000000000000000000000000000e0 * t434 + 0.11003250000000000000000000000000000000000000000000e0 * t438 + 0.12417750000000000000000000000000000000000000000000e0 * t446
  t604 = 0.1e1 + 0.29608574643216675549239059631669331438384556167466e2 / t601
  t605 = jnp.log(t604)
  t606 = t431 * t605
  t610 = t601 ** 2
  t611 = 0.1e1 / t610
  t616 = -0.86308333333333333333333333333333333333333333333334e0 * t466 - 0.30192500000000000000000000000000000000000000000000e0 * t470 - 0.55016250000000000000000000000000000000000000000000e-1 * t475 - 0.82785000000000000000000000000000000000000000000000e-1 * t479
  t618 = 0.1e1 / t604
  t619 = t611 * t616 * t618
  t620 = t459 * t619
  t624 = 0.1e1 + 0.27812500000000000000000000000000000000000000000000e-1 * t434
  t626 = 0.1e1 / t610 / t601
  t627 = t624 * t626
  t628 = t616 ** 2
  t632 = t624 * t611
  t639 = -0.57538888888888888888888888888888888888888888888889e0 * t505 + 0.11507777777777777777777777777777777777777777777778e1 * t509 + 0.40256666666666666666666666666666666666666666666667e0 * t512 + 0.36677500000000000000000000000000000000000000000000e-1 * t517 + 0.73355000000000000000000000000000000000000000000000e-1 * t519 + 0.13797500000000000000000000000000000000000000000000e0 * t522
  t640 = t639 * t618
  t643 = t610 ** 2
  t644 = 0.1e1 / t643
  t645 = t624 * t644
  t646 = t604 ** 2
  t647 = 0.1e1 / t646
  t651 = -0.70981924444444444444444444444444444444444444444442e-3 * t428 * t429 * t552 - 0.34246666666666666666666666666666666666666666666666e-1 * t458 * t566 - 0.20000000000000000000000000000000000000000000000000e1 * t573 * t574 * t564 + 0.99999999999999999999999999999999999999999999999999e0 * t578 * t585 * t564 + 0.32164683177870697973624959794146027661627532968800e2 * t591 * t574 * t593 + t456 + t487 + t496 - t527 - t535 - 0.24415406715670879921742973310852762593515528885057e-3 * t428 * t429 * t606 - 0.10843580882781524214666447553230042011687479519034e-1 * t458 * t620 - 0.11696446794910408141662685001236899248561775660981e1 * t627 * t628 * t618 + 0.58482233974552040708313425006184496242808878304903e0 * t632 * t640 + 0.17315755899375863299672358916972966258900005419821e2 * t645 * t628 * t647
  t653 = t542 * t8
  t654 = t459 * t605
  t658 = t542 * t428
  t662 = t542 * t624
  t664 = t626 * t628 * t618
  t668 = t611 * t639 * t618
  t672 = t644 * t628 * t647
  t675 = -t456 - t487 - t496 + t527 + t535 + t542 * t651 + 0.24415406715670879921742973310852762593515528885057e-3 * t653 * t507 * t654 + 0.10843580882781524214666447553230042011687479519034e-1 * t658 * t469 * t619 + 0.11696446794910408141662685001236899248561775660981e1 * t662 * t664 - 0.58482233974552040708313425006184496242808878304903e0 * t662 * t668 - 0.17315755899375863299672358916972966258900005419821e2 * t662 * t672
  t678 = f.my_piecewise3(t4, 0, t427 * t675 / 0.2e1)
  t680 = params.c_ss[1]
  t681 = t680 * s0
  t683 = 0.1e1 + 0.2e0 * t95
  t684 = 0.1e1 / t683
  t688 = params.c_ss[2]
  t689 = t688 * t103
  t690 = t683 ** 2
  t691 = 0.1e1 / t690
  t695 = params.c_ss[3]
  t696 = t695 * t116
  t697 = t690 * t683
  t698 = 0.1e1 / t697
  t702 = params.c_ss[4]
  t703 = t702 * t126
  t704 = t690 ** 2
  t705 = 0.1e1 / t704
  t709 = params.c_ss[0] + 0.2e0 * t681 * t93 * t684 + 0.8e-1 * t689 * t109 * t691 + 0.32e-1 * t696 * t119 * t698 + 0.64e-2 * t703 * t131 * t705
  t714 = 0.11073577833333333333333333333333333333333333333333e-2 * t428 * t468 * t453
  t715 = t481 * t483
  t717 = 0.10000000000000000000000000000000000000000000000000e1 * t497 * t715
  t721 = t562 * t564
  t727 = t616 * t618
  t740 = f.my_piecewise3(t4, 0, t427 * (t714 + t717 + t542 * (0.53236443333333333333333333333333333333333333333332e-3 * t428 * t468 * t552 + 0.99999999999999999999999999999999999999999999999999e0 * t578 * t721 - t714 - t717 + 0.18311555036753159941307229983139571945136646663793e-3 * t428 * t468 * t606 + 0.58482233974552040708313425006184496242808878304903e0 * t632 * t727) - 0.18311555036753159941307229983139571945136646663793e-3 * t653 * t457 * t654 - 0.58482233974552040708313425006184496242808878304903e0 * t662 * t619) / 0.2e1)
  t744 = t680 * t103
  t745 = t223 * t691
  t750 = t688 * t116
  t751 = t231 * t698
  t756 = t695 * t126
  t758 = t240 * t705 * t89
  t763 = t702 * t247
  t765 = 0.1e1 / t704 / t683
  t769 = -0.53333333333333333333333333333333333333333333333333e0 * t681 * t215 * t684 + 0.21333333333333333333333333333333333333333333333334e0 * t744 * t745 - 0.42666666666666666666666666666666666666666666666667e0 * t689 * t745 + 0.17066666666666666666666666666666666666666666666667e0 * t750 * t751 - 0.256e0 * t696 * t751 + 0.51200000000000000000000000000000000000000000000000e-1 * t756 * t758 - 0.68266666666666666666666666666666666666666666666667e-1 * t703 * t758 + 0.27306666666666666666666666666666666666666666666668e-1 * t763 * t252 * t765
  t773 = 0.62182e-1 * t489 * t452
  t776 = t624 * t605
  t785 = f.my_piecewise3(t4, 0, t427 * (-t773 + t542 * (-0.31090e-1 * t570 * t551 + t773 - 0.19751789702565206228825776161588751761046270558698e-1 * t776) + 0.19751789702565206228825776161588751761046270558698e-1 * t542 * t776) / 0.2e1)
  t789 = t372 * t691
  t792 = t680 * t116
  t793 = t377 * t698
  t800 = t688 * t126
  t802 = t388 * t705 * t89
  t809 = t695 * t247
  t811 = t400 * t765 * t11
  t818 = t702 * t409
  t820 = 0.1e1 / t704 / t690
  t824 = 0.19555555555555555555555555555555555555555555555555e1 * t681 * t365 * t684 - 0.19200000000000000000000000000000000000000000000001e1 * t744 * t789 + 0.45511111111111111111111111111111111111111111111114e0 * t792 * t793 + 0.27022222222222222222222222222222222222222222222222e1 * t689 * t789 - 0.24462222222222222222222222222222222222222222222223e1 * t750 * t793 + 0.27306666666666666666666666666666666666666666666667e0 * t800 * t802 + 0.2304e1 * t696 * t793 - 0.10069333333333333333333333333333333333333333333333e1 * t756 * t802 + 0.21845333333333333333333333333333333333333333333334e0 * t809 * t811 + 0.79644444444444444444444444444444444444444444444445e0 * t703 * t802 - 0.68266666666666666666666666666666666666666666666669e0 * t763 * t811 + 0.14563555555555555555555555555555555555555555555557e0 * t818 * t413 * t820
  t828 = t8 * t10 * t29
  t829 = jnp.sqrt(t828)
  t832 = t828 ** 0.15e1
  t835 = t441 * t9 * t142
  t837 = 0.37978500000000000000000000000000000000000000000000e1 * t829 + 0.89690000000000000000000000000000000000000000000000e0 * t828 + 0.20477500000000000000000000000000000000000000000000e0 * t832 + 0.12323500000000000000000000000000000000000000000000e0 * t835
  t840 = 0.1e1 + 0.16081824322151104821330931780901225435013347914188e2 / t837
  t841 = jnp.log(t840)
  t845 = t837 ** 2
  t846 = 0.1e1 / t845
  t847 = t147 * t846
  t849 = 0.1e1 / t829 * t5
  t850 = t7 * t10
  t851 = t850 * t147
  t852 = t849 * t851
  t855 = t828 ** 0.5e0
  t856 = t855 * t5
  t857 = t856 * t851
  t860 = t441 * t9 * t22
  t862 = -0.63297500000000000000000000000000000000000000000000e0 * t852 - 0.29896666666666666666666666666666666666666666666667e0 * t458 - 0.10238750000000000000000000000000000000000000000000e0 * t857 - 0.82156666666666666666666666666666666666666666666667e-1 * t860
  t863 = 0.1e1 / t840
  t864 = t862 * t863
  t869 = 0.1e1 + 0.53425000000000000000000000000000000000000000000000e-1 * t828
  t871 = 0.1e1 / t845 / t837
  t872 = t869 * t871
  t873 = t862 ** 2
  t874 = t873 * t863
  t877 = t869 * t846
  t880 = 0.1e1 / t829 / t828 * t440
  t881 = t26 * t9
  t882 = t881 * t92
  t883 = t880 * t882
  t885 = t850 * t268
  t886 = t849 * t885
  t888 = t8 * t507
  t890 = t828 ** (-0.5e0)
  t891 = t890 * t440
  t892 = t891 * t882
  t894 = t856 * t885
  t896 = t441 * t502
  t898 = -0.42198333333333333333333333333333333333333333333333e0 * t883 + 0.84396666666666666666666666666666666666666666666666e0 * t886 + 0.39862222222222222222222222222222222222222222222223e0 * t888 + 0.68258333333333333333333333333333333333333333333333e-1 * t892 + 0.13651666666666666666666666666666666666666666666667e0 * t894 + 0.13692777777777777777777777777777777777777777777778e0 * t896
  t899 = t898 * t863
  t902 = t845 ** 2
  t903 = 0.1e1 / t902
  t904 = t869 * t903
  t905 = t840 ** 2
  t906 = 0.1e1 / t905
  t907 = t873 * t906
  t910 = f.my_piecewise3(t3, t16, 1)
  t913 = (0.2e1 * t910 - 0.2e1) * t541
  t914 = t913 * t5
  t919 = 0.51785000000000000000000000000000000000000000000000e1 * t829 + 0.90577500000000000000000000000000000000000000000000e0 * t828 + 0.11003250000000000000000000000000000000000000000000e0 * t832 + 0.12417750000000000000000000000000000000000000000000e0 * t835
  t922 = 0.1e1 + 0.29608574643216675549239059631669331438384556167466e2 / t919
  t923 = jnp.log(t922)
  t928 = t913 * t8
  t929 = t919 ** 2
  t930 = 0.1e1 / t929
  t935 = -0.86308333333333333333333333333333333333333333333334e0 * t852 - 0.30192500000000000000000000000000000000000000000000e0 * t458 - 0.55016250000000000000000000000000000000000000000000e-1 * t857 - 0.82785000000000000000000000000000000000000000000000e-1 * t860
  t937 = 0.1e1 / t922
  t938 = t930 * t935 * t937
  t943 = 0.1e1 + 0.27812500000000000000000000000000000000000000000000e-1 * t828
  t944 = t913 * t943
  t946 = 0.1e1 / t929 / t919
  t947 = t935 ** 2
  t949 = t946 * t947 * t937
  t958 = -0.57538888888888888888888888888888888888888888888889e0 * t883 + 0.11507777777777777777777777777777777777777777777778e1 * t886 + 0.40256666666666666666666666666666666666666666666667e0 * t888 + 0.36677500000000000000000000000000000000000000000000e-1 * t892 + 0.73355000000000000000000000000000000000000000000000e-1 * t894 + 0.13797500000000000000000000000000000000000000000000e0 * t896
  t960 = t930 * t958 * t937
  t963 = t929 ** 2
  t964 = 0.1e1 / t963
  t966 = t922 ** 2
  t967 = 0.1e1 / t966
  t968 = t964 * t947 * t967
  t972 = -0.14764770444444444444444444444444444444444444444444e-2 * t8 * t507 * t841 - 0.35616666666666666666666666666666666666666666666666e-1 * t428 * t847 * t864 - 0.20000000000000000000000000000000000000000000000000e1 * t872 * t874 + 0.10000000000000000000000000000000000000000000000000e1 * t877 * t899 + 0.16081824322151104821330931780901225435013347914188e2 * t904 * t907 + 0.24415406715670879921742973310852762593515528885057e-3 * t914 * t850 * t268 * t923 + 0.10843580882781524214666447553230042011687479519034e-1 * t928 * t457 * t938 + 0.11696446794910408141662685001236899248561775660981e1 * t944 * t949 - 0.58482233974552040708313425006184496242808878304903e0 * t944 * t960 - 0.17315755899375863299672358916972966258900005419821e2 * t944 * t968 - 0.2e1 * t678
  t974 = params.c_ab[1]
  t975 = t974 * s0
  t977 = 0.1e1 + 0.6e-2 * t95
  t978 = 0.1e1 / t977
  t982 = params.c_ab[2]
  t983 = t982 * t103
  t984 = t977 ** 2
  t985 = 0.1e1 / t984
  t989 = params.c_ab[3]
  t990 = t989 * t116
  t991 = t984 * t977
  t992 = 0.1e1 / t991
  t996 = params.c_ab[4]
  t997 = t996 * t126
  t998 = t984 ** 2
  t999 = 0.1e1 / t998
  t1003 = params.c_ab[0] + 0.6e-2 * t975 * t93 * t978 + 0.72e-4 * t983 * t109 * t985 + 0.864e-6 * t990 * t119 * t992 + 0.5184e-8 * t997 * t131 * t999
  t1018 = 0.11073577833333333333333333333333333333333333333333e-2 * t8 * t457 * t841 + 0.10000000000000000000000000000000000000000000000000e1 * t877 * t864 - 0.18311555036753159941307229983139571945136646663793e-3 * t914 * t850 * t147 * t923 - 0.58482233974552040708313425006184496242808878304903e0 * t944 * t938 - 0.2e1 * t740
  t1022 = t974 * t103
  t1023 = t223 * t985
  t1028 = t982 * t116
  t1029 = t231 * t992
  t1034 = t989 * t126
  t1036 = t240 * t999 * t89
  t1041 = t996 * t247
  t1043 = 0.1e1 / t998 / t977
  t1047 = -0.16000000000000000000000000000000000000000000000000e-1 * t975 * t215 * t978 + 0.19200000000000000000000000000000000000000000000000e-3 * t1022 * t1023 - 0.38400000000000000000000000000000000000000000000000e-3 * t983 * t1023 + 0.46080000000000000000000000000000000000000000000000e-5 * t1028 * t1029 - 0.6912e-5 * t990 * t1029 + 0.41472000000000000000000000000000000000000000000000e-7 * t1034 * t1036 - 0.55296000000000000000000000000000000000000000000000e-7 * t997 * t1036 + 0.66355200000000000000000000000000000000000000000000e-9 * t1041 * t252 * t1043
  t1056 = -0.62182e-1 * t869 * t841 + 0.19751789702565206228825776161588751761046270558698e-1 * t913 * t943 * t923 - 0.2e1 * t785
  t1060 = t372 * t985
  t1063 = t974 * t116
  t1064 = t377 * t992
  t1071 = t982 * t126
  t1073 = t388 * t999 * t89
  t1080 = t989 * t247
  t1082 = t400 * t1043 * t11
  t1089 = t996 * t409
  t1091 = 0.1e1 / t998 / t984
  t1095 = 0.58666666666666666666666666666666666666666666666667e-1 * t975 * t365 * t978 - 0.17280000000000000000000000000000000000000000000000e-2 * t1022 * t1060 + 0.12288000000000000000000000000000000000000000000000e-4 * t1063 * t1064 + 0.24320000000000000000000000000000000000000000000000e-2 * t983 * t1060 - 0.66048000000000000000000000000000000000000000000000e-4 * t1028 * t1064 + 0.22118400000000000000000000000000000000000000000000e-6 * t1071 * t1073 + 0.62208e-4 * t990 * t1064 - 0.81561600000000000000000000000000000000000000000000e-6 * t1034 * t1073 + 0.53084160000000000000000000000000000000000000000000e-8 * t1080 * t1082 + 0.64512000000000000000000000000000000000000000000000e-6 * t997 * t1073 - 0.16588800000000000000000000000000000000000000000000e-7 * t1041 * t1082 + 0.10616832000000000000000000000000000000000000000000e-9 * t1089 * t413 * t1091
  t1118 = 0.1e1 / t19 / t212
  t1122 = 0.14e2 / 0.243e3 * t28 * t5 * t1118 * t33
  t1123 = f.my_piecewise3(t38, -t1122, 0)
  t1140 = t264 * t152
  t1151 = -t145 * t1123 / 0.18e2 + t156 * t1123 / 0.240e3 - t160 * t1123 / 0.4480e4 + t164 * t1123 / 0.103680e6 - t168 * t1123 / 0.2838528e7 + t172 * t1123 / 0.89456640e8 - t176 * t1123 / 0.3185049600e10 + t180 * t1123 / 0.126340300800e12 - 0.2e1 / 0.3e1 * t156 * t1140 + t44 * t152 * t273 / 0.2e1 + t160 * t1140 / 0.8e1 - t47 * t152 * t273 / 0.16e2
  t1184 = -t164 * t1140 / 0.80e2 + 0.3e1 / 0.640e3 * t50 * t152 * t273 + t168 * t1140 / 0.1152e4 - t53 * t152 * t273 / 0.3840e4 - t172 * t1140 / 0.21504e5 + t56 * t152 * t273 / 0.86016e5 + t176 * t1140 / 0.491520e6 - t59 * t152 * t273 / 0.2293760e7 - t180 * t1140 / 0.13271040e8 + t62 * t152 * t273 / 0.70778880e8 + 0.1e1 / t61 / t144 * t1140 / 0.412876800e9 - t301 * t152 * t273 / 0.2477260800e10
  t1186 = f.my_piecewise3(t38, 0, -t1122)
  t1193 = t315 * t184
  t1198 = t74 * t307
  t1201 = t312 ** 2
  t1259 = f.my_piecewise3(t37, t1151 + t1184, -0.8e1 / 0.3e1 * t1186 * t81 - 0.8e1 * t307 * t203 - 0.8e1 * t184 * t350 - 0.8e1 / 0.3e1 * t65 * (0.7e1 / 0.2e1 * t335 * t1193 * t74 - 0.3e1 / 0.2e1 * t314 * t184 * t1198 - 0.1e1 / t1201 * t1193 * t74 / 0.4e1 - 0.6e1 * t74 * t327 * t1193 + 0.6e1 * t319 * t184 * t307 - t186 * t1186 + 0.2e1 * t1186 * t78 + 0.6e1 * t307 * t200 + 0.6e1 * t184 * t347 + 0.2e1 * t65 * (0.15e2 / 0.2e1 * t314 * t1193 * t74 - 0.6e1 * t327 * t184 * t1198 - 0.5e1 / 0.2e1 / t312 / t190 * t1193 * t74 + t191 * t1186 * t74 / 0.2e1 + 0.3e1 / 0.4e1 * t335 * t307 * t184 * t74 + 0.1e1 / t1201 / t65 * t1193 * t74 / 0.8e1 - 0.12e2 * t184 * t75 * t307 - 0.3e1 * t72 * t184 * t1198 - 0.4e1 * t195 * t1186 - t67 * t1186 * t74)))
  t1274 = t89 / t20 / t106
  t1280 = t11 / t19 / t118
  t1281 = t1280 * t111
  t1284 = 0.1e1 / t238
  t1285 = t1284 * t121
  t1291 = 0.1e1 / t20 / t118 / t106
  t1293 = t1291 * t133 * t89
  t1304 = 0.1e1 / t19 / t411
  t1306 = t1304 * t254 * t11
  t1317 = 0.1e1 / t411 / t212
  t1318 = t1317 * t415
  t1327 = t126 * t116
  t1331 = 0.1e1 / t20 / t411 / t106
  t1338 = -0.18251851851851851851851851851851851851851851851852e0 * t88 * t1274 * t98 + 0.64663703703703703703703703703703703703703703703706e-2 * t219 * t1281 - 0.69176888888888888888888888888888888888888888888893e-4 * t376 * t1285 + 0.11650844444444444444444444444444444444444444444445e-6 * t87 * t126 * t1293 - 0.79265185185185185185185185185185185185185185185186e-2 * t104 * t1281 + 0.24181570370370370370370370370370370370370370370372e-3 * t229 * t1285 - 0.11796480000000000000000000000000000000000000000001e-5 * t385 * t1293 + 0.37282702222222222222222222222222222222222222222226e-8 * t102 * t247 * t1306 - 0.184320e-3 * t117 * t1285 + 0.26305422222222222222222222222222222222222222222223e-5 * t237 * t1293 - 0.24466773333333333333333333333333333333333333333335e-7 * t397 * t1306 + 0.74565404444444444444444444444444444444444444444451e-10 * t115 * t409 * t1318 - 0.16141274074074074074074074074074074074074074074075e-5 * t127 * t1293 + 0.44370299259259259259259259259259259259259259259262e-7 * t248 * t1306 - 0.40078904888888888888888888888888888888888888888891e-9 * t410 * t1318 + 0.59652323555555555555555555555555555555555555555561e-12 * t125 * t1327 * t1331 / t132 / t120 * t89
  t1344 = f.my_piecewise3(t4, 0, -0.5e1 / 0.288e3 * t13 * t18 * t92 * t138 + t13 * t23 * t208 / 0.32e2 + t13 * t23 * t259 / 0.32e2 - 0.3e1 / 0.64e2 * t13 * t143 * t355 - 0.3e1 / 0.32e2 * t13 * t143 * t359 - 0.3e1 / 0.64e2 * t13 * t143 * t420 - 0.3e1 / 0.64e2 * t13 * t263 * t1259 * t137 - 0.9e1 / 0.64e2 * t13 * t263 * t354 * t258 - 0.9e1 / 0.64e2 * t13 * t263 * t207 * t419 - 0.3e1 / 0.64e2 * t13 * t263 * t85 * t1338)
  t1349 = t493 * t481
  t1354 = 0.51725014705706168413145063783413931475389495076352e3 * t489 / t528 / t460 * t1349 / t531 / t451
  t1360 = 0.96490945932906628927985590685407352610080087485128e2 * t489 / t528 / t448 * t1349 * t532
  t1365 = 0.1e1 / t105
  t1367 = t1365 * t444 * t431
  t1368 = 0.1e1 / t435 / t446 * t6 * t1367 / 0.4e1
  t1370 = t9 * t214
  t1371 = t1370 * t503
  t1372 = t501 * t1371
  t1374 = t10 * t1118
  t1375 = t1374 * t459
  t1376 = t464 * t1375
  t1378 = t1118 * t11
  t1380 = t428 * t1378 * t431
  t1382 = t434 ** (-0.15e1)
  t1384 = t1382 * t6 * t1367
  t1386 = t516 * t1371
  t1388 = t474 * t1375
  t1391 = t442 * t215 * t444
  t1396 = 0.10000000000000000000000000000000000000000000000000e1 * t497 * (-0.50638000000000000000000000000000000000000000000000e1 * t1368 + 0.16879333333333333333333333333333333333333333333333e1 * t1372 - 0.19692555555555555555555555555555555555555555555555e1 * t1376 - 0.93011851851851851851851851851851851851851851851854e0 * t1380 + 0.27303333333333333333333333333333333333333333333333e0 * t1384 - 0.27303333333333333333333333333333333333333333333333e0 * t1386 - 0.31853888888888888888888888888888888888888888888890e0 * t1388 - 0.36514074074074074074074074074074074074074074074075e0 * t1391) * t483
  t1407 = 0.10685000000000000000000000000000000000000000000000e0 * t458 * t459 * t491 * t493 * t483
  t1410 = 0.60000000000000000000000000000000000000000000000000e1 * t530 * t1349 * t483
  t1413 = 0.60000000000000000000000000000000000000000000000000e1 * t492 * t715 * t524
  t1423 = t1354 - t1360 + t1396 - 0.32530742648344572643999342659690126035062438557102e-1 * t658 * t469 * t664 - 0.56969282336565386484066937725323112718202900731800e-3 * t653 * t1374 * t654 + t1407 + t1410 - t1413 + 0.48159446095139119802213748237831062407565640073877e0 * t658 * t469 * t672 - 0.21687161765563048429332895106460084023374959038068e-1 * t658 * t511 * t619 + 0.16265371324172286321999671329845063017531219278551e-1 * t658 * t469 * t668
  t1426 = 0.34451131037037037037037037037037037037037037037036e-2 * t428 * t1378 * t453
  t1436 = t628 * t616
  t1442 = 0.1e1 / t643 / t610
  t1445 = 0.1e1 / t646 / t604
  t1450 = 0.1e1 / t643 / t601
  t1463 = -0.69046666666666666666666666666666666666666666666667e1 * t1368 + 0.23015555555555555555555555555555555555555555555556e1 * t1372 - 0.26851481481481481481481481481481481481481481481482e1 * t1376 - 0.93932222222222222222222222222222222222222222222223e0 * t1380 + 0.14671000000000000000000000000000000000000000000000e0 * t1384 - 0.14671000000000000000000000000000000000000000000000e0 * t1386 - 0.17116166666666666666666666666666666666666666666667e0 * t1388 - 0.36793333333333333333333333333333333333333333333333e0 * t1391
  t1472 = 0.85917146441092277507960503039464796886558811231548e0 * t458 * t459 * t529 * t493 * t532
  t1474 = 0.71233333333333333333333333333333333333333333333333e-1 * t888 * t485
  t1479 = 0.53424999999999999999999999999999999999999999999999e-1 * t458 * t459 * t461 * t524 * t483
  t1483 = 0.48245472966453314463992795342703676305040043742564e2 * t530 * t524 * t532 * t481
  t1494 = t574 * t562
  t1535 = -0.10389453539625517979803415350183779755340003251893e3 * t624 * t1450 * t1436 * t647 + 0.58482233974552040708313425006184496242808878304903e0 * t632 * t1463 * t618 + 0.20691336878655965245175271659148296983999699561788e4 * t570 / t589 / t556 * t1494 / t592 / t550 - 0.19298809906722418784174975876487616596976519781280e3 * t570 / t589 / t547 * t1494 * t593 + 0.99999999999999999999999999999999999999999999999999e0 * t578 * (-0.94126000000000000000000000000000000000000000000000e1 * t1368 + 0.31375333333333333333333333333333333333333333333334e1 * t1372 - 0.36604555555555555555555555555555555555555555555556e1 * t1376 - 0.16068111111111111111111111111111111111111111111111e1 * t1380 + 0.56103333333333333333333333333333333333333333333332e0 * t1384 - 0.56103333333333333333333333333333333333333333333332e0 * t1386 - 0.65453888888888888888888888888888888888888888888890e0 * t1388 - 0.46308888888888888888888888888888888888888888888888e0 * t1391) * t564 + 0.60000000000000000000000000000000000000000000000000e1 * t591 * t1494 * t564 + 0.35089340384731224424988055003710697745685326982943e1 * t645 * t1436 * t618 + 0.10253897021007794930818001372045340355835853271641e4 * t624 * t1442 * t1436 * t1445 - t1354 + t1360 - t1396 - t1410 + t1413 - t1483 + 0.96494049533612093920874879382438082984882598906400e2 * t591 * t585 * t593 * t562 - 0.35089340384731224424988055003710697745685326982943e1 * t627 * t727 * t639
  t1577 = 0.51947267698127589899017076750918898776700016259463e2 * t645 * t639 * t647 * t616 - 0.60000000000000000000000000000000000000000000000000e1 * t573 * t721 * t585 + 0.16562449037037037037037037037037037037037037037036e-2 * t428 * t1378 * t552 + 0.56969282336565386484066937725323112718202900731800e-3 * t428 * t1378 * t606 - t1407 + t1472 - t1474 + t1479 - 0.51369999999999999999999999999999999999999999999999e-1 * t458 * t459 * t557 * t585 * t564 + 0.32530742648344572643999342659690126035062438557102e-1 * t458 * t459 * t664 + 0.10274000000000000000000000000000000000000000000000e0 * t458 * t459 * t572 * t574 * t564 + 0.21687161765563048429332895106460084023374959038068e-1 * t888 * t620 - 0.16265371324172286321999671329845063017531219278551e-1 * t458 * t459 * t668 - 0.48159446095139119802213748237831062407565640073877e0 * t458 * t459 * t672 - 0.16522997748472177549051141846252814409778063686072e1 * t458 * t459 * t590 * t574 * t593 + 0.68493333333333333333333333333333333333333333333331e-1 * t888 * t566 - t1426
  t1580 = t1426 - 0.51947267698127589899017076750918898776700016259463e2 * t662 * t644 * t639 * t647 * t616 + 0.35089340384731224424988055003710697745685326982943e1 * t662 * t626 * t616 * t640 - 0.35089340384731224424988055003710697745685326982943e1 * t662 * t644 * t1436 * t618 - 0.10253897021007794930818001372045340355835853271641e4 * t662 * t1442 * t1436 * t1445 + 0.10389453539625517979803415350183779755340003251893e3 * t662 * t1450 * t1436 * t647 - 0.58482233974552040708313425006184496242808878304903e0 * t662 * t611 * t1463 * t618 - t1472 + t1474 - t1479 + t1483 + t542 * (t1535 + t1577)
  t1584 = f.my_piecewise3(t4, 0, t427 * (t1423 + t1580) / 0.2e1)
  t1594 = t1280 * t691
  t1597 = t1284 * t698
  t1602 = t1291 * t705 * t89
  t1613 = t1304 * t765 * t11
  t1623 = t1317 * t820
  t1639 = -0.91259259259259259259259259259259259259259259259257e1 * t681 * t1274 * t684 + 0.16165925925925925925925925925925925925925925925927e2 * t744 * t1594 - 0.86471111111111111111111111111111111111111111111117e1 * t792 * t1597 + 0.72817777777777777777777777777777777777777777777782e0 * t680 * t126 * t1602 - 0.19816296296296296296296296296296296296296296296296e2 * t689 * t1594 + 0.30226962962962962962962962962962962962962962962964e2 * t750 * t1597 - 0.73728000000000000000000000000000000000000000000002e1 * t800 * t1602 + 0.11650844444444444444444444444444444444444444444445e1 * t688 * t247 * t1613 - 0.23040e2 * t696 * t1597 + 0.16440888888888888888888888888888888888888888888889e2 * t756 * t1602 - 0.76458666666666666666666666666666666666666666666668e1 * t809 * t1613 + 0.11650844444444444444444444444444444444444444444445e1 * t695 * t409 * t1623 - 0.10088296296296296296296296296296296296296296296296e2 * t703 * t1602 + 0.13865718518518518518518518518518518518518518518519e2 * t763 * t1613 - 0.62623288888888888888888888888888888888888888888894e1 * t818 * t1623 + 0.46603377777777777777777777777777777777777777777782e0 * t702 * t1327 * t1331 / t704 / t697 * t89
  t1647 = t947 * t935
  t1664 = 0.1e1 / t829 / t835 * t6 * t1365 / 0.4e1
  t1666 = t881 * t214
  t1667 = t880 * t1666
  t1669 = t850 * t1118
  t1670 = t849 * t1669
  t1672 = t8 * t1374
  t1674 = t828 ** (-0.15e1)
  t1676 = t1674 * t6 * t1365
  t1678 = t891 * t1666
  t1680 = t856 * t1669
  t1682 = t441 * t1370
  t1718 = -0.32530742648344572643999342659690126035062438557102e-1 * t928 * t457 * t949 - 0.10253897021007794930818001372045340355835853271641e4 * t944 / t963 / t929 * t1647 / t966 / t922 + 0.10389453539625517979803415350183779755340003251893e3 * t944 / t963 / t919 * t1647 * t967 - 0.58482233974552040708313425006184496242808878304903e0 * t944 * t930 * (-0.34523333333333333333333333333333333333333333333333e1 * t1664 + 0.23015555555555555555555555555555555555555555555556e1 * t1667 - 0.26851481481481481481481481481481481481481481481482e1 * t1670 - 0.93932222222222222222222222222222222222222222222223e0 * t1672 + 0.73355000000000000000000000000000000000000000000000e-1 * t1676 - 0.14671000000000000000000000000000000000000000000000e0 * t1678 - 0.17116166666666666666666666666666666666666666666667e0 * t1680 - 0.36793333333333333333333333333333333333333333333333e0 * t1682) * t937 - 0.51947267698127589899017076750918898776700016259463e2 * t944 * t964 * t958 * t967 * t935 - 0.35089340384731224424988055003710697745685326982943e1 * t944 * t964 * t1647 * t937 + 0.35089340384731224424988055003710697745685326982943e1 * t944 * t946 * t935 * t937 * t958 - 0.85917146441092277507960503039464796886558811231548e0 * t428 * t147 * t903 * t907 + 0.71233333333333333333333333333333333333333333333333e-1 * t428 * t268 * t846 * t864 - 0.53424999999999999999999999999999999999999999999999e-1 * t428 * t847 * t899 - 0.56969282336565386484066937725323112718202900731800e-3 * t914 * t850 * t1118 * t923
  t1730 = t873 * t862
  t1773 = 0.10685000000000000000000000000000000000000000000000e0 * t428 * t147 * t871 * t874 - 0.2e1 * t1584 + 0.34451131037037037037037037037037037037037037037036e-2 * t8 * t1374 * t841 + 0.51725014705706168413145063783413931475389495076352e3 * t869 / t902 / t845 * t1730 / t905 / t840 - 0.96490945932906628927985590685407352610080087485128e2 * t869 / t902 / t837 * t1730 * t906 + 0.10000000000000000000000000000000000000000000000000e1 * t877 * (-0.25319000000000000000000000000000000000000000000000e1 * t1664 + 0.16879333333333333333333333333333333333333333333333e1 * t1667 - 0.19692555555555555555555555555555555555555555555555e1 * t1670 - 0.93011851851851851851851851851851851851851851851854e0 * t1672 + 0.13651666666666666666666666666666666666666666666667e0 * t1676 - 0.27303333333333333333333333333333333333333333333333e0 * t1678 - 0.31853888888888888888888888888888888888888888888890e0 * t1680 - 0.36514074074074074074074074074074074074074074074075e0 * t1682) * t863 + 0.48245472966453314463992795342703676305040043742564e2 * t904 * t898 * t906 * t862 + 0.60000000000000000000000000000000000000000000000000e1 * t904 * t1730 * t863 - 0.60000000000000000000000000000000000000000000000000e1 * t872 * t864 * t898 - 0.21687161765563048429332895106460084023374959038068e-1 * t928 * t507 * t938 + 0.16265371324172286321999671329845063017531219278551e-1 * t928 * t457 * t960 + 0.48159446095139119802213748237831062407565640073877e0 * t928 * t457 * t968
  t1783 = t1280 * t985
  t1786 = t1284 * t992
  t1791 = t1291 * t999 * t89
  t1802 = t1304 * t1043 * t11
  t1812 = t1317 * t1091
  t1828 = -0.27377777777777777777777777777777777777777777777778e0 * t975 * t1274 * t978 + 0.14549333333333333333333333333333333333333333333333e-1 * t1022 * t1783 - 0.23347200000000000000000000000000000000000000000000e-3 * t1063 * t1786 + 0.58982400000000000000000000000000000000000000000000e-6 * t974 * t126 * t1791 - 0.17834666666666666666666666666666666666666666666667e-1 * t983 * t1783 + 0.81612800000000000000000000000000000000000000000000e-3 * t1028 * t1786 - 0.59719680000000000000000000000000000000000000000000e-5 * t1071 * t1791 + 0.28311552000000000000000000000000000000000000000000e-7 * t982 * t247 * t1802 - 0.622080e-3 * t990 * t1786 + 0.13317120000000000000000000000000000000000000000000e-4 * t1034 * t1791 - 0.18579456000000000000000000000000000000000000000000e-6 * t1080 * t1802 + 0.84934656000000000000000000000000000000000000000000e-9 * t989 * t409 * t1812 - 0.81715200000000000000000000000000000000000000000000e-5 * t997 * t1791 + 0.33693696000000000000000000000000000000000000000000e-6 * t1041 * t1802 - 0.45652377600000000000000000000000000000000000000000e-8 * t1089 * t1812 + 0.10192158720000000000000000000000000000000000000000e-10 * t996 * t1327 * t1331 / t998 / t991 * t89
  v3rho3_0_ = 0.6e1 * t425 + 0.6e1 * t678 * t709 + 0.12e2 * t740 * t769 + 0.6e1 * t785 * t824 + 0.3e1 * t972 * t1003 + 0.6e1 * t1018 * t1047 + 0.3e1 * t1056 * t1095 + r0 * (0.2e1 * t1344 + 0.2e1 * t1584 * t709 + 0.6e1 * t678 * t769 + 0.6e1 * t740 * t824 + 0.2e1 * t785 * t1639 + (t1718 + t1773) * t1003 + 0.3e1 * t972 * t1047 + 0.3e1 * t1018 * t1095 + t1056 * t1828)

  res = {'v3rho3': v3rho3_0_}
  return res

def unpol_lxc(p, r, s=None, l=None, tau=None):
  f = funcs(p)
  params = f.params
  r0, s0, l0, tau0 = r, s, l, tau

  t3 = 0.1e1 <= f.p.zeta_threshold
  t4 = r0 / 0.2e1 <= f.p.dens_threshold or t3
  t5 = 3 ** (0.1e1 / 0.3e1)
  t6 = 0.1e1 / jnp.pi
  t7 = t6 ** (0.1e1 / 0.3e1)
  t8 = t5 * t7
  t9 = 4 ** (0.1e1 / 0.3e1)
  t10 = t9 ** 2
  t11 = 2 ** (0.1e1 / 0.3e1)
  t13 = t8 * t10 * t11
  t14 = 0.2e1 <= f.p.zeta_threshold
  t15 = f.p.zeta_threshold ** (0.1e1 / 0.3e1)
  t16 = t15 * f.p.zeta_threshold
  t18 = f.my_piecewise3(t14, t16, 0.2e1 * t11)
  t19 = r0 ** 2
  t20 = r0 ** (0.1e1 / 0.3e1)
  t21 = t20 ** 2
  t23 = 0.1e1 / t21 / t19
  t24 = t18 * t23
  t25 = 9 ** (0.1e1 / 0.3e1)
  t26 = t25 ** 2
  t27 = t7 ** 2
  t29 = t26 * t27 * f.p.cam_omega
  t30 = 0.1e1 / t20
  t32 = f.my_piecewise3(t14, t15, t11)
  t34 = t11 / t32
  t37 = t29 * t5 * t30 * t34 / 0.18e2
  t38 = 0.135e1 <= t37
  t39 = 0.135e1 < t37
  t40 = f.my_piecewise3(t39, t37, 0.135e1)
  t41 = t40 ** 2
  t44 = t41 ** 2
  t45 = 0.1e1 / t44
  t47 = t44 * t41
  t48 = 0.1e1 / t47
  t50 = t44 ** 2
  t51 = 0.1e1 / t50
  t54 = 0.1e1 / t50 / t41
  t57 = 0.1e1 / t50 / t44
  t60 = 0.1e1 / t50 / t47
  t62 = t50 ** 2
  t63 = 0.1e1 / t62
  t66 = f.my_piecewise3(t39, 0.135e1, t37)
  t67 = jnp.sqrt(jnp.pi)
  t68 = 0.1e1 / t66
  t70 = jnp.erf(t68 / 0.2e1)
  t72 = t66 ** 2
  t73 = 0.1e1 / t72
  t75 = jnp.exp(-t73 / 0.4e1)
  t76 = t75 - 0.1e1
  t79 = t75 - 0.3e1 / 0.2e1 - 0.2e1 * t72 * t76
  t82 = 0.2e1 * t66 * t79 + t67 * t70
  t86 = f.my_piecewise3(t38, 0.1e1 / t41 / 0.36e2 - t45 / 0.960e3 + t48 / 0.26880e5 - t51 / 0.829440e6 + t54 / 0.28385280e8 - t57 / 0.1073479680e10 + t60 / 0.44590694400e11 - t63 / 0.2021444812800e13, 0.1e1 - 0.8e1 / 0.3e1 * t66 * t82)
  t88 = params.c_x[1]
  t89 = t88 * s0
  t90 = t11 ** 2
  t91 = t90 * t23
  t93 = s0 * t90 * t23
  t95 = 0.1e1 + 0.4e-2 * t93
  t96 = 0.1e1 / t95
  t100 = params.c_x[2]
  t101 = s0 ** 2
  t102 = t100 * t101
  t103 = t19 ** 2
  t104 = t103 * r0
  t106 = 0.1e1 / t20 / t104
  t107 = t11 * t106
  t108 = t95 ** 2
  t109 = 0.1e1 / t108
  t113 = params.c_x[3]
  t114 = t101 * s0
  t115 = t113 * t114
  t116 = t103 ** 2
  t117 = 0.1e1 / t116
  t118 = t108 * t95
  t119 = 0.1e1 / t118
  t123 = params.c_x[4]
  t124 = t101 ** 2
  t125 = t123 * t124
  t126 = t116 * t19
  t129 = t90 / t21 / t126
  t130 = t108 ** 2
  t131 = 0.1e1 / t130
  t135 = params.c_x[0] + 0.4e-2 * t89 * t91 * t96 + 0.32e-4 * t102 * t107 * t109 + 0.256e-6 * t115 * t117 * t119 + 0.1024e-8 * t125 * t129 * t131
  t136 = t86 * t135
  t141 = 0.1e1 / t21 / r0
  t142 = t18 * t141
  t143 = t41 * t40
  t144 = 0.1e1 / t143
  t146 = 0.1e1 / t20 / r0
  t150 = t29 * t5 * t146 * t34 / 0.54e2
  t151 = f.my_piecewise3(t39, -t150, 0)
  t154 = t44 * t40
  t155 = 0.1e1 / t154
  t158 = t44 * t143
  t159 = 0.1e1 / t158
  t163 = 0.1e1 / t50 / t40
  t167 = 0.1e1 / t50 / t143
  t171 = 0.1e1 / t50 / t154
  t175 = 0.1e1 / t50 / t158
  t179 = 0.1e1 / t62 / t40
  t183 = f.my_piecewise3(t39, 0, -t150)
  t185 = t75 * t73
  t189 = t72 * t66
  t190 = 0.1e1 / t189
  t194 = t66 * t76
  t199 = t190 * t183 * t75 / 0.2e1 - 0.4e1 * t194 * t183 - t68 * t183 * t75
  t202 = -t185 * t183 + 0.2e1 * t183 * t79 + 0.2e1 * t66 * t199
  t206 = f.my_piecewise3(t38, -t144 * t151 / 0.18e2 + t155 * t151 / 0.240e3 - t159 * t151 / 0.4480e4 + t163 * t151 / 0.103680e6 - t167 * t151 / 0.2838528e7 + t171 * t151 / 0.89456640e8 - t175 * t151 / 0.3185049600e10 + t179 * t151 / 0.126340300800e12, -0.8e1 / 0.3e1 * t183 * t82 - 0.8e1 / 0.3e1 * t66 * t202)
  t207 = t206 * t135
  t211 = t19 * r0
  t213 = 0.1e1 / t21 / t211
  t214 = t90 * t213
  t218 = t88 * t101
  t219 = t103 * t19
  t222 = t11 / t20 / t219
  t223 = t222 * t109
  t228 = t100 * t114
  t229 = t116 * r0
  t230 = 0.1e1 / t229
  t231 = t230 * t119
  t236 = t113 * t124
  t237 = t116 * t211
  t239 = 0.1e1 / t21 / t237
  t241 = t239 * t131 * t90
  t246 = t124 * s0
  t247 = t123 * t246
  t248 = t116 * t219
  t251 = t11 / t20 / t248
  t253 = 0.1e1 / t130 / t95
  t257 = -0.10666666666666666666666666666666666666666666666667e-1 * t89 * t214 * t96 + 0.85333333333333333333333333333333333333333333333336e-4 * t218 * t223 - 0.17066666666666666666666666666666666666666666666667e-3 * t102 * t223 + 0.13653333333333333333333333333333333333333333333334e-5 * t228 * t231 - 0.2048e-5 * t115 * t231 + 0.81920000000000000000000000000000000000000000000003e-8 * t236 * t241 - 0.10922666666666666666666666666666666666666666666667e-7 * t125 * t241 + 0.87381333333333333333333333333333333333333333333336e-10 * t247 * t251 * t253
  t258 = t86 * t257
  t262 = 0.1e1 / t21
  t263 = t18 * t262
  t264 = t151 ** 2
  t268 = 0.1e1 / t20 / t19
  t272 = 0.2e1 / 0.81e2 * t29 * t5 * t268 * t34
  t273 = f.my_piecewise3(t39, t272, 0)
  t301 = 0.1e1 / t62 / t41
  t306 = t45 * t264 / 0.6e1 - t144 * t273 / 0.18e2 - t48 * t264 / 0.48e2 + t155 * t273 / 0.240e3 + t51 * t264 / 0.640e3 - t159 * t273 / 0.4480e4 - t54 * t264 / 0.11520e5 + t163 * t273 / 0.103680e6 + t57 * t264 / 0.258048e6 - t167 * t273 / 0.2838528e7 - t60 * t264 / 0.6881280e7 + t171 * t273 / 0.89456640e8 + t63 * t264 / 0.212336640e9 - t175 * t273 / 0.3185049600e10 - t301 * t264 / 0.7431782400e10 + t179 * t273 / 0.126340300800e12
  t307 = f.my_piecewise3(t39, 0, t272)
  t312 = t72 ** 2
  t314 = 0.1e1 / t312 / t66
  t315 = t183 ** 2
  t316 = t314 * t315
  t319 = t75 * t190
  t327 = 0.1e1 / t312
  t335 = 0.1e1 / t312 / t72
  t336 = t335 * t315
  t347 = -0.2e1 * t327 * t315 * t75 + t190 * t307 * t75 / 0.2e1 + t336 * t75 / 0.4e1 - 0.4e1 * t315 * t76 - t73 * t315 * t75 - 0.4e1 * t194 * t307 - t68 * t307 * t75
  t350 = -t316 * t75 / 0.2e1 + 0.2e1 * t319 * t315 - t185 * t307 + 0.2e1 * t307 * t79 + 0.4e1 * t183 * t199 + 0.2e1 * t66 * t347
  t354 = f.my_piecewise3(t38, t306, -0.8e1 / 0.3e1 * t307 * t82 - 0.16e2 / 0.3e1 * t183 * t202 - 0.8e1 / 0.3e1 * t66 * t350)
  t355 = t354 * t135
  t359 = t206 * t257
  t364 = 0.1e1 / t21 / t103
  t365 = t90 * t364
  t369 = t103 * t211
  t372 = t11 / t20 / t369
  t373 = t372 * t109
  t376 = t88 * t114
  t377 = 0.1e1 / t126
  t378 = t377 * t119
  t385 = t100 * t124
  t386 = t116 * t103
  t388 = 0.1e1 / t21 / t386
  t390 = t388 * t131 * t90
  t397 = t113 * t246
  t400 = 0.1e1 / t20 / t116 / t369
  t402 = t400 * t253 * t11
  t409 = t124 * t101
  t410 = t123 * t409
  t411 = t116 ** 2
  t413 = 0.1e1 / t411 / t19
  t415 = 0.1e1 / t130 / t108
  t419 = 0.39111111111111111111111111111111111111111111111112e-1 * t89 * t365 * t96 - 0.76800000000000000000000000000000000000000000000003e-3 * t218 * t373 + 0.36408888888888888888888888888888888888888888888891e-5 * t376 * t378 + 0.10808888888888888888888888888888888888888888888889e-2 * t102 * t373 - 0.19569777777777777777777777777777777777777777777779e-4 * t228 * t378 + 0.43690666666666666666666666666666666666666666666670e-7 * t385 * t390 + 0.18432e-4 * t115 * t378 - 0.16110933333333333333333333333333333333333333333334e-6 * t236 * t390 + 0.69905066666666666666666666666666666666666666666671e-9 * t397 * t402 + 0.12743111111111111111111111111111111111111111111112e-6 * t125 * t390 - 0.21845333333333333333333333333333333333333333333334e-8 * t247 * t402 + 0.93206755555555555555555555555555555555555555555561e-11 * t410 * t413 * t415
  t420 = t86 * t419
  t424 = t18 * t20
  t426 = 0.1e1 / t20 / t211
  t430 = 0.14e2 / 0.243e3 * t29 * t5 * t426 * t34
  t431 = f.my_piecewise3(t39, -t430, 0)
  t448 = t264 * t151
  t459 = -t167 * t431 / 0.2838528e7 + t171 * t431 / 0.89456640e8 - t175 * t431 / 0.3185049600e10 + t179 * t431 / 0.126340300800e12 - t144 * t431 / 0.18e2 + t155 * t431 / 0.240e3 - t159 * t431 / 0.4480e4 + t163 * t431 / 0.103680e6 - 0.2e1 / 0.3e1 * t155 * t448 + t45 * t151 * t273 / 0.2e1 + t159 * t448 / 0.8e1 - t48 * t151 * t273 / 0.16e2
  t486 = 0.1e1 / t62 / t143
  t492 = -t163 * t448 / 0.80e2 + 0.3e1 / 0.640e3 * t51 * t151 * t273 + t167 * t448 / 0.1152e4 - t54 * t151 * t273 / 0.3840e4 - t171 * t448 / 0.21504e5 + t57 * t151 * t273 / 0.86016e5 + t175 * t448 / 0.491520e6 - t60 * t151 * t273 / 0.2293760e7 - t179 * t448 / 0.13271040e8 + t63 * t151 * t273 / 0.70778880e8 + t486 * t448 / 0.412876800e9 - t301 * t151 * t273 / 0.2477260800e10
  t494 = f.my_piecewise3(t39, 0, -t430)
  t501 = t315 * t183
  t505 = t314 * t183
  t506 = t75 * t307
  t509 = t312 ** 2
  t510 = 0.1e1 / t509
  t514 = t75 * t327
  t530 = t327 * t183
  t534 = 0.1e1 / t312 / t189
  t542 = t183 * t75
  t546 = 0.1e1 / t509 / t66
  t550 = t183 * t76
  t553 = t73 * t183
  t560 = 0.15e2 / 0.2e1 * t314 * t501 * t75 - 0.6e1 * t530 * t506 - 0.5e1 / 0.2e1 * t534 * t501 * t75 + t190 * t494 * t75 / 0.2e1 + 0.3e1 / 0.4e1 * t335 * t307 * t542 + t546 * t501 * t75 / 0.8e1 - 0.12e2 * t550 * t307 - 0.3e1 * t553 * t506 - 0.4e1 * t194 * t494 - t68 * t494 * t75
  t563 = 0.7e1 / 0.2e1 * t335 * t501 * t75 - 0.3e1 / 0.2e1 * t505 * t506 - t510 * t501 * t75 / 0.4e1 - 0.6e1 * t514 * t501 + 0.6e1 * t319 * t183 * t307 - t185 * t494 + 0.2e1 * t494 * t79 + 0.6e1 * t307 * t199 + 0.6e1 * t183 * t347 + 0.2e1 * t66 * t560
  t567 = f.my_piecewise3(t38, t459 + t492, -0.8e1 / 0.3e1 * t494 * t82 - 0.8e1 * t307 * t202 - 0.8e1 * t183 * t350 - 0.8e1 / 0.3e1 * t66 * t563)
  t568 = t567 * t135
  t572 = t354 * t257
  t576 = t206 * t419
  t582 = t90 / t21 / t104
  t588 = t11 / t20 / t116
  t589 = t588 * t109
  t592 = 0.1e1 / t237
  t593 = t592 * t119
  t596 = t88 * t124
  t599 = 0.1e1 / t21 / t116 / t104
  t601 = t599 * t131 * t90
  t610 = t100 * t246
  t612 = 0.1e1 / t20 / t411
  t614 = t612 * t253 * t11
  t623 = t113 * t409
  t625 = 0.1e1 / t411 / t211
  t626 = t625 * t415
  t635 = t124 * t114
  t636 = t123 * t635
  t639 = 0.1e1 / t21 / t411 / t104
  t641 = 0.1e1 / t130 / t118
  t646 = -0.18251851851851851851851851851851851851851851851852e0 * t89 * t582 * t96 + 0.64663703703703703703703703703703703703703703703706e-2 * t218 * t589 - 0.69176888888888888888888888888888888888888888888893e-4 * t376 * t593 + 0.11650844444444444444444444444444444444444444444445e-6 * t596 * t601 - 0.79265185185185185185185185185185185185185185185186e-2 * t102 * t589 + 0.24181570370370370370370370370370370370370370370372e-3 * t228 * t593 - 0.11796480000000000000000000000000000000000000000001e-5 * t385 * t601 + 0.37282702222222222222222222222222222222222222222226e-8 * t610 * t614 - 0.184320e-3 * t115 * t593 + 0.26305422222222222222222222222222222222222222222223e-5 * t236 * t601 - 0.24466773333333333333333333333333333333333333333335e-7 * t397 * t614 + 0.74565404444444444444444444444444444444444444444451e-10 * t623 * t626 - 0.16141274074074074074074074074074074074074074074075e-5 * t125 * t601 + 0.44370299259259259259259259259259259259259259259262e-7 * t247 * t614 - 0.40078904888888888888888888888888888888888888888891e-9 * t410 * t626 + 0.59652323555555555555555555555555555555555555555561e-12 * t636 * t639 * t641 * t90
  t647 = t86 * t646
  t652 = f.my_piecewise3(t4, 0, -0.5e1 / 0.288e3 * t13 * t24 * t136 + t13 * t142 * t207 / 0.32e2 + t13 * t142 * t258 / 0.32e2 - 0.3e1 / 0.64e2 * t13 * t263 * t355 - 0.3e1 / 0.32e2 * t13 * t263 * t359 - 0.3e1 / 0.64e2 * t13 * t263 * t420 - 0.3e1 / 0.64e2 * t13 * t424 * t568 - 0.9e1 / 0.64e2 * t13 * t424 * t572 - 0.9e1 / 0.64e2 * t13 * t424 * t576 - 0.3e1 / 0.64e2 * t13 * t424 * t647)
  t654 = f.my_piecewise3(t3, f.p.zeta_threshold, 1)
  t655 = t8 * t10
  t658 = f.my_piecewise3(t3, 0.1e1 / t15, 1)
  t660 = t655 * t30 * t11 * t658
  t662 = 0.1e1 + 0.53425000000000000000000000000000000000000000000000e-1 * t660
  t663 = jnp.sqrt(t660)
  t666 = t660 ** 0.15e1
  t668 = t5 ** 2
  t669 = t668 * t27
  t670 = t669 * t9
  t672 = t658 ** 2
  t674 = t670 * t262 * t90 * t672
  t676 = 0.37978500000000000000000000000000000000000000000000e1 * t663 + 0.89690000000000000000000000000000000000000000000000e0 * t660 + 0.20477500000000000000000000000000000000000000000000e0 * t666 + 0.12323500000000000000000000000000000000000000000000e0 * t674
  t677 = t676 ** 2
  t678 = t677 ** 2
  t680 = 0.1e1 / t678 / t677
  t681 = t662 * t680
  t684 = 0.1e1 / t663 * t5 * t7
  t685 = t10 * t146
  t686 = t11 * t658
  t687 = t685 * t686
  t688 = t684 * t687
  t690 = t146 * t11
  t691 = t690 * t658
  t692 = t655 * t691
  t694 = t660 ** 0.5e0
  t696 = t694 * t5 * t7
  t697 = t696 * t687
  t701 = t670 * t141 * t90 * t672
  t703 = -0.63297500000000000000000000000000000000000000000000e0 * t688 - 0.29896666666666666666666666666666666666666666666667e0 * t692 - 0.10238750000000000000000000000000000000000000000000e0 * t697 - 0.82156666666666666666666666666666666666666666666667e-1 * t701
  t704 = t703 ** 2
  t705 = t704 * t703
  t708 = 0.1e1 + 0.16081824322151104821330931780901225435013347914188e2 / t676
  t709 = t708 ** 2
  t711 = 0.1e1 / t709 / t708
  t714 = 0.51725014705706168413145063783413931475389495076352e3 * t681 * t705 * t711
  t716 = 0.1e1 / t678 / t676
  t717 = t662 * t716
  t718 = 0.1e1 / t709
  t721 = 0.96490945932906628927985590685407352610080087485128e2 * t717 * t705 * t718
  t722 = 0.1e1 / t677
  t723 = t662 * t722
  t727 = 0.1e1 / t663 / t674 * t6 / 0.4e1
  t728 = 0.1e1 / t103
  t729 = t672 * t658
  t730 = t728 * t729
  t731 = t727 * t730
  t736 = 0.1e1 / t663 / t660 * t668 * t27
  t737 = t9 * t213
  t738 = t90 * t672
  t739 = t737 * t738
  t740 = t736 * t739
  t742 = t10 * t426
  t743 = t742 * t686
  t744 = t684 * t743
  t746 = t426 * t11
  t747 = t746 * t658
  t748 = t655 * t747
  t750 = t660 ** (-0.15e1)
  t751 = t750 * t6
  t752 = t751 * t730
  t754 = t660 ** (-0.5e0)
  t756 = t754 * t668 * t27
  t757 = t756 * t739
  t759 = t696 * t743
  t762 = t670 * t214 * t672
  t764 = -0.50638000000000000000000000000000000000000000000000e1 * t731 + 0.16879333333333333333333333333333333333333333333333e1 * t740 - 0.19692555555555555555555555555555555555555555555555e1 * t744 - 0.93011851851851851851851851851851851851851851851854e0 * t748 + 0.27303333333333333333333333333333333333333333333333e0 * t752 - 0.27303333333333333333333333333333333333333333333333e0 * t757 - 0.31853888888888888888888888888888888888888888888890e0 * t759 - 0.36514074074074074074074074074074074074074074074075e0 * t762
  t765 = 0.1e1 / t708
  t766 = t764 * t765
  t768 = 0.10000000000000000000000000000000000000000000000000e1 * t723 * t766
  t770 = f.my_piecewise3(0.0e0 <= f.p.zeta_threshold, t16, 0)
  t774 = 0.1e1 / (0.2e1 * t11 - 0.2e1)
  t775 = (t18 + t770 - 0.2e1) * t774
  t776 = t775 * t655
  t781 = 0.51785000000000000000000000000000000000000000000000e1 * t663 + 0.90577500000000000000000000000000000000000000000000e0 * t660 + 0.11003250000000000000000000000000000000000000000000e0 * t666 + 0.12417750000000000000000000000000000000000000000000e0 * t674
  t782 = t781 ** 2
  t783 = t782 * t781
  t784 = 0.1e1 / t783
  t789 = -0.86308333333333333333333333333333333333333333333334e0 * t688 - 0.30192500000000000000000000000000000000000000000000e0 * t692 - 0.55016250000000000000000000000000000000000000000000e-1 * t697 - 0.82785000000000000000000000000000000000000000000000e-1 * t701
  t790 = t789 ** 2
  t794 = 0.1e1 + 0.29608574643216675549239059631669331438384556167466e2 / t781
  t795 = 0.1e1 / t794
  t796 = t784 * t790 * t795
  t800 = t775 * t8
  t801 = jnp.log(t794)
  t802 = t686 * t801
  t806 = t8 * t685
  t807 = t677 * t676
  t808 = 0.1e1 / t807
  t811 = t686 * t808 * t704 * t765
  t813 = 0.10685000000000000000000000000000000000000000000000e0 * t806 * t811
  t814 = 0.1e1 / t678
  t815 = t662 * t814
  t818 = 0.60000000000000000000000000000000000000000000000000e1 * t815 * t705 * t765
  t819 = t662 * t808
  t820 = t703 * t765
  t821 = t9 * t23
  t822 = t821 * t738
  t823 = t736 * t822
  t825 = t10 * t268
  t826 = t825 * t686
  t827 = t684 * t826
  t829 = t268 * t11
  t830 = t829 * t658
  t831 = t655 * t830
  t833 = t756 * t822
  t835 = t696 * t826
  t838 = t670 * t91 * t672
  t840 = -0.42198333333333333333333333333333333333333333333333e0 * t823 + 0.84396666666666666666666666666666666666666666666666e0 * t827 + 0.39862222222222222222222222222222222222222222222223e0 * t831 + 0.68258333333333333333333333333333333333333333333333e-1 * t833 + 0.13651666666666666666666666666666666666666666666667e0 * t835 + 0.13692777777777777777777777777777777777777777777778e0 * t838
  t841 = t820 * t840
  t843 = 0.60000000000000000000000000000000000000000000000000e1 * t819 * t841
  t845 = t840 * t718 * t703
  t847 = 0.48245472966453314463992795342703676305040043742564e2 * t815 * t845
  t848 = t782 ** 2
  t849 = 0.1e1 / t848
  t850 = t849 * t790
  t851 = t794 ** 2
  t852 = 0.1e1 / t851
  t853 = t850 * t852
  t857 = 0.1e1 / t782
  t859 = t857 * t789 * t795
  t863 = t714 - t721 + t768 - 0.32530742648344572643999342659690126035062438557102e-1 * t776 * t691 * t796 - 0.56969282336565386484066937725323112718202900731800e-3 * t800 * t742 * t802 + t813 + t818 - t843 + t847 + 0.48159446095139119802213748237831062407565640073877e0 * t776 * t691 * t853 - 0.21687161765563048429332895106460084023374959038068e-1 * t776 * t830 * t859
  t870 = -0.57538888888888888888888888888888888888888888888889e0 * t823 + 0.11507777777777777777777777777777777777777777777778e1 * t827 + 0.40256666666666666666666666666666666666666666666667e0 * t831 + 0.36677500000000000000000000000000000000000000000000e-1 * t833 + 0.73355000000000000000000000000000000000000000000000e-1 * t835 + 0.13797500000000000000000000000000000000000000000000e0 * t838
  t872 = t857 * t870 * t795
  t876 = jnp.log(t708)
  t877 = t658 * t876
  t880 = 0.34451131037037037037037037037037037037037037037036e-2 * t655 * t746 * t877
  t882 = 0.1e1 + 0.27812500000000000000000000000000000000000000000000e-1 * t660
  t883 = t775 * t882
  t885 = t852 * t789
  t889 = t784 * t789
  t890 = t795 * t870
  t894 = t790 * t789
  t896 = t849 * t894 * t795
  t901 = t686 * t814 * t704 * t718
  t903 = 0.85917146441092277507960503039464796886558811231548e0 * t806 * t901
  t904 = t8 * t825
  t907 = t686 * t722 * t703 * t765
  t909 = 0.71233333333333333333333333333333333333333333333333e-1 * t904 * t907
  t912 = t686 * t722 * t840 * t765
  t914 = 0.53424999999999999999999999999999999999999999999999e-1 * t806 * t912
  t916 = 0.1e1 / t848 / t782
  t919 = 0.1e1 / t851 / t794
  t920 = t916 * t894 * t919
  t924 = 0.1e1 / t848 / t781
  t926 = t924 * t894 * t852
  t937 = -0.69046666666666666666666666666666666666666666666667e1 * t731 + 0.23015555555555555555555555555555555555555555555556e1 * t740 - 0.26851481481481481481481481481481481481481481481482e1 * t744 - 0.93932222222222222222222222222222222222222222222223e0 * t748 + 0.14671000000000000000000000000000000000000000000000e0 * t752 - 0.14671000000000000000000000000000000000000000000000e0 * t757 - 0.17116166666666666666666666666666666666666666666667e0 * t759 - 0.36793333333333333333333333333333333333333333333333e0 * t762
  t939 = t857 * t937 * t795
  t942 = t882 * t784
  t943 = t789 * t795
  t944 = t943 * t870
  t947 = t882 * t849
  t949 = t870 * t852 * t789
  t953 = 0.1e1 + 0.51370000000000000000000000000000000000000000000000e-1 * t660
  t958 = 0.70594500000000000000000000000000000000000000000000e1 * t663 + 0.15494250000000000000000000000000000000000000000000e1 * t660 + 0.42077500000000000000000000000000000000000000000000e0 * t666 + 0.15629250000000000000000000000000000000000000000000e0 * t674
  t959 = t958 ** 2
  t960 = t959 * t958
  t961 = 0.1e1 / t960
  t962 = t953 * t961
  t967 = -0.11765750000000000000000000000000000000000000000000e1 * t688 - 0.51647500000000000000000000000000000000000000000000e0 * t692 - 0.21038750000000000000000000000000000000000000000000e0 * t697 - 0.10419500000000000000000000000000000000000000000000e0 * t701
  t970 = 0.1e1 + 0.32164683177870697973624959794146027661627532968800e2 / t958
  t971 = 0.1e1 / t970
  t972 = t967 * t971
  t979 = -0.78438333333333333333333333333333333333333333333333e0 * t823 + 0.15687666666666666666666666666666666666666666666667e1 * t827 + 0.68863333333333333333333333333333333333333333333333e0 * t831 + 0.14025833333333333333333333333333333333333333333333e0 * t833 + 0.28051666666666666666666666666666666666666666666667e0 * t835 + 0.17365833333333333333333333333333333333333333333333e0 * t838
  t980 = t972 * t979
  t983 = t959 ** 2
  t984 = 0.1e1 / t983
  t985 = t953 * t984
  t986 = t970 ** 2
  t987 = 0.1e1 / t986
  t989 = t979 * t987 * t967
  t992 = t686 * t872
  t995 = t686 * t853
  t998 = t967 ** 2
  t1001 = t686 * t984 * t998 * t987
  t1004 = 0.1e1 / t959
  t1007 = t686 * t1004 * t967 * t971
  t1012 = t686 * t1004 * t979 * t971
  t1015 = -t880 - t813 + t903 - 0.35089340384731224424988055003710697745685326982943e1 * t942 * t944 + 0.51947267698127589899017076750918898776700016259463e2 * t947 * t949 - 0.60000000000000000000000000000000000000000000000000e1 * t962 * t980 + 0.96494049533612093920874879382438082984882598906400e2 * t985 * t989 + t843 - t847 - t909 + t914 - 0.16265371324172286321999671329845063017531219278551e-1 * t806 * t992 - 0.48159446095139119802213748237831062407565640073877e0 * t806 * t995 - 0.16522997748472177549051141846252814409778063686072e1 * t806 * t1001 + 0.68493333333333333333333333333333333333333333333331e-1 * t904 * t1007 - 0.51369999999999999999999999999999999999999999999999e-1 * t806 * t1012
  t1016 = t686 * t796
  t1021 = t686 * t961 * t998 * t971
  t1024 = t686 * t859
  t1027 = jnp.log(t970)
  t1028 = t658 * t1027
  t1032 = t658 * t801
  t1036 = t998 * t967
  t1043 = t882 * t916
  t1047 = t882 * t924
  t1051 = t882 * t857
  t1052 = t937 * t795
  t1056 = 0.1e1 / t983 / t959
  t1057 = t953 * t1056
  t1059 = 0.1e1 / t986 / t970
  t1064 = 0.1e1 / t983 / t958
  t1065 = t953 * t1064
  t1069 = t953 * t1004
  t1078 = -0.94126000000000000000000000000000000000000000000000e1 * t731 + 0.31375333333333333333333333333333333333333333333334e1 * t740 - 0.36604555555555555555555555555555555555555555555556e1 * t744 - 0.16068111111111111111111111111111111111111111111111e1 * t748 + 0.56103333333333333333333333333333333333333333333332e0 * t752 - 0.56103333333333333333333333333333333333333333333332e0 * t757 - 0.65453888888888888888888888888888888888888888888890e0 * t759 - 0.46308888888888888888888888888888888888888888888888e0 * t762
  t1079 = t1078 * t971
  t1082 = 0.32530742648344572643999342659690126035062438557102e-1 * t806 * t1016 + 0.10274000000000000000000000000000000000000000000000e0 * t806 * t1021 + 0.21687161765563048429332895106460084023374959038068e-1 * t904 * t1024 - t714 + t721 - t768 - t818 + 0.16562449037037037037037037037037037037037037037036e-2 * t655 * t746 * t1028 + 0.56969282336565386484066937725323112718202900731800e-3 * t655 * t746 * t1032 + 0.60000000000000000000000000000000000000000000000000e1 * t985 * t1036 * t971 + 0.35089340384731224424988055003710697745685326982943e1 * t947 * t894 * t795 + 0.10253897021007794930818001372045340355835853271641e4 * t1043 * t894 * t919 - 0.10389453539625517979803415350183779755340003251893e3 * t1047 * t894 * t852 + 0.58482233974552040708313425006184496242808878304903e0 * t1051 * t1052 + 0.20691336878655965245175271659148296983999699561788e4 * t1057 * t1036 * t1059 - 0.19298809906722418784174975876487616596976519781280e3 * t1065 * t1036 * t987 + 0.99999999999999999999999999999999999999999999999999e0 * t1069 * t1079
  t1085 = 0.16265371324172286321999671329845063017531219278551e-1 * t776 * t691 * t872 + t880 - 0.51947267698127589899017076750918898776700016259463e2 * t883 * t849 * t870 * t885 + 0.35089340384731224424988055003710697745685326982943e1 * t883 * t889 * t890 - 0.35089340384731224424988055003710697745685326982943e1 * t883 * t896 - t903 + t909 - t914 - 0.10253897021007794930818001372045340355835853271641e4 * t883 * t920 + 0.10389453539625517979803415350183779755340003251893e3 * t883 * t926 - 0.58482233974552040708313425006184496242808878304903e0 * t883 * t939 + t775 * (t1015 + t1082)
  t1089 = f.my_piecewise3(t4, 0, t654 * (t863 + t1085) / 0.2e1)
  t1091 = params.c_ss[1]
  t1092 = t1091 * s0
  t1094 = 0.1e1 + 0.2e0 * t93
  t1095 = 0.1e1 / t1094
  t1099 = params.c_ss[2]
  t1100 = t1099 * t101
  t1101 = t1094 ** 2
  t1102 = 0.1e1 / t1101
  t1106 = params.c_ss[3]
  t1107 = t1106 * t114
  t1108 = t1101 * t1094
  t1109 = 0.1e1 / t1108
  t1113 = params.c_ss[4]
  t1114 = t1113 * t124
  t1115 = t1101 ** 2
  t1116 = 0.1e1 / t1115
  t1120 = params.c_ss[0] + 0.2e0 * t1092 * t91 * t1095 + 0.8e-1 * t1100 * t107 * t1102 + 0.32e-1 * t1107 * t117 * t1109 + 0.64e-2 * t1114 * t129 * t1116
  t1125 = 0.14764770444444444444444444444444444444444444444444e-2 * t655 * t829 * t877
  t1127 = 0.35616666666666666666666666666666666666666666666666e-1 * t806 * t907
  t1128 = t704 * t765
  t1130 = 0.20000000000000000000000000000000000000000000000000e1 * t819 * t1128
  t1133 = 0.10000000000000000000000000000000000000000000000000e1 * t723 * t840 * t765
  t1134 = t704 * t718
  t1136 = 0.16081824322151104821330931780901225435013347914188e2 * t815 * t1134
  t1142 = t998 * t971
  t1148 = t998 * t987
  t1156 = t790 * t795
  t1161 = t790 * t852
  t1164 = -0.70981924444444444444444444444444444444444444444442e-3 * t655 * t829 * t1028 - 0.34246666666666666666666666666666666666666666666666e-1 * t806 * t1007 - 0.20000000000000000000000000000000000000000000000000e1 * t962 * t1142 + 0.99999999999999999999999999999999999999999999999999e0 * t1069 * t979 * t971 + 0.32164683177870697973624959794146027661627532968800e2 * t985 * t1148 + t1125 + t1127 + t1130 - t1133 - t1136 - 0.24415406715670879921742973310852762593515528885057e-3 * t655 * t829 * t1032 - 0.10843580882781524214666447553230042011687479519034e-1 * t806 * t1024 - 0.11696446794910408141662685001236899248561775660981e1 * t942 * t1156 + 0.58482233974552040708313425006184496242808878304903e0 * t1051 * t890 + 0.17315755899375863299672358916972966258900005419821e2 * t947 * t1161
  t1178 = -t1125 - t1127 - t1130 + t1133 + t1136 + t775 * t1164 + 0.24415406715670879921742973310852762593515528885057e-3 * t800 * t825 * t802 + 0.10843580882781524214666447553230042011687479519034e-1 * t776 * t691 * t859 + 0.11696446794910408141662685001236899248561775660981e1 * t883 * t796 - 0.58482233974552040708313425006184496242808878304903e0 * t883 * t872 - 0.17315755899375863299672358916972966258900005419821e2 * t883 * t853
  t1181 = f.my_piecewise3(t4, 0, t654 * t1178 / 0.2e1)
  t1185 = t1091 * t101
  t1186 = t222 * t1102
  t1191 = t1099 * t114
  t1192 = t230 * t1109
  t1197 = t1106 * t124
  t1199 = t239 * t1116 * t90
  t1204 = t1113 * t246
  t1206 = 0.1e1 / t1115 / t1094
  t1210 = -0.53333333333333333333333333333333333333333333333333e0 * t1092 * t214 * t1095 + 0.21333333333333333333333333333333333333333333333334e0 * t1185 * t1186 - 0.42666666666666666666666666666666666666666666666667e0 * t1100 * t1186 + 0.17066666666666666666666666666666666666666666666667e0 * t1191 * t1192 - 0.256e0 * t1107 * t1192 + 0.51200000000000000000000000000000000000000000000000e-1 * t1197 * t1199 - 0.68266666666666666666666666666666666666666666666667e-1 * t1114 * t1199 + 0.27306666666666666666666666666666666666666666666668e-1 * t1204 * t251 * t1206
  t1215 = 0.11073577833333333333333333333333333333333333333333e-2 * t655 * t690 * t877
  t1217 = 0.10000000000000000000000000000000000000000000000000e1 * t723 * t820
  t1238 = f.my_piecewise3(t4, 0, t654 * (t1215 + t1217 + t775 * (0.53236443333333333333333333333333333333333333333332e-3 * t655 * t690 * t1028 + 0.99999999999999999999999999999999999999999999999999e0 * t1069 * t972 - t1215 - t1217 + 0.18311555036753159941307229983139571945136646663793e-3 * t655 * t690 * t1032 + 0.58482233974552040708313425006184496242808878304903e0 * t1051 * t943) - 0.18311555036753159941307229983139571945136646663793e-3 * t800 * t685 * t802 - 0.58482233974552040708313425006184496242808878304903e0 * t883 * t859) / 0.2e1)
  t1242 = t372 * t1102
  t1245 = t1091 * t114
  t1246 = t377 * t1109
  t1253 = t1099 * t124
  t1255 = t388 * t1116 * t90
  t1262 = t1106 * t246
  t1264 = t400 * t1206 * t11
  t1271 = t1113 * t409
  t1273 = 0.1e1 / t1115 / t1101
  t1277 = 0.19555555555555555555555555555555555555555555555555e1 * t1092 * t365 * t1095 - 0.19200000000000000000000000000000000000000000000001e1 * t1185 * t1242 + 0.45511111111111111111111111111111111111111111111114e0 * t1245 * t1246 + 0.27022222222222222222222222222222222222222222222222e1 * t1100 * t1242 - 0.24462222222222222222222222222222222222222222222223e1 * t1191 * t1246 + 0.27306666666666666666666666666666666666666666666667e0 * t1253 * t1255 + 0.2304e1 * t1107 * t1246 - 0.10069333333333333333333333333333333333333333333333e1 * t1197 * t1255 + 0.21845333333333333333333333333333333333333333333334e0 * t1262 * t1264 + 0.79644444444444444444444444444444444444444444444445e0 * t1114 * t1255 - 0.68266666666666666666666666666666666666666666666669e0 * t1204 * t1264 + 0.14563555555555555555555555555555555555555555555557e0 * t1271 * t413 * t1273
  t1281 = 0.62182e-1 * t662 * t876
  t1284 = t882 * t801
  t1293 = f.my_piecewise3(t4, 0, t654 * (-t1281 + t775 * (-0.31090e-1 * t953 * t1027 + t1281 - 0.19751789702565206228825776161588751761046270558698e-1 * t1284) + 0.19751789702565206228825776161588751761046270558698e-1 * t775 * t1284) / 0.2e1)
  t1297 = t588 * t1102
  t1300 = t592 * t1109
  t1303 = t1091 * t124
  t1305 = t599 * t1116 * t90
  t1314 = t1099 * t246
  t1316 = t612 * t1206 * t11
  t1325 = t1106 * t409
  t1326 = t625 * t1273
  t1335 = t1113 * t635
  t1337 = 0.1e1 / t1115 / t1108
  t1342 = -0.91259259259259259259259259259259259259259259259257e1 * t1092 * t582 * t1095 + 0.16165925925925925925925925925925925925925925925927e2 * t1185 * t1297 - 0.86471111111111111111111111111111111111111111111117e1 * t1245 * t1300 + 0.72817777777777777777777777777777777777777777777782e0 * t1303 * t1305 - 0.19816296296296296296296296296296296296296296296296e2 * t1100 * t1297 + 0.30226962962962962962962962962962962962962962962964e2 * t1191 * t1300 - 0.73728000000000000000000000000000000000000000000002e1 * t1253 * t1305 + 0.11650844444444444444444444444444444444444444444445e1 * t1314 * t1316 - 0.23040e2 * t1107 * t1300 + 0.16440888888888888888888888888888888888888888888889e2 * t1197 * t1305 - 0.76458666666666666666666666666666666666666666666668e1 * t1262 * t1316 + 0.11650844444444444444444444444444444444444444444445e1 * t1325 * t1326 - 0.10088296296296296296296296296296296296296296296296e2 * t1114 * t1305 + 0.13865718518518518518518518518518518518518518518519e2 * t1204 * t1316 - 0.62623288888888888888888888888888888888888888888894e1 * t1271 * t1326 + 0.46603377777777777777777777777777777777777777777782e0 * t1335 * t639 * t1337 * t90
  t1345 = f.my_piecewise3(t3, t16, 1)
  t1348 = (0.2e1 * t1345 - 0.2e1) * t774
  t1349 = t1348 * t8
  t1351 = t8 * t10 * t30
  t1352 = jnp.sqrt(t1351)
  t1355 = t1351 ** 0.15e1
  t1358 = t669 * t9 * t262
  t1360 = 0.51785000000000000000000000000000000000000000000000e1 * t1352 + 0.90577500000000000000000000000000000000000000000000e0 * t1351 + 0.11003250000000000000000000000000000000000000000000e0 * t1355 + 0.12417750000000000000000000000000000000000000000000e0 * t1358
  t1361 = t1360 ** 2
  t1362 = t1361 * t1360
  t1363 = 0.1e1 / t1362
  t1365 = 0.1e1 / t1352 * t5
  t1366 = t7 * t10
  t1367 = t1366 * t146
  t1368 = t1365 * t1367
  t1371 = t1351 ** 0.5e0
  t1372 = t1371 * t5
  t1373 = t1372 * t1367
  t1376 = t669 * t9 * t141
  t1378 = -0.86308333333333333333333333333333333333333333333334e0 * t1368 - 0.30192500000000000000000000000000000000000000000000e0 * t806 - 0.55016250000000000000000000000000000000000000000000e-1 * t1373 - 0.82785000000000000000000000000000000000000000000000e-1 * t1376
  t1379 = t1378 ** 2
  t1383 = 0.1e1 + 0.29608574643216675549239059631669331438384556167466e2 / t1360
  t1384 = 0.1e1 / t1383
  t1385 = t1363 * t1379 * t1384
  t1390 = 0.1e1 + 0.53425000000000000000000000000000000000000000000000e-1 * t1351
  t1395 = 0.37978500000000000000000000000000000000000000000000e1 * t1352 + 0.89690000000000000000000000000000000000000000000000e0 * t1351 + 0.20477500000000000000000000000000000000000000000000e0 * t1355 + 0.12323500000000000000000000000000000000000000000000e0 * t1358
  t1396 = t1395 ** 2
  t1397 = t1396 ** 2
  t1398 = 0.1e1 / t1397
  t1399 = t1390 * t1398
  t1402 = 0.1e1 / t1352 / t1351 * t668
  t1403 = t27 * t9
  t1404 = t1403 * t23
  t1405 = t1402 * t1404
  t1407 = t1366 * t268
  t1408 = t1365 * t1407
  t1411 = t1351 ** (-0.5e0)
  t1412 = t1411 * t668
  t1413 = t1412 * t1404
  t1415 = t1372 * t1407
  t1417 = t669 * t821
  t1419 = -0.42198333333333333333333333333333333333333333333333e0 * t1405 + 0.84396666666666666666666666666666666666666666666666e0 * t1408 + 0.39862222222222222222222222222222222222222222222223e0 * t904 + 0.68258333333333333333333333333333333333333333333333e-1 * t1413 + 0.13651666666666666666666666666666666666666666666667e0 * t1415 + 0.13692777777777777777777777777777777777777777777778e0 * t1417
  t1422 = 0.1e1 + 0.16081824322151104821330931780901225435013347914188e2 / t1395
  t1423 = t1422 ** 2
  t1424 = 0.1e1 / t1423
  t1425 = t1419 * t1424
  t1430 = -0.63297500000000000000000000000000000000000000000000e0 * t1368 - 0.29896666666666666666666666666666666666666666666667e0 * t806 - 0.10238750000000000000000000000000000000000000000000e0 * t1373 - 0.82156666666666666666666666666666666666666666666667e-1 * t1376
  t1434 = t1396 * t1395
  t1435 = 0.1e1 / t1434
  t1436 = t1390 * t1435
  t1437 = 0.1e1 / t1422
  t1438 = t1430 * t1437
  t1442 = t1430 ** 2
  t1443 = t1442 * t1430
  t1444 = t1443 * t1437
  t1447 = 0.1e1 / t1361
  t1449 = t1447 * t1378 * t1384
  t1459 = -0.57538888888888888888888888888888888888888888888889e0 * t1405 + 0.11507777777777777777777777777777777777777777777778e1 * t1408 + 0.40256666666666666666666666666666666666666666666667e0 * t904 + 0.36677500000000000000000000000000000000000000000000e-1 * t1413 + 0.73355000000000000000000000000000000000000000000000e-1 * t1415 + 0.13797500000000000000000000000000000000000000000000e0 * t1417
  t1461 = t1447 * t1459 * t1384
  t1465 = t1361 ** 2
  t1466 = 0.1e1 / t1465
  t1467 = t1466 * t1379
  t1468 = t1383 ** 2
  t1469 = 0.1e1 / t1468
  t1470 = t1467 * t1469
  t1475 = 0.1e1 + 0.27812500000000000000000000000000000000000000000000e-1 * t1351
  t1476 = t1348 * t1475
  t1478 = 0.1e1 / t1465 / t1361
  t1479 = t1379 * t1378
  t1482 = 0.1e1 / t1468 / t1383
  t1483 = t1478 * t1479 * t1482
  t1487 = 0.1e1 / t1465 / t1360
  t1489 = t1487 * t1479 * t1469
  t1495 = 0.1e1 / t1352 / t1358 * t6 / 0.4e1
  t1496 = t1495 * t728
  t1498 = t1403 * t213
  t1499 = t1402 * t1498
  t1501 = t1366 * t426
  t1502 = t1365 * t1501
  t1504 = t8 * t742
  t1506 = t1351 ** (-0.15e1)
  t1507 = t1506 * t6
  t1508 = t1507 * t728
  t1510 = t1412 * t1498
  t1512 = t1372 * t1501
  t1514 = t669 * t737
  t1516 = -0.34523333333333333333333333333333333333333333333333e1 * t1496 + 0.23015555555555555555555555555555555555555555555556e1 * t1499 - 0.26851481481481481481481481481481481481481481481482e1 * t1502 - 0.93932222222222222222222222222222222222222222222223e0 * t1504 + 0.73355000000000000000000000000000000000000000000000e-1 * t1508 - 0.14671000000000000000000000000000000000000000000000e0 * t1510 - 0.17116166666666666666666666666666666666666666666667e0 * t1512 - 0.36793333333333333333333333333333333333333333333333e0 * t1514
  t1518 = t1447 * t1516 * t1384
  t1522 = t1469 * t1378
  t1526 = -0.32530742648344572643999342659690126035062438557102e-1 * t1349 * t685 * t1385 + 0.48245472966453314463992795342703676305040043742564e2 * t1399 * t1425 * t1430 - 0.60000000000000000000000000000000000000000000000000e1 * t1436 * t1438 * t1419 + 0.60000000000000000000000000000000000000000000000000e1 * t1399 * t1444 - 0.21687161765563048429332895106460084023374959038068e-1 * t1349 * t825 * t1449 + 0.16265371324172286321999671329845063017531219278551e-1 * t1349 * t685 * t1461 + 0.48159446095139119802213748237831062407565640073877e0 * t1349 * t685 * t1470 - 0.10253897021007794930818001372045340355835853271641e4 * t1476 * t1483 + 0.10389453539625517979803415350183779755340003251893e3 * t1476 * t1489 - 0.58482233974552040708313425006184496242808878304903e0 * t1476 * t1518 - 0.51947267698127589899017076750918898776700016259463e2 * t1476 * t1466 * t1459 * t1522
  t1528 = t1466 * t1479 * t1384
  t1532 = t1384 * t1459
  t1536 = t146 * t1398
  t1537 = t1442 * t1424
  t1541 = 0.1e1 / t1396
  t1542 = t268 * t1541
  t1546 = t146 * t1541
  t1547 = t1419 * t1437
  t1552 = t1348 * t5
  t1553 = jnp.log(t1383)
  t1559 = t1442 * t1437
  t1563 = jnp.log(t1422)
  t1568 = 0.1e1 / t1397 / t1396
  t1569 = t1390 * t1568
  t1571 = 0.1e1 / t1423 / t1422
  t1572 = t1443 * t1571
  t1576 = 0.1e1 / t1397 / t1395
  t1577 = t1390 * t1576
  t1578 = t1443 * t1424
  t1581 = t1390 * t1541
  t1590 = -0.25319000000000000000000000000000000000000000000000e1 * t1496 + 0.16879333333333333333333333333333333333333333333333e1 * t1499 - 0.19692555555555555555555555555555555555555555555555e1 * t1502 - 0.93011851851851851851851851851851851851851851851854e0 * t1504 + 0.13651666666666666666666666666666666666666666666667e0 * t1508 - 0.27303333333333333333333333333333333333333333333333e0 * t1510 - 0.31853888888888888888888888888888888888888888888890e0 * t1512 - 0.36514074074074074074074074074074074074074074074075e0 * t1514
  t1591 = t1590 * t1437
  t1594 = -0.35089340384731224424988055003710697745685326982943e1 * t1476 * t1528 + 0.35089340384731224424988055003710697745685326982943e1 * t1476 * t1363 * t1378 * t1532 - 0.85917146441092277507960503039464796886558811231548e0 * t655 * t1536 * t1537 + 0.71233333333333333333333333333333333333333333333333e-1 * t655 * t1542 * t1438 - 0.53424999999999999999999999999999999999999999999999e-1 * t655 * t1546 * t1547 - 0.2e1 * t1089 - 0.56969282336565386484066937725323112718202900731800e-3 * t1552 * t1366 * t426 * t1553 + 0.10685000000000000000000000000000000000000000000000e0 * t655 * t146 * t1435 * t1559 + 0.34451131037037037037037037037037037037037037037036e-2 * t8 * t742 * t1563 + 0.51725014705706168413145063783413931475389495076352e3 * t1569 * t1572 - 0.96490945932906628927985590685407352610080087485128e2 * t1577 * t1578 + 0.10000000000000000000000000000000000000000000000000e1 * t1581 * t1591
  t1595 = t1526 + t1594
  t1597 = params.c_ab[1]
  t1598 = t1597 * s0
  t1600 = 0.1e1 + 0.6e-2 * t93
  t1601 = 0.1e1 / t1600
  t1605 = params.c_ab[2]
  t1606 = t1605 * t101
  t1607 = t1600 ** 2
  t1608 = 0.1e1 / t1607
  t1612 = params.c_ab[3]
  t1613 = t1612 * t114
  t1614 = t1607 * t1600
  t1615 = 0.1e1 / t1614
  t1619 = params.c_ab[4]
  t1620 = t1619 * t124
  t1621 = t1607 ** 2
  t1622 = 0.1e1 / t1621
  t1626 = params.c_ab[0] + 0.6e-2 * t1598 * t91 * t1601 + 0.72e-4 * t1606 * t107 * t1608 + 0.864e-6 * t1613 * t117 * t1615 + 0.5184e-8 * t1620 * t129 * t1622
  t1655 = -0.14764770444444444444444444444444444444444444444444e-2 * t8 * t825 * t1563 - 0.35616666666666666666666666666666666666666666666666e-1 * t655 * t1546 * t1438 - 0.20000000000000000000000000000000000000000000000000e1 * t1436 * t1559 + 0.10000000000000000000000000000000000000000000000000e1 * t1581 * t1547 + 0.16081824322151104821330931780901225435013347914188e2 * t1399 * t1537 + 0.24415406715670879921742973310852762593515528885057e-3 * t1552 * t1366 * t268 * t1553 + 0.10843580882781524214666447553230042011687479519034e-1 * t1349 * t685 * t1449 + 0.11696446794910408141662685001236899248561775660981e1 * t1476 * t1385 - 0.58482233974552040708313425006184496242808878304903e0 * t1476 * t1461 - 0.17315755899375863299672358916972966258900005419821e2 * t1476 * t1470 - 0.2e1 * t1181
  t1659 = t1597 * t101
  t1660 = t222 * t1608
  t1665 = t1605 * t114
  t1666 = t230 * t1615
  t1671 = t1612 * t124
  t1673 = t239 * t1622 * t90
  t1678 = t1619 * t246
  t1680 = 0.1e1 / t1621 / t1600
  t1684 = -0.16000000000000000000000000000000000000000000000000e-1 * t1598 * t214 * t1601 + 0.19200000000000000000000000000000000000000000000000e-3 * t1659 * t1660 - 0.38400000000000000000000000000000000000000000000000e-3 * t1606 * t1660 + 0.46080000000000000000000000000000000000000000000000e-5 * t1665 * t1666 - 0.6912e-5 * t1613 * t1666 + 0.41472000000000000000000000000000000000000000000000e-7 * t1671 * t1673 - 0.55296000000000000000000000000000000000000000000000e-7 * t1620 * t1673 + 0.66355200000000000000000000000000000000000000000000e-9 * t1678 * t251 * t1680
  t1699 = 0.11073577833333333333333333333333333333333333333333e-2 * t8 * t685 * t1563 + 0.10000000000000000000000000000000000000000000000000e1 * t1581 * t1438 - 0.18311555036753159941307229983139571945136646663793e-3 * t1552 * t1366 * t146 * t1553 - 0.58482233974552040708313425006184496242808878304903e0 * t1476 * t1449 - 0.2e1 * t1238
  t1703 = t372 * t1608
  t1706 = t1597 * t114
  t1707 = t377 * t1615
  t1714 = t1605 * t124
  t1716 = t388 * t1622 * t90
  t1723 = t1612 * t246
  t1725 = t400 * t1680 * t11
  t1732 = t1619 * t409
  t1734 = 0.1e1 / t1621 / t1607
  t1738 = 0.58666666666666666666666666666666666666666666666667e-1 * t1598 * t365 * t1601 - 0.17280000000000000000000000000000000000000000000000e-2 * t1659 * t1703 + 0.12288000000000000000000000000000000000000000000000e-4 * t1706 * t1707 + 0.24320000000000000000000000000000000000000000000000e-2 * t1606 * t1703 - 0.66048000000000000000000000000000000000000000000000e-4 * t1665 * t1707 + 0.22118400000000000000000000000000000000000000000000e-6 * t1714 * t1716 + 0.62208e-4 * t1613 * t1707 - 0.81561600000000000000000000000000000000000000000000e-6 * t1671 * t1716 + 0.53084160000000000000000000000000000000000000000000e-8 * t1723 * t1725 + 0.64512000000000000000000000000000000000000000000000e-6 * t1620 * t1716 - 0.16588800000000000000000000000000000000000000000000e-7 * t1678 * t1725 + 0.10616832000000000000000000000000000000000000000000e-9 * t1732 * t413 * t1734
  t1747 = -0.62182e-1 * t1390 * t1563 + 0.19751789702565206228825776161588751761046270558698e-1 * t1348 * t1475 * t1553 - 0.2e1 * t1293
  t1751 = t588 * t1608
  t1754 = t592 * t1615
  t1757 = t1597 * t124
  t1759 = t599 * t1622 * t90
  t1768 = t1605 * t246
  t1770 = t612 * t1680 * t11
  t1779 = t1612 * t409
  t1780 = t625 * t1734
  t1789 = t1619 * t635
  t1791 = 0.1e1 / t1621 / t1614
  t1796 = -0.27377777777777777777777777777777777777777777777778e0 * t1598 * t582 * t1601 + 0.14549333333333333333333333333333333333333333333333e-1 * t1659 * t1751 - 0.23347200000000000000000000000000000000000000000000e-3 * t1706 * t1754 + 0.58982400000000000000000000000000000000000000000000e-6 * t1757 * t1759 - 0.17834666666666666666666666666666666666666666666667e-1 * t1606 * t1751 + 0.81612800000000000000000000000000000000000000000000e-3 * t1665 * t1754 - 0.59719680000000000000000000000000000000000000000000e-5 * t1714 * t1759 + 0.28311552000000000000000000000000000000000000000000e-7 * t1768 * t1770 - 0.622080e-3 * t1613 * t1754 + 0.13317120000000000000000000000000000000000000000000e-4 * t1671 * t1759 - 0.18579456000000000000000000000000000000000000000000e-6 * t1723 * t1770 + 0.84934656000000000000000000000000000000000000000000e-9 * t1779 * t1780 - 0.81715200000000000000000000000000000000000000000000e-5 * t1620 * t1759 + 0.33693696000000000000000000000000000000000000000000e-6 * t1678 * t1770 - 0.45652377600000000000000000000000000000000000000000e-8 * t1732 * t1780 + 0.10192158720000000000000000000000000000000000000000e-10 * t1789 * t639 * t1791 * t90
  t1803 = t273 ** 2
  t1806 = t264 ** 2
  t1840 = 0.1e1 / t20 / t103
  t1844 = 0.140e3 / 0.729e3 * t29 * t5 * t1840 * t34
  t1845 = f.my_piecewise3(t39, t1844, 0)
  t1854 = -t48 * t1803 / 0.16e2 + 0.9e1 / 0.80e2 * t54 * t1806 + 0.3e1 / 0.640e3 * t51 * t1803 - 0.11e2 / 0.1152e4 * t57 * t1806 - t54 * t1803 / 0.3840e4 + 0.13e2 / 0.21504e5 * t60 * t1806 + t57 * t1803 / 0.86016e5 - t63 * t1806 / 0.32768e5 - t60 * t1803 / 0.2293760e7 + 0.17e2 / 0.13271040e8 * t301 * t1806 + t63 * t1803 / 0.70778880e8 - 0.19e2 / 0.412876800e9 / t62 / t44 * t1806 - t301 * t1803 / 0.2477260800e10 + 0.10e2 / 0.3e1 * t48 * t1806 + t45 * t1803 / 0.2e1 - 0.7e1 / 0.8e1 * t51 * t1806 - t167 * t1845 / 0.2838528e7 + t171 * t1845 / 0.89456640e8 - t175 * t1845 / 0.3185049600e10 + t179 * t1845 / 0.126340300800e12
  t1911 = -t144 * t1845 / 0.18e2 + t155 * t1845 / 0.240e3 - t159 * t1845 / 0.4480e4 + t163 * t1845 / 0.103680e6 - 0.3e1 / 0.40e2 * t163 * t264 * t273 + t167 * t264 * t273 / 0.192e3 - t171 * t264 * t273 / 0.3584e4 + t175 * t264 * t273 / 0.81920e5 - t179 * t264 * t273 / 0.2211840e7 + t486 * t264 * t273 / 0.68812800e8 + t57 * t431 * t151 / 0.64512e5 - t60 * t431 * t151 / 0.1720320e7 + t63 * t431 * t151 / 0.53084160e8 - t301 * t431 * t151 / 0.1857945600e10 + 0.2e1 / 0.3e1 * t45 * t431 * t151 - t48 * t431 * t151 / 0.12e2 + t51 * t431 * t151 / 0.160e3 - t54 * t431 * t151 / 0.2880e4 - 0.4e1 * t155 * t264 * t273 + 0.3e1 / 0.4e1 * t159 * t264 * t273
  t1913 = f.my_piecewise3(t39, 0, t1844)
  t1922 = t315 ** 2
  t1939 = t307 ** 2
  t1943 = t75 * t494
  t1987 = -0.75e2 / 0.2e1 * t335 * t1922 * t75 + 0.45e2 * t316 * t506 - 0.6e1 * t327 * t1939 * t75 - 0.8e1 * t530 * t1943 - 0.15e2 * t534 * t315 * t506 + t335 * t494 * t542 + 0.3e1 / 0.4e1 * t335 * t1939 * t75 + 0.3e1 / 0.4e1 * t546 * t307 * t315 * t75 - 0.3e1 * t73 * t1939 * t75 - 0.4e1 * t553 * t1943 + 0.85e2 / 0.4e1 * t510 * t1922 * t75 - 0.19e2 / 0.8e1 / t509 / t72 * t1922 * t75 + t190 * t1913 * t75 / 0.2e1 + 0.1e1 / t509 / t312 * t1922 * t75 / 0.16e2 - 0.12e2 * t1939 * t76 - 0.16e2 * t550 * t494 - 0.4e1 * t194 * t1913 - t68 * t1913 * t75
  t2020 = 0.15e2 / 0.4e1 * t546 * t1922 * t75 - 0.1e1 / t509 / t189 * t1922 * t75 / 0.8e1 - t185 * t1913 + 0.8e1 * t183 * t560 + 0.2e1 * t66 * t1987 + 0.2e1 * t1913 * t79 + 0.8e1 * t494 * t199 + 0.12e2 * t307 * t347 - 0.2e1 * t505 * t1943 - 0.3e1 / 0.2e1 * t510 * t315 * t506 + 0.24e2 * t75 * t314 * t1922 - 0.36e2 * t514 * t315 * t307 + 0.6e1 * t319 * t1939 + 0.8e1 * t319 * t183 * t494 - 0.24e2 * t534 * t1922 * t75 + 0.21e2 * t336 * t506 - 0.3e1 / 0.2e1 * t314 * t1939 * t75
  t2024 = f.my_piecewise3(t38, t1854 + t1911, -0.8e1 / 0.3e1 * t1913 * t82 - 0.32e2 / 0.3e1 * t494 * t202 - 0.16e2 * t307 * t350 - 0.32e2 / 0.3e1 * t183 * t563 - 0.8e1 / 0.3e1 * t66 * t2020)
  t2043 = t90 / t21 / t219
  t2049 = t11 / t20 / t229
  t2050 = t2049 * t109
  t2054 = 0.1e1 / t21 / t248
  t2055 = t90 * t2054
  t2056 = t2055 * t131
  t2061 = 0.1e1 / t21 / t411 / t219
  t2063 = t2061 * t641 * t90
  t2066 = t124 ** 2
  t2070 = 0.1e1 / t20 / t411 / t229
  t2071 = t130 ** 2
  t2084 = 0.1e1 / t20 / t411 / r0
  t2086 = t2084 * t253 * t11
  t2093 = 0.1e1 / t386
  t2094 = t2093 * t119
  t2112 = 0.1e1 / t411 / t103
  t2113 = t2112 * t415
  t2120 = 0.10342716049382716049382716049382716049382716049383e1 * t89 * t2043 * t96 + 0.66054320987654320987654320987654320987654320987655e-1 * t102 * t2050 + 0.22059741234567901234567901234567901234567901234569e-4 * t125 * t2056 - 0.38575169232592592592592592592592592592592592592596e-10 * t636 * t2063 + 0.89080803176296296296296296296296296296296296296308e-13 * t123 * t2066 * t2070 / t2071 * t11 - 0.57780148148148148148148148148148148148148148148150e-1 * t218 * t2050 - 0.38059425185185185185185185185185185185185185185188e-5 * t596 * t2056 + 0.99420539259259259259259259259259259259259259259267e-8 * t88 * t246 * t2086 + 0.23859958518518518518518518518518518518518518518520e-4 * t385 * t2056 - 0.16155837629629629629629629629629629629629629629631e-6 * t610 * t2086 + 0.2027520e-2 * t115 * t2094 - 0.41848983703703703703703703703703703703703703703705e-4 * t236 * t2056 + 0.62409690074074074074074074074074074074074074074078e-6 * t397 * t2086 + 0.47721858844444444444444444444444444444444444444450e-11 * t113 * t635 * t2063 - 0.86245376000000000000000000000000000000000000000006e-6 * t247 * t2086 + 0.10368442469135802469135802469135802469135802469136e-2 * t376 * t2094 - 0.29981708641975308641975308641975308641975308641977e-2 * t228 * t2094 + 0.39768215703703703703703703703703703703703703703709e-9 * t100 * t409 * t2113 - 0.40265318400000000000000000000000000000000000000004e-8 * t623 * t2113 + 0.12347823849876543209876543209876543209876543209877e-7 * t410 * t2113
  t2152 = 0.5e1 / 0.108e3 * t13 * t18 * t213 * t136 - 0.3e1 / 0.64e2 * t13 * t424 * t2024 * t135 - 0.3e1 / 0.16e2 * t13 * t424 * t567 * t257 - 0.9e1 / 0.32e2 * t13 * t424 * t354 * t419 - 0.3e1 / 0.16e2 * t13 * t424 * t206 * t646 - 0.3e1 / 0.64e2 * t13 * t424 * t86 * t2120 + t13 * t142 * t420 / 0.16e2 - t13 * t263 * t568 / 0.16e2 - 0.3e1 / 0.16e2 * t13 * t263 * t572 - 0.3e1 / 0.16e2 * t13 * t263 * t576 - t13 * t263 * t647 / 0.16e2 - 0.5e1 / 0.72e2 * t13 * t24 * t207 - 0.5e1 / 0.72e2 * t13 * t24 * t258 + t13 * t142 * t355 / 0.16e2 + t13 * t142 * t359 / 0.8e1
  t2153 = f.my_piecewise3(t4, 0, t2152)
  t2156 = t775 * t5 * t1367
  t2172 = t1840 * t11
  t2175 = 0.11483710345679012345679012345679012345679012345679e-1 * t655 * t2172 * t877
  t2194 = t704 ** 2
  t2197 = 0.62070017646847402095774076540096717770467394091622e4 * t662 / t678 / t807 * t2194 * t711
  t2200 = 0.57894567559743977356791354411244411566048052491077e3 * t681 * t2194 * t718
  t2203 = 0.24000000000000000000000000000000000000000000000000e2 * t717 * t2194 * t765
  t2205 = t8 * t685 * t11
  t2209 = 0.42740000000000000000000000000000000000000000000000e0 * t2205 * t658 * t808 * t841
  t2213 = 0.34366858576436911003184201215785918754623524492620e1 * t2205 * t658 * t814 * t845
  t2220 = t790 * t919
  t2234 = t2175 - 0.86748647062252193717331580425840336093499836152272e-1 * t904 * t1016 + 0.44061327329259140130803044923340838426074836496192e1 * t904 * t1001 - 0.21309037037037037037037037037037037037037037037036e0 * t1504 * t1007 - 0.55208163456790123456790123456790123456790123456787e-2 * t655 * t2172 * t1028 - 0.18989760778855128828022312575107704239400966910600e-2 * t655 * t2172 * t1032 + t2197 - t2200 + t2203 - t2209 + t2213 + 0.36000000000000000000000000000000000000000000000000e2 * t985 * t1142 * t979 + 0.21053604230838734654992833002226418647411196189766e2 * t947 * t1156 * t870 + 0.61523382126046769584908008232272042135015119629847e4 * t1043 * t2220 * t870 - 0.62336721237753107878820492101102678532040019511357e3 * t1047 * t1161 * t870 - 0.46785787179641632566650740004947596994247102643924e1 * t942 * t1052 * t789 + 0.69263023597503453198689435667891865035600021679284e2 * t947 * t937 * t852 * t789
  t2252 = 0.31035008823423701047887038270048358885233697045812e4 * t681 * t704 * t711 * t840
  t2255 = 0.57894567559743977356791354411244411566048052491077e3 * t717 * t1134 * t840
  t2258 = 0.80000000000000000000000000000000000000000000000000e1 * t819 * t766 * t703
  t2262 = 0.64327297288604419285323727123604901740053391656752e2 * t815 * t764 * t718 * t703
  t2265 = 0.36000000000000000000000000000000000000000000000000e2 * t815 * t1128 * t840
  t2266 = t870 ** 2
  t2274 = 0.1e1 / t848 / t783
  t2276 = t790 ** 2
  t2283 = t998 ** 2
  t2293 = t848 ** 2
  t2294 = 0.1e1 / t2293
  t2296 = t851 ** 2
  t2297 = 0.1e1 / t2296
  t2301 = t979 ** 2
  t2305 = 0.12414802127193579147105162995488978190399819737073e5 * t1057 * t998 * t1059 * t979 - 0.11579285944033451270504985525892569958185911868768e4 * t1065 * t1148 * t979 - 0.80000000000000000000000000000000000000000000000000e1 * t962 * t1079 * t967 + 0.12865873271148279189449983917658411064651013187520e3 * t985 * t1078 * t987 * t967 - t2252 + t2255 + t2258 - t2262 - t2265 - 0.35089340384731224424988055003710697745685326982943e1 * t942 * t2266 * t795 + 0.51947267698127589899017076750918898776700016259463e2 * t947 * t2266 * t852 - 0.12304676425209353916981601646454408427003023925970e5 * t882 * t2274 * t2276 * t919 - 0.24829604254387158294210325990977956380799639474146e5 * t953 / t983 / t960 * t2283 * t1059 + 0.11579285944033451270504985525892569958185911868768e4 * t1057 * t2283 * t987 + 0.62336721237753107878820492101102678532040019511358e3 * t1043 * t2276 * t852 + 0.91080982599109921218848830805163797795664001346962e5 * t882 * t2294 * t2276 * t2297 - 0.60000000000000000000000000000000000000000000000000e1 * t962 * t2301 * t971
  t2317 = t6 / r0
  t2323 = t672 ** 2
  t2324 = t106 * t2323
  t2326 = 0.1e1 / t663 / t2317 / t729 * t6 * t2324 * t13 / 0.96e2
  t2328 = 0.1e1 / t104
  t2329 = t2328 * t729
  t2330 = t727 * t2329
  t2332 = t9 * t364
  t2333 = t2332 * t738
  t2334 = t736 * t2333
  t2336 = t10 * t1840
  t2337 = t2336 * t686
  t2338 = t684 * t2337
  t2341 = t655 * t2172 * t658
  t2343 = t660 ** (-0.25e1)
  t2346 = t2343 * t6 * t2324 * t13
  t2348 = t751 * t2329
  t2350 = t756 * t2333
  t2352 = t696 * t2337
  t2355 = t670 * t365 * t672
  t2371 = -0.57538888888888888888888888888888888888888888888889e1 * t2326 + 0.55237333333333333333333333333333333333333333333334e2 * t2330 - 0.10229135802469135802469135802469135802469135802469e2 * t2334 + 0.89504938271604938271604938271604938271604938271607e1 * t2338 + 0.31310740740740740740740740740740740740740740740741e1 * t2341 + 0.73355000000000000000000000000000000000000000000000e-1 * t2346 - 0.11736800000000000000000000000000000000000000000000e1 * t2348 + 0.65204444444444444444444444444444444444444444444445e0 * t2350 + 0.57053888888888888888888888888888888888888888888890e0 * t2352 + 0.13490888888888888888888888888888888888888888888889e1 * t2355
  t2375 = t983 ** 2
  t2378 = t986 ** 2
  t2383 = t840 ** 2
  t2386 = 0.60000000000000000000000000000000000000000000000000e1 * t819 * t2383 * t765
  t2389 = 0.48245472966453314463992795342703676305040043742564e2 * t815 * t2383 * t718
  t2390 = t678 ** 2
  t2393 = t709 ** 2
  t2397 = 0.24954977986735470914321699422701391789612506067521e5 * t662 / t2390 * t2194 / t2393
  t2411 = 0.10000000000000000000000000000000000000000000000000e1 * t723 * (-0.42198333333333333333333333333333333333333333333333e1 * t2326 + 0.40510400000000000000000000000000000000000000000000e2 * t2330 - 0.75019259259259259259259259259259259259259259259258e1 * t2334 + 0.65641851851851851851851851851851851851851851851850e1 * t2338 + 0.31003950617283950617283950617283950617283950617285e1 * t2341 + 0.13651666666666666666666666666666666666666666666666e0 * t2346 - 0.21842666666666666666666666666666666666666666666666e1 * t2348 + 0.12134814814814814814814814814814814814814814814815e1 * t2350 + 0.10617962962962962962962962962962962962962962962963e1 * t2352 + 0.13388493827160493827160493827160493827160493827161e1 * t2355) * t765
  t2435 = 0.96494049533612093920874879382438082984882598906400e2 * t985 * t2301 * t987 - 0.24000000000000000000000000000000000000000000000000e2 * t1065 * t2283 * t971 - 0.14035736153892489769995222001484279098274130793177e2 * t1047 * t2276 * t795 + 0.99999999999999999999999999999999999999999999999999e0 * t1069 * (-0.78438333333333333333333333333333333333333333333333e1 * t2326 + 0.75300800000000000000000000000000000000000000000001e2 * t2330 - 0.13944592592592592592592592592592592592592592592593e2 * t2334 + 0.12201518518518518518518518518518518518518518518519e2 * t2338 + 0.53560370370370370370370370370370370370370370370370e1 * t2341 + 0.28051666666666666666666666666666666666666666666666e0 * t2346 - 0.44882666666666666666666666666666666666666666666666e1 * t2348 + 0.24934814814814814814814814814814814814814814814815e1 * t2350 + 0.21817962962962962962962962962962962962962962962963e1 * t2352 + 0.16979925925925925925925925925925925925925925925926e1 * t2355) * t971 + 0.58482233974552040708313425006184496242808878304903e0 * t1051 * t2371 * t795 + 0.19965908856856833623520686708731068173688999255505e6 * t953 / t2375 * t2283 / t2378 + t2386 - t2389 - t2397 - t2411 + 0.38527556876111295841770998590264849926052512059102e1 * t806 * t686 * t926 - 0.41096000000000000000000000000000000000000000000000e0 * t806 * t686 * t984 * t1036 * t971 - 0.13012297059337829057599737063876050414024975422841e0 * t806 * t686 * t896 - 0.38024868119570572868450088421334803819557955882337e2 * t806 * t686 * t920 + 0.43374323531126096858665790212920168046749918076136e-1 * t904 * t992 + 0.13698666666666666666666666666666666666666666666666e0 * t904 * t1012 - 0.68493333333333333333333333333333333333333333333332e-1 * t806 * t686 * t1004 * t1078 * t971
  t2456 = 0.22161481481481481481481481481481481481481481481481e0 * t1504 * t907
  t2461 = 0.71233333333333333333333333333333333333333333333332e-1 * t806 * t686 * t722 * t764 * t765
  t2463 = 0.14246666666666666666666666666666666666666666666666e0 * t904 * t912
  t2468 = 0.36845452142031360632963667101718523854302450326054e2 * t806 * t686 * t680 * t705 * t711
  t2473 = 0.68733717152873822006368402431571837509247048985239e1 * t806 * t686 * t716 * t705 * t718
  t2475 = 0.28493333333333333333333333333333333333333333333334e0 * t904 * t811
  t2480 = 0.42740000000000000000000000000000000000000000000000e0 * t806 * t686 * t814 * t705 * t765
  t2482 = 0.22911239050957940668789467477190612503082349661746e1 * t904 * t901
  t2499 = -0.21687161765563048429332895106460084023374959038068e-1 * t806 * t686 * t939 - 0.14172186339420759128595382735072640214240860886520e3 * t806 * t686 * t1056 * t1036 * t1059 + 0.13218398198777742039240913477002251527822450948858e2 * t806 * t686 * t1064 * t1036 * t987 + 0.12842518958703765280590332863421616642017504019700e1 * t904 * t995 - 0.27397333333333333333333333333333333333333333333333e0 * t904 * t1021 - 0.67471169937307261780146784775653594739388761451767e-1 * t1504 * t1024 + t2456 + t2461 - t2463 + t2468 - t2473 + t2475 + t2480 - t2482 - 0.19263778438055647920885499295132424963026256029551e1 * t2205 * t658 * t849 * t949 + 0.13012297059337829057599737063876050414024975422841e0 * t2205 * t658 * t784 * t944 + 0.41096000000000000000000000000000000000000000000000e0 * t2205 * t658 * t961 * t980 - 0.66091990993888710196204567385011257639112254744288e1 * t2205 * t658 * t984 * t989
  t2519 = -0.13012297059337829057599737063876050414024975422841e0 * t2156 * t686 * t784 * t944 + 0.19263778438055647920885499295132424963026256029551e1 * t2156 * t686 * t849 * t949 - 0.21053604230838734654992833002226418647411196189766e2 * t883 * t850 * t890 + 0.62336721237753107878820492101102678532040019511357e3 * t883 * t924 * t870 * t1161 - t2175 + 0.46785787179641632566650740004947596994247102643924e1 * t883 * t889 * t1052 + t775 * (t2234 + t2305 + t2435 + t2499) - 0.58482233974552040708313425006184496242808878304903e0 * t883 * t857 * t2371 * t795 + 0.14035736153892489769995222001484279098274130793177e2 * t883 * t924 * t2276 * t795 + 0.35089340384731224424988055003710697745685326982943e1 * t883 * t784 * t2266 * t795 - 0.51947267698127589899017076750918898776700016259463e2 * t883 * t849 * t2266 * t852
  t2548 = -0.91080982599109921218848830805163797795664001346962e5 * t883 * t2294 * t2276 * t2297 - 0.38527556876111295841770998590264849926052512059102e1 * t776 * t691 * t926 + 0.67471169937307261780146784775653594739388761451767e-1 * t776 * t747 * t859 + 0.86748647062252193717331580425840336093499836152272e-1 * t776 * t830 * t796 - t2197 + t2200 - t2203 + 0.13012297059337829057599737063876050414024975422841e0 * t776 * t691 * t896 - 0.12842518958703765280590332863421616642017504019700e1 * t776 * t830 * t853 + 0.38024868119570572868450088421334803819557955882337e2 * t776 * t691 * t920 - 0.43374323531126096858665790212920168046749918076136e-1 * t776 * t830 * t872 + 0.21687161765563048429332895106460084023374959038068e-1 * t776 * t691 * t939
  t2566 = t2209 - t2213 - 0.69263023597503453198689435667891865035600021679284e2 * t883 * t849 * t937 * t885 - 0.61523382126046769584908008232272042135015119629847e4 * t883 * t916 * t870 * t2220 + t2252 - t2255 - t2258 + t2262 + t2265 - 0.62336721237753107878820492101102678532040019511358e3 * t883 * t916 * t2276 * t852 + 0.12304676425209353916981601646454408427003023925970e5 * t883 * t2274 * t2276 * t919 - t2386
  t2570 = t2389 + t2397 + t2411 - t2456 - t2461 + t2463 - t2468 + t2473 - t2475 - t2480 + t2482 + 0.18989760778855128828022312575107704239400966910600e-2 * t800 * t2336 * t802
  t2575 = f.my_piecewise3(t4, 0, t654 * (t2519 + t2548 + t2566 + t2570) / 0.2e1)
  t2585 = t2054 * t1116 * t90
  t2589 = t2084 * t1206 * t11
  t2594 = t2061 * t1337 * t90
  t2602 = t1115 ** 2
  t2608 = t2049 * t1102
  t2620 = t2093 * t1109
  t2635 = t2112 * t1273
  t2642 = -0.26155614814814814814814814814814814814814814814815e3 * t1197 * t2585 + 0.19503028148148148148148148148148148148148148148148e3 * t1262 * t2589 + 0.37282702222222222222222222222222222222222222222224e1 * t1106 * t635 * t2594 - 0.26951680000000000000000000000000000000000000000000e3 * t1204 * t2589 - 0.30136850962962962962962962962962962962962962962965e2 * t1335 * t2594 + 0.34797188740740740740740740740740740740740740740745e1 * t1113 * t2066 * t2070 / t2602 * t11 - 0.14445037037037037037037037037037037037037037037037e3 * t1185 * t2608 - 0.23787140740740740740740740740740740740740740740743e2 * t1303 * t2585 + 0.31068918518518518518518518518518518518518518518521e1 * t1091 * t246 * t2589 + 0.14912474074074074074074074074074074074074074074074e3 * t1253 * t2585 - 0.50486992592592592592592592592592592592592592592595e2 * t1314 * t2589 + 0.253440e3 * t1107 * t2620 + 0.13787338271604938271604938271604938271604938271605e3 * t1114 * t2585 + 0.51713580246913580246913580246913580246913580246912e2 * t1092 * t2043 * t1095 + 0.16513580246913580246913580246913580246913580246913e3 * t1100 * t2608 + 0.12960553086419753086419753086419753086419753086421e3 * t1245 * t2620 - 0.37477135802469135802469135802469135802469135802470e3 * t1191 * t2620 + 0.62137837037037037037037037037037037037037037037042e1 * t1099 * t409 * t2635 - 0.62914560000000000000000000000000000000000000000004e2 * t1325 * t2635 + 0.19293474765432098765432098765432098765432098765434e3 * t1271 * t2635
  t2679 = -0.38527556876111295841770998590264849926052512059102e1 * t1349 * t685 * t1489 - 0.43374323531126096858665790212920168046749918076136e-1 * t1349 * t825 * t1461 - 0.12842518958703765280590332863421616642017504019700e1 * t1349 * t825 * t1470 + 0.21687161765563048429332895106460084023374959038068e-1 * t1349 * t685 * t1518 + 0.38024868119570572868450088421334803819557955882337e2 * t1349 * t685 * t1483 + 0.67471169937307261780146784775653594739388761451767e-1 * t1349 * t742 * t1449 + 0.86748647062252193717331580425840336093499836152272e-1 * t1349 * t825 * t1385 + 0.13012297059337829057599737063876050414024975422841e0 * t1349 * t685 * t1528 - 0.42740000000000000000000000000000000000000000000000e0 * t655 * t1536 * t1444 - 0.36845452142031360632963667101718523854302450326054e2 * t655 * t146 * t1568 * t1572 + 0.14246666666666666666666666666666666666666666666666e0 * t655 * t1542 * t1547
  t2693 = t1469 * t1459
  t2698 = t1384 * t1378
  t2729 = 0.68733717152873822006368402431571837509247048985239e1 * t655 * t146 * t1576 * t1578 - 0.22161481481481481481481481481481481481481481481481e0 * t655 * t426 * t1541 * t1438 - 0.28493333333333333333333333333333333333333333333334e0 * t655 * t268 * t1435 * t1559 + 0.62336721237753107878820492101102678532040019511357e3 * t1476 * t1487 * t1379 * t2693 + 0.46785787179641632566650740004947596994247102643924e1 * t1476 * t1363 * t1516 * t2698 - 0.69263023597503453198689435667891865035600021679284e2 * t1476 * t1466 * t1516 * t1522 - 0.21053604230838734654992833002226418647411196189766e2 * t1476 * t1467 * t1532 + 0.18989760778855128828022312575107704239400966910600e-2 * t1552 * t1366 * t1840 * t1553 + 0.22911239050957940668789467477190612503082349661746e1 * t655 * t268 * t1398 * t1537 - 0.71233333333333333333333333333333333333333333333332e-1 * t655 * t1546 * t1591 - 0.61523382126046769584908008232272042135015119629847e4 * t1476 * t1478 * t1379 * t1482 * t1459 + 0.42740000000000000000000000000000000000000000000000e0 * t806 * t1435 * t1430 * t1547
  t2739 = t1397 ** 2
  t2742 = t1442 ** 2
  t2743 = t1423 ** 2
  t2765 = t1348 * t655
  t2781 = 0.1e1 / t1352 / t2317 * t6 * t106 * t655 / 0.48e2
  t2783 = t1495 * t2328
  t2785 = t1403 * t364
  t2786 = t1402 * t2785
  t2788 = t1366 * t1840
  t2789 = t1365 * t2788
  t2791 = t8 * t2336
  t2793 = t1351 ** (-0.25e1)
  t2796 = t2793 * t6 * t106 * t655
  t2798 = t1507 * t2328
  t2800 = t1412 * t2785
  t2802 = t1372 * t2788
  t2804 = t669 * t2332
  t2825 = -0.34366858576436911003184201215785918754623524492620e1 * t806 * t1398 * t1419 * t1424 * t1430 - 0.57894567559743977356791354411244411566048052491077e3 * t1577 * t1425 * t1442 + 0.24954977986735470914321699422701391789612506067521e5 * t1390 / t2739 * t2742 / t2743 - 0.80000000000000000000000000000000000000000000000000e1 * t1436 * t1438 * t1590 + 0.31035008823423701047887038270048358885233697045812e4 * t1569 * t1419 * t1571 * t1442 + 0.64327297288604419285323727123604901740053391656752e2 * t1399 * t1590 * t1424 * t1430 - 0.11483710345679012345679012345679012345679012345679e-1 * t8 * t2336 * t1563 + 0.36000000000000000000000000000000000000000000000000e2 * t1399 * t1559 * t1419 - 0.13012297059337829057599737063876050414024975422841e0 * t2765 * t146 * t1363 * t2698 * t1459 + 0.19263778438055647920885499295132424963026256029551e1 * t2765 * t146 * t1466 * t2693 * t1378 - 0.58482233974552040708313425006184496242808878304903e0 * t1476 * t1447 * (-0.28769444444444444444444444444444444444444444444444e1 * t2781 + 0.27618666666666666666666666666666666666666666666667e2 * t2783 - 0.10229135802469135802469135802469135802469135802469e2 * t2786 + 0.89504938271604938271604938271604938271604938271607e1 * t2789 + 0.31310740740740740740740740740740740740740740740741e1 * t2791 + 0.36677500000000000000000000000000000000000000000000e-1 * t2796 - 0.58684000000000000000000000000000000000000000000000e0 * t2798 + 0.65204444444444444444444444444444444444444444444445e0 * t2800 + 0.57053888888888888888888888888888888888888888888890e0 * t2802 + 0.13490888888888888888888888888888888888888888888889e1 * t2804) * t1384 + 0.10000000000000000000000000000000000000000000000000e1 * t1581 * (-0.21099166666666666666666666666666666666666666666667e1 * t2781 + 0.20255200000000000000000000000000000000000000000000e2 * t2783 - 0.75019259259259259259259259259259259259259259259258e1 * t2786 + 0.65641851851851851851851851851851851851851851851850e1 * t2789 + 0.31003950617283950617283950617283950617283950617285e1 * t2791 + 0.68258333333333333333333333333333333333333333333335e-1 * t2796 - 0.10921333333333333333333333333333333333333333333333e1 * t2798 + 0.12134814814814814814814814814814814814814814814815e1 * t2800 + 0.10617962962962962962962962962962962962962962962963e1 * t2802 + 0.13388493827160493827160493827160493827160493827161e1 * t2804) * t1437
  t2838 = t1419 ** 2
  t2846 = t1465 ** 2
  t2848 = t1379 ** 2
  t2850 = t1468 ** 2
  t2855 = t1459 ** 2
  t2878 = 0.57894567559743977356791354411244411566048052491077e3 * t1569 * t2742 * t1424 - 0.62070017646847402095774076540096717770467394091622e4 * t1390 / t1397 / t1434 * t2742 * t1571 - 0.24000000000000000000000000000000000000000000000000e2 * t1577 * t2742 * t1437 + 0.48245472966453314463992795342703676305040043742564e2 * t1399 * t2838 * t1424 - 0.60000000000000000000000000000000000000000000000000e1 * t1436 * t2838 * t1437 - 0.2e1 * t2575 - 0.91080982599109921218848830805163797795664001346962e5 * t1476 / t2846 * t2848 / t2850 + 0.35089340384731224424988055003710697745685326982943e1 * t1476 * t1363 * t2855 * t1384 - 0.51947267698127589899017076750918898776700016259463e2 * t1476 * t1466 * t2855 * t1469 + 0.14035736153892489769995222001484279098274130793177e2 * t1476 * t1487 * t2848 * t1384 - 0.62336721237753107878820492101102678532040019511358e3 * t1476 * t1478 * t2848 * t1469 + 0.12304676425209353916981601646454408427003023925970e5 * t1476 / t1465 / t1362 * t2848 * t1482
  t2888 = t2055 * t1622
  t2894 = t2049 * t1608
  t2903 = t2084 * t1680 * t11
  t2910 = t2093 * t1615
  t2919 = t2061 * t1791 * t90
  t2927 = t1621 ** 2
  t2938 = t2112 * t1734
  t2945 = 0.11167744000000000000000000000000000000000000000000e-3 * t1620 * t2888 + 0.15514074074074074074074074074074074074074074074074e1 * t1598 * t2043 * t1601 + 0.14862222222222222222222222222222222222222222222222e0 * t1606 * t2894 - 0.13000533333333333333333333333333333333333333333333e0 * t1659 * t2894 - 0.19267584000000000000000000000000000000000000000000e-4 * t1757 * t2888 + 0.75497472000000000000000000000000000000000000000000e-7 * t1597 * t246 * t2903 + 0.12079104000000000000000000000000000000000000000000e-3 * t1714 * t2888 - 0.12268339200000000000000000000000000000000000000000e-5 * t1768 * t2903 + 0.6842880e-2 * t1613 * t2910 - 0.21186048000000000000000000000000000000000000000000e-3 * t1671 * t2888 + 0.47392358400000000000000000000000000000000000000000e-5 * t1723 * t2903 + 0.81537269760000000000000000000000000000000000000000e-10 * t1612 * t635 * t2919 - 0.65492582400000000000000000000000000000000000000000e-5 * t1678 * t2903 - 0.65909293056000000000000000000000000000000000000000e-9 * t1789 * t2919 + 0.22830435532800000000000000000000000000000000000000e-11 * t1619 * t2066 * t2070 / t2927 * t11 + 0.34993493333333333333333333333333333333333333333333e-2 * t1706 * t2910 - 0.10118826666666666666666666666666666666666666666667e-1 * t1665 * t2910 + 0.45298483200000000000000000000000000000000000000000e-8 * t1605 * t409 * t2938 - 0.45864714240000000000000000000000000000000000000000e-7 * t1779 * t2938 + 0.14064943104000000000000000000000000000000000000000e-6 * t1732 * t2938
  t2947 = 0.2e1 * t2153 + 0.2e1 * t2575 * t1120 + 0.8e1 * t1089 * t1210 + 0.12e2 * t1181 * t1277 + 0.8e1 * t1238 * t1342 + 0.2e1 * t1293 * t2642 + (t2679 + t2729 + t2825 + t2878) * t1626 + 0.4e1 * t1595 * t1684 + 0.6e1 * t1655 * t1738 + 0.4e1 * t1699 * t1796 + t1747 * t2945
  v4rho4_0_ = r0 * t2947 + 0.8e1 * t1089 * t1120 + 0.24e2 * t1181 * t1210 + 0.24e2 * t1238 * t1277 + 0.8e1 * t1293 * t1342 + 0.4e1 * t1595 * t1626 + 0.12e2 * t1655 * t1684 + 0.12e2 * t1699 * t1738 + 0.4e1 * t1747 * t1796 + 0.8e1 * t652

  res = {'v4rho4': v4rho4_0_}
  return res

def pol_fxc(p, r, s=(None, None, None), l=(None, None), tau=(None, None)):
  f = funcs(p)
  params = f.params
  (r0, r1), (s0, s1, s2), (l0, l1), (tau0, tau1) = r, s, l, tau

  _b = lambda x: (jnp.asarray(x) + jnp.zeros_like(r0))
  _tmp_res = {'v2rho2': jnp.stack([_b(d11), _b(d12), _b(d22)], axis=-1) if 'd12' in locals() else _b(d11), 'v2rhosigma': jnp.stack([_b(d13), _b(d14), _b(d15), _b(d23), _b(d24), _b(d25)], axis=-1) if 'd13' in locals() else None, 'v2sigma2': jnp.stack([_b(d33), _b(d34), _b(d35), _b(d44), _b(d45), _b(d55)], axis=-1) if 'd33' in locals() else None, 'v2rholapl': jnp.stack([_b(d16), _b(d17), _b(d26), _b(d27)], axis=-1) if 'd16' in locals() else None, 'v2rhotau': jnp.stack([_b(d18), _b(d19), _b(d28), _b(d29)], axis=-1) if 'd18' in locals() else None, 'v2sigmalapl': jnp.stack([_b(d36), _b(d37), _b(d46), _b(d47), _b(d56), _b(d57)], axis=-1) if 'd36' in locals() else None, 'v2sigmatau': jnp.stack([_b(d38), _b(d39), _b(d48), _b(d49), _b(d58), _b(d59)], axis=-1) if 'd38' in locals() else None, 'v2lapl2': jnp.stack([_b(d66), _b(d67), _b(d77)], axis=-1) if 'd66' in locals() else None, 'v2lapltau': jnp.stack([_b(d68), _b(d69), _b(d78), _b(d79)], axis=-1) if 'd68' in locals() else None, 'v2tau2': jnp.stack([_b(d88), _b(d89), _b(d99)], axis=-1) if 'd88' in locals() else None}
  res = {k: v for (k, v) in _tmp_res.items() if v is not None}
  return res

