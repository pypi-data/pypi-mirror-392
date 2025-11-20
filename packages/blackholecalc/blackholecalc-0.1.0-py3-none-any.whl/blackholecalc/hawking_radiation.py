"""
Calculates the Hawking Temperature of a black hole.
"""
from typing import Union
from .constants import G, c, hbar, kB, pi, SOLAR_MASS

def hawking_radiation(mass: Union[int, float]) -> float:
    """
    Calculates the Hawking Temperature (T) of a non-rotating black hole.

    The formula is: T = (hbar * c^3) / (8 * pi * G * k_B * M)

    Args:
        mass: The mass of the black hole (must be > 0). Assumed to be in kilograms (kg).

    Returns:
        The Hawking Temperature in Kelvin (K).

    Raises:
        TypeError: If mass is not a number.
        ValueError: If mass is zero or negative.
    """
    if not isinstance(mass, (int, float)):
        raise TypeError(f"Mass must be a number (int or float), not {type(mass).__name__}")
    if mass <= 0:
        raise ValueError("Mass must be a positive, non-zero value.")

    # T = (hbar * c^3) / (8 * pi * G * k_B * M)
    numerator = hbar * (c ** 3)
    denominator = 8.0 * pi * G * kB * mass

    temperature = numerator / denominator
    return temperature

if __name__ == "__main__":
    # Example Usage: Calculate the Hawking temperature for different masses.
    print("--- Hawking Radiation Calculation Example ---")

    # 1. Stellar Mass Black Hole (10 Solar Masses)
    stellar_mass_kg = 10.0 * SOLAR_MASS
    temp_stellar = hawking_radiation(stellar_mass_kg)

    print("--- Stellar Black Hole Example (10 Solar Masses) ---")
    print(f"Input Mass: {stellar_mass_kg:.3e} kg")
    print(f"Hawking Temperature: {temp_stellar:.4e} Kelvin") # Very small, near absolute zero

    # 2. Primordial Black Hole (approx 10^12 kg, just before evaporation)
    primordial_mass_kg = 1.0e12
    temp_primordial = hawking_radiation(primordial_mass_kg)

    print("\n--- Primordial Black Hole Example (10^12 kg) ---")
    print(f"Input Mass: {primordial_mass_kg:.3e} kg")
    # This is a much higher temperature, illustrating the inverse relationship (smaller mass, hotter BH)
    print(f"Hawking Temperature: {temp_primordial:.4f} Kelvin")

    # Example 3: Error handling
    try:
        hawking_radiation(0)
    except ValueError as e:
        print(f"\nCaught Expected Error: {e}")