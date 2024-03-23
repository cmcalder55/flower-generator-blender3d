import numpy as np

def generate_torus_points(num_points=10):
    """
    Generate points on the surface of a torus in a normal distribution.

    Parameters:
    - R: Major radius of the torus.
    - r: Minor radius of the torus.
    - num_points: Number of points to generate.

    Returns:
    - A list of (x, y, z) tuples representing points on the torus.
    """
    r = 1.2  # Major radius
    R = 0.7  # Minor radius
    # Mean values for theta and phi
    mean_theta = np.pi
    mean_phi = np.pi

    # Standard deviation (spread or “width”) of the distribution.
    # Adjust these values to change the distribution characteristics.
    std_theta = np.pi
    std_phi = np.pi

    z_base = 0.7 # Base Z level for variation
    z_variation = 0.5  # Allowable variation from the base Z level

    # Generate theta and phi values from a normal distribution
    theta = np.random.normal(mean_theta, std_theta, num_points)
    phi = np.random.normal(mean_phi, std_phi, num_points)

    # Ensure theta and phi are within the valid range [0, 2pi]
    theta = np.mod(theta, 2 * np.pi)
    phi = np.mod(phi, 2 * np.pi)

    # Calculate the x, y, and z coordinates
    x = (R + r * np.cos(theta)) * np.cos(phi) - 0.5
    y = (R + r * np.cos(theta)) * np.sin(phi) #+ 1.5
    z = z_base + np.random.uniform(-z_variation, z_variation)  # Random Z level

    # Return the points as a list of tuples
    return list(zip(x, y, z))

# Example usage:

points = generate_torus_points()
for point in points:
    print(point)