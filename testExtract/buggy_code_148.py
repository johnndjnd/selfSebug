def bf(planet1, planet2):
    planet_names = ("Mercury", "Venus", "Earth", "Mars", "Jupyter", "Saturn", "Uranus", "Neptune")
    if planet1 not in planet_names or planet2 not in planet_names or planet1 == planet2:
        return ()
    planet1_index = planet_names.index(planet1)
    planet2_index = planet_names.index(planet2)
    if planet1_index < planet2_index:
        return (planet_names[planet1_index + 1: planet2_index])
    else:
        return (planet_names[planet2_index + 1 : planet1_index])


def bf(planet1, planet2):
    planet_names = ("Mercury", "Venus", "Earth", "Mars", "Jupyter", "Saturn", "Uranus", "Neptune")
    x2 = planet1 not in planet_names
    x3 = planet2 not in planet_names
    x4 = x2 or x3
    x5 = planet1 == planet2
    x6 = x4 or x5
    if x6:
        x7 = ()
        return x7
    planet1_index = planet_names.index(planet1)
    planet2_index = planet_names.index(planet2)
    x10 = planet1_index < planet2_index
    if x10:
        x11 = planet1_index + 1
        x12 = planet_names[x11:planet2_index]
        return x12
    else:
        x13 = planet2_index + 1
        x14 = planet_names[x13:planet1_index]
        return x14