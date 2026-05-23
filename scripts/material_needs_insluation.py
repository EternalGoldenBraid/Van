from dataclasses import dataclass
import math
from typing import List, Dict, Optional, Tuple


width=1800
height=2000
length_top=3000
length_bottom=3350

class Surface:
    """
    A rectangular surface area (in mm dims) used to estimate coverage needs.

    This is intentionally a simplification: real vans have ribs, curves, windows,
    cutouts, and partial coverage. Treat the output as a planning baseline.
    """

    def __init__(self, dims: Dict[str, int]):

        self.dims = dims

    def get_surface_area(self):
        """
        Returns area in mm^2 by multiplying the dimensions in `dims`.

        Example:
          {"width": 1800, "length": 3350} -> 1800 * 3350 mm^2
        """

        _surface_area: float = 1.
        for _, dim in self.dims.items():
            _surface_area *= dim

        return _surface_area


@dataclass
class Material:
    """
    A purchasable material item.

    `unit_coverage_m2` means:
      The surface area (in m^2) covered by ONE unit you buy.

    Examples:
    - 1 sheet of 1m x 1m foam -> unit_coverage_m2 = 1.0
    - 1 XPS board 600mm x 2500mm -> 0.6 * 2.5 = 1.5 m^2
    - 1 butyl pack containing multiple tiles totaling 0.18 m^2 -> 0.18

    The calculator uses:
      units_needed = ceil((surface_m2 * coverage_ratio) / unit_coverage_m2)
    """

    name: str
    url: Optional[str]
    unit_name: str
    unit_coverage_m2: float
    unit_price_eur: Optional[float]
    unit_dims_mm: Optional[Tuple[int, int, int]] = None


@dataclass
class MaterialNeed:
    """
    A material applied to a surface.

    `coverage_ratio`:
      Fraction of the surface area you plan to cover with this material.

    Examples:
    - Full coverage layer (foam, XPS): coverage_ratio = 1.0
    - Patch sound damping: coverage_ratio = 0.20 .. 0.50
    """

    material: Material
    coverage_ratio: float = 1.0  # 1.0 = cover the full surface area
    note: Optional[str] = None


def units_needed(surface_m2: float, need: MaterialNeed) -> int:
    target_m2 = max(0.0, surface_m2 * float(need.coverage_ratio))
    if need.material.unit_coverage_m2 <= 0:
        raise ValueError("unit_coverage_m2 must be > 0")
    return int(math.ceil(target_m2 / float(need.material.unit_coverage_m2)))


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

    walls: List[Surface] = [left_wall, right_wall]
    doors: List[Surface] = [barn_doors]
    surfaces: List[Surface] = [floor, ceiling] + walls + doors

    def sum_area_mm2(items: List[Surface]) -> float:
        total: float = 0.0
        for surface in items:
            total += surface.get_surface_area()
        return total

    floor_mm2 = sum_area_mm2([floor])
    ceiling_mm2 = sum_area_mm2([ceiling])
    walls_mm2 = sum_area_mm2(walls)
    doors_mm2 = sum_area_mm2(doors)
    total_mm2 = sum_area_mm2(surfaces)

    def mm2_to_m2(mm2: float) -> float:
        return mm2 * 10**(-3) * 10**(-3)

    floor_m2 = mm2_to_m2(floor_mm2)
    ceiling_m2 = mm2_to_m2(ceiling_mm2)
    walls_m2 = mm2_to_m2(walls_mm2)
    doors_m2 = mm2_to_m2(doors_mm2)

    print("Surface area summary")
    print("  floor:  ", floor_mm2, "mm^2  |", floor_m2, "m^2")
    print("  ceiling:", ceiling_mm2, "mm^2  |", ceiling_m2, "m^2")
    print("  walls:  ", walls_mm2, "mm^2  |", walls_m2, "m^2")
    print("  doors:  ", doors_mm2, "mm^2  |", doors_m2, "m^2")
    print("  total:  ", total_mm2, "mm^2  |", mm2_to_m2(total_mm2), "m^2")
    print()

    # Materials (edit these values for your shopping list)
    m_butyl = Material(
        name="CTK alumiinibutyylivaimennusmatto (2mm)",
        url="https://www.motonet.fi/tuote/ctk-practic-alumiinibutyylivaimennusmattosarja-018-x-40-x-25-cm?product=65-05166",
        unit_name="pack",
        unit_coverage_m2=0.18,
        unit_price_eur=24.90,
        unit_dims_mm=(400, 250, 2),
    )
    m_ccf = Material(
        name="NMC solukumieriste liimalla (6mm)",
        url="https://www.puuilo.fi/nmc-solukumieriste-liimalla-6mm-x-1m-x-1m",
        unit_name="sheet",
        unit_coverage_m2=1.0,
        unit_price_eur=None,
        unit_dims_mm=(1000, 1000, 6),
    )
    m_xps = Material(
        name="Finnfoam FI-300 XPS (25mm)",
        url="https://www.k-rauta.fi/tuote/eristyslevy-finnfoam-fi-300-20x600x2500-suorareunainen/6418711190639",
        unit_name="board",
        unit_coverage_m2=0.6 * 2.5,
        unit_price_eur=None,
        unit_dims_mm=(600, 2500, 25),
    )
    m_plywood = Material(
        name="Plywood (owned)",
        url=None,
        unit_name="sheet",
        unit_coverage_m2=1.25 * 2.5,
        unit_price_eur=0.0,
        unit_dims_mm=(1250, 2500, 12),
    )

    # Per-surface needs. Keep this minimal: ratio covers partial coverage cases.
    needs_by_surface: Dict[str, List[MaterialNeed]] = {
        "floor": [
            MaterialNeed(m_butyl, coverage_ratio=0.30, note="optional; patch coverage"),
            MaterialNeed(m_ccf, coverage_ratio=1.00),
            MaterialNeed(m_xps, coverage_ratio=1.00),
            MaterialNeed(m_plywood, coverage_ratio=1.00),
        ],
        "walls": [
            MaterialNeed(m_butyl, coverage_ratio=0.30, note="patch coverage"),
            MaterialNeed(m_ccf, coverage_ratio=1.00),
        ],
        "ceiling": [
            MaterialNeed(m_butyl, coverage_ratio=0.20, note="optional; patch coverage"),
            MaterialNeed(m_ccf, coverage_ratio=1.00),
        ],
        "doors": [
            MaterialNeed(m_butyl, coverage_ratio=0.30, note="patch coverage"),
            MaterialNeed(m_ccf, coverage_ratio=1.00),
        ],
    }

    def print_surface_needs(surface_name: str, surface_m2: float) -> float:
        print("-"*30)
        print(f"{surface_name} ({surface_m2:.2f} m^2)")
        subtotal = 0.0
        for need in needs_by_surface.get(surface_name, []):
            print()
            units = units_needed(surface_m2, need)
            if need.material.unit_price_eur is None:
                cost = None
            else:
                cost = units * float(need.material.unit_price_eur)
                subtotal += cost
            dims = ""
            if need.material.unit_dims_mm is not None:
                w, h, t = need.material.unit_dims_mm
                dims = f" [{w}x{h}x{t}mm]"
            note = "" if need.note is None else f" ({need.note})"
            price = "unknown" if need.material.unit_price_eur is None else f"{need.material.unit_price_eur:.2f} EUR"
            print(f"  - {need.material.name}{note}")
            line = f"    {units} x {need.material.unit_name}{dims} (covers {need.material.unit_coverage_m2:.2f} m^2 each, {price})"
            if cost is None:
                line += " -> unknown EUR"
            else:
                line += f" -> {cost:.2f} EUR"
            print(line)
            if need.material.url:
                print(f"    {need.material.url}")
        print(f"  {surface_name} subtotal: {subtotal:.2f} EUR")
        print("-"*30,"\n")
        return subtotal

    grand = 0.0
    grand += print_surface_needs("floor", floor_m2)
    grand += print_surface_needs("walls", walls_m2)
    grand += print_surface_needs("ceiling", ceiling_m2)
    grand += print_surface_needs("doors", doors_m2)
    print(f"Grand total (known prices only): {grand:.2f} EUR")


if __name__ == "__main__":
    main()
