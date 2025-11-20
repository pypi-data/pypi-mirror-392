"""
Calculates the Luminosity of a simplified, geometrically thin, optically thick
accretion disk based on energy conversion efficiency.
"""
from typing import Union
from .constants import c, G

def accretion_disk(
    mass: Union[int, float],
    radius: Union[int, float],
    mdot: Union[int, float] = 1e18,
    efficiency: Union[int, float] = 0.1
) -> float:
    """
    Calculates the accretion disk luminosity (L) using the efficiency model.

    The formula is: L = efficiency * mdot * c^2
    
    Note: The radius argument is kept for API compatibility with more complex 
    models (like Novikov-Thorne) but is not used in this simplified efficiency
    calculation.

    Args:
        mass: The mass of the black hole (kg). Must be > 0.
        radius: The inner radius of the accretion disk (m). Must be > 0.
        mdot: The mass accretion rate (kg/s). Defaults to 1e18 kg/s (approx 1.5e-8 Solar Masses/year). Must be > 0.
        efficiency: The efficiency (unitless) of converting accreting mass into energy. 
                    Must be between 0.0 (exclusive) and 1.0 (inclusive). Defaults to 0.1.

    Returns:
        The accretion disk luminosity in Watts (W).

    Raises:
        TypeError: If any input is not a number.
        ValueError: If inputs are non-positive or efficiency is out of range.
    """
    # 1. Type and Value Validation
    if not isinstance(mass, (int, float)) or not isinstance(radius, (int, float)):
        raise TypeError("Mass and Radius must be numbers.")
    if not isinstance(mdot, (int, float)) or not isinstance(efficiency, (int, float)):
        raise TypeError("Mdot and Efficiency must be numbers.")
        
    if mass <= 0 or radius <= 0 or mdot <= 0:
        raise ValueError("Mass, Radius, and Mass Accretion Rate (mdot) must be positive, non-zero values.")
    if not (0.0 < efficiency <= 1.0):
        raise ValueError("Efficiency must be between 0.0 (exclusive) and 1.0 (inclusive).")

    # 2. Calculation using the efficiency model
    # L = efficiency * mdot * c^2
    luminosity = efficiency * mdot * (c ** 2)

    # Alternative calculation using gravitational potential approximation (commented out)
    # L_approx = (G * mass * mdot) / (2 * radius) 
    # print(f"Approximation (Gravitational Potential): {L_approx:.3e} W")

    return luminosity

if __name__ == "__main__":
    # Example Usage: Calculate the luminosity of an actively accreting black hole.
    print("--- Accretion Disk Luminosity Calculation Example ---")

    # 1. Standard parameters (10 solar masses, typical accretion rate, 10% efficiency)
    test_mass = 10.0 * 1.98847e30 # 10 Solar Masses in kg
    test_radius = 3.0e4 # Placeholder radius (30 km)
    test_mdot = 1.0e16 # 10^16 kg/s

    luminosity_w = accretion_disk(
        mass=test_mass,
        radius=test_radius,
        mdot=test_mdot,
        efficiency=0.1
    )

    print(f"Input Mass (M): {test_mass:.3e} kg")
    print(f"Input Radius (R): {test_radius:.3e} m")
    print(f"Input Mdot: {test_mdot:.3e} kg/s")
    print(f"Input Efficiency: 0.1")
    print(f"Accretion Luminosity (L): {luminosity_w:.3e} Watts")
    
    # 2. Example with maximum theoretical efficiency (for a Kerr BH)
    luminosity_max = accretion_disk(
        mass=test_mass,
        radius=test_radius,
        mdot=test_mdot,
        efficiency=0.42 # Approx max efficiency for Kerr BH
    )
    print(f"\nMax Efficiency (0.42) Luminosity: {luminosity_max:.3e} Watts")

    # Example 3: Error handling
    try:
        accretion_disk(1e30, 1e4, efficiency=1.1)
    except ValueError as e:
        print(f"\nCaught Expected Error: {e}")