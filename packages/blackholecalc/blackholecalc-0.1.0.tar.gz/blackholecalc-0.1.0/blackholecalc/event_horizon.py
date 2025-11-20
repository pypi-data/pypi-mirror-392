"""
Calculates the Event Horizon radius for both non-rotating (Schwarzschild)
and rotating (Kerr) black holes.
"""
from typing import Union
import math
from .constants import G, c, SOLAR_MASS

def event_horizon(
    mass: Union[int, float], 
    spin_param: Union[int, float] = 0.0
) -> float:
    """
    Calculates the outer event horizon radius (r_+) of a black hole 
    (Schwarzschild for spin=0, Kerr for spin > 0).

    The formula for the outer event horizon (Kerr metric) is:
    r_+ = R_g * (1 + sqrt(1 - a*^2))
    where R_g = G * M / c^2 (Gravitational Radius) and a* is the dimensionless 
    spin parameter (spin_param).

    Args:
        mass: The mass of the black hole (must be > 0) in kilograms (kg).
        spin_param: The dimensionless spin parameter (a/M or a*). 
                    Must be between 0.0 (non-rotating) and 1.0 (extremal Kerr).
                    Defaults to 0.0.

    Returns:
        The outer event horizon radius (r_+) in meters (m).

    Raises:
        TypeError: If mass or spin_param is not a number.
        ValueError: If mass is non-positive or spin_param is outside [0, 1].
    """
    # 1. Type and Value Validation
    if not isinstance(mass, (int, float)) or not isinstance(spin_param, (int, float)):
        raise TypeError("Mass and spin_param must be numbers (int or float).")
    if mass <= 0:
        raise ValueError("Mass must be a positive, non-zero value.")
    if not (0.0 <= spin_param <= 1.0):
        raise ValueError("The dimensionless spin parameter must be between 0.0 (Schwarzschild) and 1.0 (Extremal Kerr).")

    # Gravitational Radius: R_g = G * M / c^2
    gravitational_radius = G * mass / (c ** 2)
    
    # Inner term under the square root: 1 - a*^2
    root_term = 1.0 - (spin_param ** 2)
    
    # Outer Event Horizon (r_+): R_g * (1 + sqrt(1 - a*^2))
    # Note: If spin_param is 0, r_+ = R_g * (1 + 1) = 2 * R_g, which is the Schwarzschild radius.
    radius = gravitational_radius * (1.0 + math.sqrt(root_term))
    
    return radius

if __name__ == "__main__":
    # Example Usage: Calculate the event horizon radius for different scenarios.
    print("--- Event Horizon Calculation Example ---")
    
    solar_mass_kg = SOLAR_MASS
    
    # 1. Schwarzschild Black Hole (non-rotating, spin_param = 0.0)
    rs_schwarzschild = event_horizon(mass=solar_mass_kg, spin_param=0.0)
    print("--- 1 Solar Mass: Schwarzschild (Spin=0.0) ---")
    print(f"Input Mass: {solar_mass_kg:.3e} kg")
    print(f"Event Horizon Radius (r_s): {rs_schwarzschild:.4f} meters ({rs_schwarzschild/1000:.4f} km)")
    
    # 2. Kerr Black Hole (moderately rotating, spin_param = 0.5)
    rs_kerr_moderate = event_horizon(mass=solar_mass_kg, spin_param=0.5)
    print("\n--- 1 Solar Mass: Kerr (Spin=0.5) ---")
    print(f"Input Spin Parameter (a*): 0.5")
    print(f"Event Horizon Radius (r_+): {rs_kerr_moderate:.4f} meters ({rs_kerr_moderate/1000:.4f} km)")
    
    # 3. Extremal Kerr Black Hole (max rotation, spin_param = 1.0)
    rs_kerr_max = event_horizon(mass=solar_mass_kg, spin_param=1.0)
    print("\n--- 1 Solar Mass: Extremal Kerr (Spin=1.0) ---")
    print(f"Input Spin Parameter (a*): 1.0")
    print(f"Event Horizon Radius (r_+): {rs_kerr_max:.4f} meters ({rs_kerr_max/1000:.4f} km)")
    
    # Note: The radius shrinks as the spin increases (from 2Rg to 1Rg)

    # Example 4: Error handling
    try:
        event_horizon(1e30, 1.1)
    except ValueError as e:
        print(f"\nCaught Expected Error: {e}")