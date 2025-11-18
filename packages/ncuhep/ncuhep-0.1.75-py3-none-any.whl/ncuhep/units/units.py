import numpy as np
from scipy import constants as const
from itertools import product

TAU = 2 * const.pi  # full turn in radians (τ)

# -------------------------
# Dimension / Registry core
# -------------------------

def _normalize_sig(sig: dict) -> tuple:
    """Normalize a signature dict into a sorted, hashable tuple."""
    return tuple(sorted((k, int(v)) for k, v in sig.items() if v != 0))

def _add_sig(a: dict, b: dict, sgn=1) -> dict:
    """Combine dimension signatures: a + sgn*b."""
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0) + sgn * v
        if out[k] == 0:
            out.pop(k)
    return out

# The registry maps normalized signatures -> concrete classes
_DERIVED_REGISTRY = {}

def register_derived(cls):
    """Class decorator to register a derived quantity by its SIG."""
    key = _normalize_sig(cls.SIG)
    _DERIVED_REGISTRY[key] = cls
    return cls

# ---------------
# Unit base class
# ---------------

class Unit:
    """
    Stores values in SI; attribute-based set/get via conversions dict.
    Carries a dimension signature (SIG) and participates in dimensional
    arithmetic. If a result's signature matches a registered class -> return that.
    Else -> return GenericQuantity with composed conversions.
    """
    SIG = {}  # override in subclasses, e.g. {'L':1}, {'T':1}, etc.

    def __init__(self, conversions: dict, si_unit: str, sig: dict = None):
        self._conversions = conversions
        self._si_unit = si_unit
        # instance signature (default = class SIG)
        self._sig = dict(self.SIG if sig is None else sig)
        self.__value_si = 0.0  # scalar or np.ndarray

    # Attribute set/get for named units
    def __setattr__(self, name, value):
        if "_conversions" in self.__dict__ and name in self._conversions:
            arr = np.asarray(value, dtype=float)
            object.__setattr__(self, "_Unit__value_si", arr * self._conversions[name])
        else:
            object.__setattr__(self, name, value)

    def __getattr__(self, name):
        if name in self._conversions:
            return self.__value_si / self._conversions[name]
        raise AttributeError(f"'{self.__class__.__name__}' has no unit '{name}'")

    # Helpers
    def _get_value_si(self):
        return self._Unit__value_si

    @property
    def value(self):
        """
        Return the raw SI value (float or ndarray).
        For dimensionless quantities, this is the plain numeric value.
        """
        return self._Unit__value_si

    @property
    def unit(self):
        """
        Return a human-readable dimensional signature string,
        showing numerator/denominator units.
        """
        num = []
        den = []
        base_syms = {'M': 'kg', 'L': 'm', 'T': 's', 'Ω': 'sr', 'N': 'count'}
        for k, exp in self._sig.items():
            u = base_syms.get(k, k)
            if exp > 0:
                if exp == 1:
                    num.append(u)
                else:
                    num.append(f"{u}^{exp}")
            elif exp < 0:
                if exp == -1:
                    den.append(u)
                else:
                    den.append(f"{u}^{-exp}")
        if not num:
            num = ["1"]
        if den:
            return " · ".join(num) + " / " + "·".join(den)
        else:
            return " · ".join(num)

    @staticmethod
    def _is_number(x):
        return isinstance(x, (int, float, np.floating)) or isinstance(x, (list, tuple, np.ndarray))

    def _spawn_like(self, cls, sig, si_value):
        """Create an instance of cls (or GenericQuantity) with given SI value & signature."""
        if cls is None:
            # generic fallback
            return GenericQuantity(sig, si_value)
        out = cls.__new__(cls)  # bypass __init__ to set SI directly
        # call __init__ to build conversions dicts
        cls.__init__(out)
        object.__setattr__(out, "_sig", dict(sig))
        object.__setattr__(out, "_Unit__value_si", si_value)
        return out

    # -------------------------
    # Comparisons (element-wise)
    # -------------------------
    def __eq__(self, other):
        if isinstance(other, Unit):
            if _normalize_sig(self._sig) != _normalize_sig(other._sig):
                return NotImplemented
            return np.equal(self._get_value_si(), other._get_value_si())
        if self._is_number(other):
            # interpret scalar in this object's SI
            return np.equal(self._get_value_si(), np.asarray(other, dtype=float))
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Unit):
            if _normalize_sig(self._sig) != _normalize_sig(other._sig):
                return NotImplemented
            return np.less(self._get_value_si(), other._get_value_si())
        if self._is_number(other):
            return np.less(self._get_value_si(), np.asarray(other, dtype=float))
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, Unit):
            if _normalize_sig(self._sig) != _normalize_sig(other._sig):
                return NotImplemented
            return np.less_equal(self._get_value_si(), other._get_value_si())
        if self._is_number(other):
            return np.less_equal(self._get_value_si(), np.asarray(other, dtype=float))
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Unit):
            if _normalize_sig(self._sig) != _normalize_sig(other._sig):
                return NotImplemented
            return np.greater(self._get_value_si(), other._get_value_si())
        if self._is_number(other):
            return np.greater(self._get_value_si(), np.asarray(other, dtype=float))
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, Unit):
            if _normalize_sig(self._sig) != _normalize_sig(other._sig):
                return NotImplemented
            return np.greater_equal(self._get_value_si(), other._get_value_si())
        if self._is_number(other):
            return np.greater_equal(self._get_value_si(), np.asarray(other, dtype=float))
        return NotImplemented

    # -------------------------
    # Arithmetic within same dimension (+/-) or numeric
    # -------------------------
    def __add__(self, other):
        if isinstance(other, Unit):
            if _normalize_sig(self._sig) != _normalize_sig(other._sig):
                return NotImplemented
            si = self._get_value_si() + other._get_value_si()
        elif self._is_number(other):
            si = self._get_value_si() + np.asarray(other, dtype=float)
        else:
            return NotImplemented
        return self._spawn_like(self.__class__, self._sig, si)

    def __sub__(self, other):
        if isinstance(other, Unit):
            if _normalize_sig(self._sig) != _normalize_sig(other._sig):
                return NotImplemented
            si = self._get_value_si() - other._get_value_si()
        elif self._is_number(other):
            si = self._get_value_si() - np.asarray(other, dtype=float)
        else:
            return NotImplemented
        return self._spawn_like(self.__class__, self._sig, si)

    def __radd__(self, other):
        if self._is_number(other):
            return self + other
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, Unit):
            if _normalize_sig(self._sig) != _normalize_sig(other._sig):
                return NotImplemented
            si = other._get_value_si() - self._get_value_si()
            return self._spawn_like(self.__class__, self._sig, si)
        if self._is_number(other):
            si = np.asarray(other, dtype=float) - self._get_value_si()
            return self._spawn_like(self.__class__, self._sig, si)
        return NotImplemented

    def __iadd__(self, other):
        return self.__class__.__add__(self, other)

    def __isub__(self, other):
        return self.__class__.__sub__(self, other)

    # -------------------------
    # Dimensional multiply / divide
    # -------------------------
    def __mul__(self, other):
        if self._is_number(other):
            si = self._get_value_si() * np.asarray(other, dtype=float)
            return self._spawn_like(self.__class__, self._sig, si)
        if isinstance(other, Unit):
            new_sig = _add_sig(self._sig, other._sig, +1)
            si = self._get_value_si() * other._get_value_si()
            # lookup implemented type
            cls = _DERIVED_REGISTRY.get(_normalize_sig(new_sig))
            return self._spawn_like(cls, new_sig, si)
        return NotImplemented

    def __truediv__(self, other):
        if self._is_number(other):
            si = self._get_value_si() / np.asarray(other, dtype=float)
            return self._spawn_like(self.__class__, self._sig, si)
        if isinstance(other, Unit):
            new_sig = _add_sig(self._sig, other._sig, -1)
            si = self._get_value_si() / other._get_value_si()
            cls = _DERIVED_REGISTRY.get(_normalize_sig(new_sig))
            return self._spawn_like(cls, new_sig, si)
        return NotImplemented


    # ------------------------
    # len()
    # ------------------------

    def __len__(self):
        """Return the length of the underlying array, or 1 if scalar."""
        val = self._get_value_si()
        try:
            return len(val)
        except TypeError:
            return 1


# -------------------------------------------
# Base conversions for composing generics
# -------------------------------------------

def _base_conversions():
    """Return the base unit dictionaries used to build generics."""
    return {
        'L': Length()._conversions,
        'T': Time()._conversions,
        'M': Mass()._conversions,
        'Ω': SolidAngle()._conversions,
        'N': Counts()._conversions,
    }

def _compose_unit_name(sig: dict) -> str:
    """Generate a canonical unit name like 'kg_m3_s_sr' for the signature."""
    order = ['M', 'L', 'T', 'Ω', 'N']  # mass, length, time, solid angle, counts
    parts = []
    sym_si = {'M':'kg','L':'m','T':'s','Ω':'sr','N':'count'}
    for key in order:
        exp = sig.get(key, 0)
        if exp:
            u = sym_si[key]
            if abs(exp) == 1:
                parts.append(u)
            else:
                parts.append(f"{u}{abs(exp)}")
    return "_".join(parts) if parts else "dimensionless"

def _generate_conversions_from_signature(sig: dict) -> dict:
    """
    Build a conversions table for a composite signature by multiplying the
    base unit dictionaries to the appropriate powers. Names are concatenated
    with exponents, e.g. 'kg_m3_s_sr'.
    """
    bases = _base_conversions()
    # Build a list of (dim, exponent, dict) for nonzero exponents
    dims = [(d, sig[d], bases[d]) for d in sig if sig[d] != 0 and d in bases]
    if not dims:
        # dimensionless: allow a simple scalar '1'
        return {"": 1.0}

    # For each dimension, list all unit keys raised to |exp|
    name_lists = []
    factor_lists = []
    for d, exp, conv in dims:
        keys = list(conv.keys())
        # name with exponent (e.g. 'cm2'), factor to the power (positive or negative)
        names = [f"{k}{abs(exp) if abs(exp) != 1 else ''}" for k in keys]
        if exp > 0:
            facs = [conv[k] ** exp for k in keys]
        else:
            facs = [(conv[k] ** (-exp)) ** -1 for k in keys]  # 1/(factor^|exp|)
        name_lists.append(names)
        factor_lists.append(facs)

    conversions = {}
    # Cross product across all dimensions
    for name_tuple, fac_tuple in zip(product(*name_lists), product(*factor_lists)):
        name = "_".join(name_tuple)
        # Multiply all factors together
        fac = 1.0
        for f in fac_tuple:
            fac = fac * f
        conversions[name] = fac
    # Always include a clean SI label:
    conversions[_compose_unit_name(sig)] = 1.0  # ensure SI name exists
    return conversions


# -------------------------
# Generic fallback quantity
# -------------------------

class GenericQuantity(Unit):
    """
    A generic derived quantity with a dynamic signature and conversions composed
    from base unit dictionaries. Returned when no implemented class is registered.
    """
    def __init__(self, sig: dict, si_value):
        conv = _generate_conversions_from_signature(sig)
        si_name = _compose_unit_name(sig)
        super().__init__(conv, si_unit=si_name, sig=sig)
        object.__setattr__(self, "_Unit__value_si", np.asarray(si_value))


# ===================
# Concrete Unit types
# ===================

class Counts(Unit):
    SIG = {'N': 1}
    def __init__(self):
        conversions = {
            "count": 1.0, "counts": 1.0,
            "kcount": 1e3, "Mcount": 1e6, "Gcount": 1e9,
        }
        super().__init__(conversions, si_unit="count")


class Length(Unit):
    SIG = {'L': 1}
    def __init__(self):
        conversions = {
            "m": 1.0, "dm": 0.1, "cm": 0.01, "mm": 0.001,
            "µm": 1e-6, "nm": 1e-9, "pm": 1e-12, "km": 1000.0, "fm": 1e-15,
            "angstrom": const.angstrom, "Å": const.angstrom,
            "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mile": 1609.344, "nmi": 1852.0,
            "mil": 2.54e-5,
            "au": const.au, "ly": const.light_year, "pc": const.parsec,
            "kpc": const.parsec * 1e3, "Mpc": const.parsec * 1e6, "Gpc": const.parsec * 1e9,
        }
        super().__init__(conversions, si_unit="m")


class Time(Unit):
    SIG = {'T': 1}
    def __init__(self):
        conversions = {
            "s": 1.0, "ms": 1e-3, "µs": 1e-6, "ns": 1e-9, "ps": 1e-12, "fs": 1e-15,
            "min": const.minute, "h": const.hour, "day": const.day, "week": const.week,
            "yr": const.year, "kyr": const.year * 1e3, "Myr": const.year * 1e6, "Gyr": const.year * 1e9,
        }
        super().__init__(conversions, si_unit="s")


class Angle(Unit):
    # dimensionless in SI, but we don't use it for dimensional algebra here.
    SIG = {}  # (leave out of the dimension system)
    def __init__(self):
        conversions = {
            "rad": 1.0, "mrad": 1e-3, "µrad": 1e-6,
            "deg": np.deg2rad(1.0), "arcmin": np.deg2rad(1.0 / 60.0),
            "arcsec": np.deg2rad(1.0 / 3600.0), "turn": TAU, "rev": TAU,
            "grad": const.pi / 200.0,
        }
        super().__init__(conversions, si_unit="rad")


class Mass(Unit):
    SIG = {'M': 1}
    def __init__(self):
        conversions = {
            "kg": 1.0,
            "g": 1e-3, "mg": 1e-6, "µg": 1e-9, "ng": 1e-12, "pg": 1e-15, "fg": 1e-18,
            "tonne": 1000.0, "t": 1000.0, "kt": 1e6, "Mt": 1e9, "Gt": 1e12,
            "lb": 0.45359237, "oz": 0.028349523125, "st": 6.35029318,
            "cwt": 50.80234544, "slug": 14.59390294,
            "amu": const.atomic_mass, "Da": const.atomic_mass,
        }
        super().__init__(conversions, si_unit="kg")


class SolidAngle(Unit):
    SIG = {'Ω': 1}
    def __init__(self):
        one_deg_in_rad = np.deg2rad(1.0)
        conversions = {
            "sr": 1.0,
            "deg2": (one_deg_in_rad ** 2),
            "arcmin2": (np.deg2rad(1.0 / 60.0) ** 2),
            "arcsec2": (np.deg2rad(1.0 / 3600.0) ** 2),
            "sphere": 4 * const.pi, "hemisphere": 2 * const.pi,
        }
        super().__init__(conversions, si_unit="sr")


# ==========================
# Implemented derived types
# ==========================

@register_derived
class Density(Unit):
    # mass / volume  -> {'M':1, 'L':-3}
    SIG = {'M': 1, 'L': -3}
    def __init__(self):
        # Build conversions programmatically (mass x length^3)
        mass_units  = Mass()._conversions
        length_units = Length()._conversions  # we'll use L^-3 from length units
        conversions = {}
        for m_name, m_fac in mass_units.items():
            for l_name, l_fac in length_units.items():
                name = f"{m_name}_{l_name}3"  # e.g., kg_m3, g_cm3
                conversions[name] = m_fac / (l_fac ** 3)
        super().__init__(conversions, si_unit="kg_m3")

    @staticmethod
    def explain_units():
        print("Density = mass / volume (SI: kg/m³). Conventional: mass → volume.")


@register_derived
class Flux(Unit):
    # counts / (area * time * solid angle) -> {'N':1,'L':-2,'T':-1,'Ω':-1}
    SIG = {'N': 1, 'L': -2, 'T': -1, 'Ω': -1}
    def __init__(self):
        count_units = Counts()._conversions
        length_units = Length()._conversions
        time_units = Time()._conversions
        omega_units = SolidAngle()._conversions
        conversions = {}
        for c_name, c_fac in count_units.items():
            for l_name, l_fac in length_units.items():
                for t_name, t_fac in time_units.items():
                    for o_name, o_fac in omega_units.items():
                        # area = l^2 -> put ^2 in name
                        name = f"{c_name}_{l_name}2_{t_name}_{o_name}"
                        conversions[name] = c_fac / ( (l_fac**2) * t_fac * o_fac )
        super().__init__(conversions, si_unit="count_m2_s_sr")

    @staticmethod
    def explain_units():
        print("Flux = counts / (area × time × solid angle) (SI: count·m⁻²·s⁻¹·sr⁻¹). "
              "Order (denominator): area → time → solid angle.")


@register_derived
class Area(Unit):
    SIG = {'L': 2}
    def __init__(self):
        conversions = {
            "m2": 1.0,
            "km2": 1e6, "cm2": 1e-4, "mm2": 1e-6, "µm2": 1e-12, "nm2": 1e-18,
            "ha": 1e4, "are": 100.0,
            "in2": (0.0254**2), "ft2": (0.3048**2), "yd2": (0.9144**2),
            "mi2": (1609.344**2), "acre": 4046.8564224,
        }
        super().__init__(conversions, si_unit="m2")


@register_derived
class Volume(Unit):
    SIG = {'L': 3}
    def __init__(self):
        conversions = {
            "m3": 1.0,
            "L": 1e-3, "mL": 1e-6, "cL": 1e-5, "dL": 1e-4, "cm3": 1e-6,
            "mm3": 1e-9, "µL": 1e-9, "dm3": 1e-3, "km3": 1e9,
            "in3": (0.0254**3), "ft3": (0.3048**3), "yd3": (0.9144**3),
            "gal_us": 0.003785411784, "qt_us": 0.000946352946,
            "pt_us": 0.000473176473, "cup_us": 0.0002365882365,
            "fl_oz_us": 2.957352956e-5,
            "gal_imp": 0.00454609, "qt_imp": 0.0011365225,
            "pt_imp": 0.00056826125, "fl_oz_imp": 2.84130625e-5,
        }
        super().__init__(conversions, si_unit="m3")


@register_derived
class Dimensionless(Unit):
    SIG = {}
    def __init__(self):
        conversions = {"": 1.0}  # empty unit
        super().__init__(conversions, si_unit="")



