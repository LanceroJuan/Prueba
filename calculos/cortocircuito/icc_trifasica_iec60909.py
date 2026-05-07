"""
Cálculo de corriente de cortocircuito trifásica según IEC 60909.

Fórmulas aplicadas:
    I"k3 = (c · Un) / (√3 · |Zk|)      [A]
    S"k  = √3 · Un · I"k3               [VA]

Donde:
    Un  — tensión nominal de la barra (fase-fase) [kV]
    Zk  — impedancia de Thevenin vista desde la barra [Ω]
    c   — factor de tensión según IEC 60909-0 Tabla 1
          (típicamente 1,05 o 1,10 para máxima; 0,95 para mínima)
"""

import math


def calcular_icc_trifasica(un_kv: float, zk_ohm: complex, c: float) -> dict:
    """
    Calcula la corriente de cortocircuito trifásica inicial (I"k3) y la
    potencia de cortocircuito (S"k) según IEC 60909.

    Parámetros
    ----------
    un_kv   : Tensión nominal de la barra en kV (valor de línea).
    zk_ohm  : Impedancia de Thevenin en Ω (puede ser compleja R + jX).
    c       : Factor de tensión IEC 60909 (sin unidades).

    Retorna
    -------
    dict con Icc_kA, Scc_MVA, Zk_ohm y factor_c.
    """
    if un_kv <= 0:
        raise ValueError("La tensión nominal debe ser mayor que cero.")
    if abs(zk_ohm) == 0:
        raise ValueError("La impedancia de Thevenin no puede ser cero.")
    if c <= 0:
        raise ValueError("El factor c debe ser mayor que cero.")

    un_v = un_kv * 1e3                        # kV → V
    zk_mod = abs(zk_ohm)                      # módulo de Zk [Ω]

    icc_a = (c * un_v) / (math.sqrt(3) * zk_mod)   # I"k3 [A]
    scc_va = math.sqrt(3) * un_v * icc_a            # S"k  [VA]

    return {
        "Icc_kA": icc_a / 1e3,
        "Scc_MVA": scc_va / 1e6,
        "Zk_ohm": zk_ohm,
        "Zk_mod_ohm": zk_mod,
        "factor_c": c,
        "Un_kV": un_kv,
    }


def pedir_complejo(prompt: str) -> complex:
    """Lee un número complejo desde consola en formato 'R+Xj' o solo 'R'."""
    valor = input(prompt).strip().replace(" ", "").replace(",", ".")
    try:
        return complex(valor)
    except ValueError:
        raise ValueError(
            f"Formato inválido: '{valor}'. Use p.ej. '0.5+2.3j' o '2.5'."
        )


def main():
    print("=" * 55)
    print("  Cortocircuito trifásico — IEC 60909")
    print("=" * 55)

    try:
        un_kv = float(
            input("Tensión nominal de la barra Un [kV]: ")
            .replace(",", ".")
        )
        zk_ohm = pedir_complejo(
            "Impedancia de Thevenin Zk [Ω]  (ej. 0.5+2.3j): "
        )
        c = float(
            input("Factor de tensión c (ej. 1.0 / 1.05 / 1.10): ")
            .replace(",", ".")
        )

        res = calcular_icc_trifasica(un_kv, zk_ohm, c)

    except ValueError as e:
        print(f"\nError en los datos de entrada: {e}")
        return

    print()
    print("-" * 55)
    print("  RESULTADOS")
    print("-" * 55)
    print(f"  Tensión nominal          Un  = {res['Un_kV']:.3f} kV")
    print(f"  Impedancia Thevenin      Zk  = {res['Zk_ohm']}  Ω")
    print(f"  Módulo de Zk            |Zk| = {res['Zk_mod_ohm']:.4f} Ω")
    print(f"  Factor de tensión         c  = {res['factor_c']}")
    print("-" * 55)
    print(f"  Corriente cortocircuito  I\"k3 = {res['Icc_kA']:.4f} kA")
    print(f"  Potencia cortocircuito   S\"k  = {res['Scc_MVA']:.2f} MVA")
    print("-" * 55)


if __name__ == "__main__":
    main()
