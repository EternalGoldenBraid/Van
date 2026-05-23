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
    units: Optional[int] = None  # if set, use this count directly
    note: Optional[str] = None
    optional: bool = False


def units_needed(surface_m2: float, need: MaterialNeed) -> int:
    if need.units is not None:
        return int(need.units)
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
        name="CTK Practic 2.0 alumiini/butyylivaimennusmatto (2.96 m^2 box, 2.0mm)",
        url="https://www.motonet.fi/tuote/ctk-practic-20-alumiinibutyylivaimennusmatto-20-mm-296-m?product=65-03543",
        unit_name="box",
        unit_coverage_m2=2.96,
        unit_price_eur=79.90,
        unit_dims_mm=(500, 370, 2),
    )
    m_ccf_6 = Material(
        name="NMC solukumieriste liimalla (6mm)",
        url="https://www.puuilo.fi/nmc-solukumieriste-liimalla-6mm-x-1m-x-1m",
        unit_name="sheet",
        unit_coverage_m2=1.0,
        unit_price_eur=29.99,
        unit_dims_mm=(1000, 1000, 6),
    )
    m_ccf_13 = Material(
        name="NMC solukumieriste liimalla (6mm)",
        url="https://www.puuilo.fi/nmc-solukumieriste-liimalla-13mm-x-1m-x-1m",
        unit_name="sheet",
        unit_coverage_m2=1.0,
        unit_price_eur=38.99,
        unit_dims_mm=(1000, 1000, 13),
    )
    m_pir = Material(
        name="PIR board",
        url="https://www.stark-suomi.fi/tuote/eristelevy-ff-pir-30-alk-30x600x2400-mm-1-44-m2-12gn",
        unit_name="board",
        unit_coverage_m2=0.6 * 2.4,
        unit_price_eur=29.15,
        unit_dims_mm=(600, 2400, 30),
    )
    m_xps_underfloor_heating = Material(
        name="Topaway XPS-lattialämmitys",
        url="https://www.topway.fi/product/63/lattialammityslevy-topway-16mm",
        unit_name="board",
        unit_coverage_m2=0.6 * 1.2,
        unit_price_eur=18.90,
        unit_dims_mm=(600, 1200, 25),
    )
    m_xps = Material(
        name="Finnfoam XPS",
        url="https://www.k-rauta.fi/tuote/eristyslevy-finnfoam-fi-300-30x600x2500-suorareunainen/6418711190431",
        unit_name="board",
        unit_coverage_m2=0.6 * 2.5,
        unit_price_eur=14.20,
        unit_dims_mm=(600, 2500, 30),
    )
    m_batten_33 = Material(
        name="Hoylatty Cello 33x33x2400 (US 1-3 manty)",
        url="https://www.k-rauta.fi/tuote/hoylatty-cello-33x33x2400-us-1-3-manty/6420611090315",
        unit_name="pc",
        unit_coverage_m2=0.033 * 2.4,
        unit_price_eur=9.19,
        unit_dims_mm=(33, 2400, 33),
    )
    m_plywood = Material(
        name="Plywood (owned)",
        url=None,
        unit_name="sheet",
        unit_coverage_m2=1.25 * 2.5,
        unit_price_eur=0.0,
        unit_dims_mm=(1250, 2500, 12),
    )
    
    m_wool = Material(
        name="Organic wool",
        url="https://www.k-rauta.fi/tuote/eristyslevy-ekovilla-50x565x870mm-59m/6419412110506",
        unit_name="sheet",
        unit_coverage_m2=0.565 * 0.870,
        unit_price_eur=0.0,
        unit_dims_mm=(565, 870, 50),
    )

    # Aux / tools / consumables for the floor job (buy counts are placeholders).
    a_step_drill = Material(
        name="Step drill bit (askelpora) HSS 4-10mm",
        url="https://www.puuilo.fi/wolfcraft-askelpora-hss-4-10mm",
        unit_name="pc",
        unit_coverage_m2=1.0,
        unit_price_eur=9.99,
        unit_dims_mm=None,
    )
    a_rivet_pliers = Material(
        name="Pop rivet pliers (vetoniittipihdit) 360",
        url="https://www.puuilo.fi/finbullet-vetoniittipihdit-360",
        unit_name="pc",
        unit_coverage_m2=1.0,
        unit_price_eur=17.99,
        unit_dims_mm=None,
    )
    a_rivets_assort = Material(
        name="Pop rivet assortment 220 pcs",
        url="https://www.puuilo.fi/promaster-popniittilajitelma-220-os",
        unit_name="box",
        unit_coverage_m2=1.0,
        unit_price_eur=6.99,
        unit_dims_mm=None,
    )
    a_rust_converter = Material(
        name="Rust converter (ruosteenmuunnin) CRC Rust Seal 750ml",
        url="https://www.puuilo.fi/crc-rust-seal-ruosteenmuunnin-750ml",
        unit_name="can",
        unit_coverage_m2=1.0,
        unit_price_eur=74.90,
        unit_dims_mm=None,
    )
    a_metal_primer = Material(
        name="Primer spray: aluminum/galvanized metal 400ml",
        url="https://www.puuilo.fi/maston-pohjamaalispray-alumiini-galvanoitu-metalli-400ml",
        unit_name="can",
        unit_coverage_m2=1.0,
        unit_price_eur=8.99,
        unit_dims_mm=None,
    )
    a_metal_topcoat = Material(
        name="Metal topcoat spray 400ml (Maston Hammer)",
        url="https://www.puuilo.fi/maston-hammer-spraymaali-400ml-silea-musta",
        unit_name="can",
        unit_coverage_m2=1.0,
        unit_price_eur=10.99,
        unit_dims_mm=None,
    )
    a_alu_tape = Material(
        name="Aluminum tape 50mm x 25m",
        url="https://www.puuilo.fi/tarmo-alumiiniteippi-50mmx25m",
        unit_name="roll",
        unit_coverage_m2=1.0,
        unit_price_eur=5.99,
        unit_dims_mm=None,
    )
    a_masking_tape = Material(
        name="Masking tape 38mm x 50m",
        url="https://www.puuilo.fi/telpak-maalarinteippi-ammattilaatu-38mm-50m",
        unit_name="roll",
        unit_coverage_m2=1.0,
        unit_price_eur=2.99,
        unit_dims_mm=None,
    )
    a_foam = Material(
        name="PU foam (pistoolivaahto) 750ml",
        url="https://www.puuilo.fi/wurth-megafoam-pistoolivaahto-750ml",
        unit_name="can",
        unit_coverage_m2=1.0,
        unit_price_eur=7.49,
        unit_dims_mm=None,
    )
    a_pencil = Material(
        name="Carpenter pencil (timpurinkynä)",
        url="https://www.puuilo.fi/blackedge-timpurinkyna-soft",
        unit_name="pc",
        unit_coverage_m2=1.0,
        unit_price_eur=1.00,
        unit_dims_mm=None,
    )
    a_respirator = Material(
        name="Half mask respirator (puolinaamari) Moldex 7002 M",
        url="https://www.puuilo.fi/moldex-7002-puolinaamari-koko-m",
        unit_name="pc",
        unit_coverage_m2=1.0,
        unit_price_eur=27.99,
        unit_dims_mm=None,
    )
    a_filter_p3 = Material(
        name="Respirator particle filter P3 (Moldex 903012)",
        url="https://www.puuilo.fi/moldex-903012-hiukkassuodatin-p3-r-d",
        unit_name="pc",
        unit_coverage_m2=1.0,
        unit_price_eur=15.49,
        unit_dims_mm=None,
    )
    a_wire_cup_brush = Material(
        name="Wire cup brush for drill (kuppiharja) 75mm RST",
        url="https://www.puuilo.fi/wolfcraft-kuppiharja-rst-75mm",
        unit_name="pc",
        unit_coverage_m2=1.0,
        unit_price_eur=8.99,
        unit_dims_mm=None,
    )
    a_metal_drill_bit_series = Material(
        name="Metal drill bits 1.5-6mm",
        url="https://www.puuilo.fi/promaster-metalliporanterasarja-5-os",
        unit_name="pc",
        unit_coverage_m2=1.0,
        unit_price_eur=5.99,
        unit_dims_mm=None,
    )

    # Per-surface needs. Keep this minimal: ratio covers partial coverage cases.
    needs_by_surface: Dict[str, List[MaterialNeed]] = {
        "floor": [
            MaterialNeed(m_butyl, coverage_ratio=0.20, note="optional; patch coverage"),
            MaterialNeed(m_ccf_6, coverage_ratio=1.00),
            # MaterialNeed(m_xps_underfloor_heating, coverage_ratio=1.00),
            MaterialNeed(m_xps, coverage_ratio=1.00),
            MaterialNeed(m_batten_33, units=9, note="batten estimate"),
            MaterialNeed(m_plywood, coverage_ratio=1.00),
        ],
        "floor_aux": [
            MaterialNeed(a_step_drill, units=1),
            MaterialNeed(a_rivet_pliers, units=1),
            MaterialNeed(a_rivets_assort, units=1),
            MaterialNeed(a_wire_cup_brush, units=1),
            MaterialNeed(a_rust_converter, units=1, optional=True, note="If persistent rust."),
            MaterialNeed(a_metal_primer, units=1),
            MaterialNeed(a_metal_topcoat, units=1),
            MaterialNeed(a_alu_tape, units=2),
            MaterialNeed(a_masking_tape, units=1),
            MaterialNeed(a_foam, units=1, optional=True, note="for XPS gaps / air sealing"),
            MaterialNeed(a_pencil, units=1),
            MaterialNeed(a_filter_p3, units=1),
            MaterialNeed(a_metal_drill_bit_series, units=1),
        ],
        "walls": [
            MaterialNeed(m_butyl, coverage_ratio=0.30, note="patch coverage"),
            MaterialNeed(m_ccf_13, coverage_ratio=1.00),
            MaterialNeed(m_pir, coverage_ratio=1.00),
            MaterialNeed(m_wool, coverage_ratio=0.30),
        ],
        "ceiling": [
            MaterialNeed(m_butyl, coverage_ratio=0.20, note="optional; patch coverage"),
            MaterialNeed(m_ccf_13, coverage_ratio=1.00),
            MaterialNeed(m_pir, coverage_ratio=1.00),
            MaterialNeed(m_wool, coverage_ratio=1.00),
        ],
        "doors": [
            MaterialNeed(m_butyl, coverage_ratio=0.30, note="patch coverage"),
            MaterialNeed(m_ccf_6, coverage_ratio=1.00),
            MaterialNeed(m_wool, coverage_ratio=1.00),
        ],
    }

    def print_surface_needs(surface_name: str, surface_m2: float) -> Tuple[float, float]:
        print("-"*30)
        print(f"{surface_name} ({surface_m2:.2f} m^2)")
        subtotal_min = 0.0
        subtotal_max = 0.0
        for need in needs_by_surface.get(surface_name, []):
            print()
            units = units_needed(surface_m2, need)
            if need.material.unit_price_eur is None:
                cost = None
            else:
                cost = units * float(need.material.unit_price_eur)
                subtotal_max += cost
                if not need.optional:
                    subtotal_min += cost
            dims = ""
            if need.material.unit_dims_mm is not None:
                w, h, t = need.material.unit_dims_mm
                dims = f" [{w}x{h}x{t}mm]"
            note = "" if need.note is None else f" ({need.note})"
            optional = " [optional]" if need.optional else ""
            price = "unknown" if need.material.unit_price_eur is None else f"{need.material.unit_price_eur:.2f} EUR"
            print(f"  - {need.material.name}{optional}{note}")
            if need.material.unit_coverage_m2 is None:
                coverage = "n/a"
            else:
                coverage = f"{need.material.unit_coverage_m2:.2f} m^2"
            line = f"    {units} x {need.material.unit_name}{dims} (covers {coverage} each, {price})"
            if cost is None:
                line += " -> unknown EUR"
            else:
                line += f" -> {cost:.2f} EUR"
            print(line)
            if need.material.url:
                print(f"    {need.material.url}")
        print(f"  {surface_name} subtotal min..max: {subtotal_min:.2f} .. {subtotal_max:.2f} EUR")
        print("-"*30,"\n")
        return subtotal_min, subtotal_max

    grand_min = 0.0
    grand_max = 0.0
    for surface_name, surface_m2 in [
        ("floor", floor_m2),
        ("floor_aux", floor_m2),
        ("walls", walls_m2),
        ("ceiling", ceiling_m2),
        ("doors", doors_m2),
    ]:
        sub_min, sub_max = print_surface_needs(surface_name, surface_m2)
        grand_min += sub_min
        grand_max += sub_max
    print(f"Grand total (known prices, min..max): {grand_min:.2f} .. {grand_max:.2f} EUR")


if __name__ == "__main__":
    main()
