from typing import List, Dict


width=1800
height=2000
length_top=3000
length_bottom=3350

class Surface:

    def __init__(self, dims: Dict[str, int]):

        self.dims = dims

    def get_surface_area(self):

        _surface_area: float = 1.
        for _, dim in self.dims.items():
            _surface_area *= dim

        return _surface_area

def main():

    floor: Surface = Surface({
        "width": 1800,
        "length": 3350,
    })

    ceiling: Surface = Surface({
        "width": 1800,
        "length": 3350,
    })

    left_wall: Surface = Surface({
        "height": 2000,
        "length": 3350,
    })
    
    right_wall: Surface = Surface({
        "height": 2000,
        "length": 3350,
    })

    barn_doors: Surface = Surface({
        "height": 2000,
        "width": 1800,
    })

    surfaces: List[Surface] = [floor, ceiling, left_wall, right_wall, barn_doors]

    print("Total surface area (mm^2)")
    total: float = 0.0
    for surface in surfaces:
        total += surface.get_surface_area()

    print(total, "mm^2")
    print(total* 10**(-3) * 10**(-3) )


if __name__ == "__main__":
    main()
