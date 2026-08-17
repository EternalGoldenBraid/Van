from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class Product:
    name: str
    url: Optional[str]
    unit_name: str
    unit_price_eur: Optional[float]


@dataclass
class LineItem:
    product: Product
    units: int
    note: Optional[str] = None
    optional: bool = False


@dataclass
class Section:
    name: str
    items: List[LineItem]
    include_in_grand_total: bool = True
    note: Optional[str] = None


def print_section(section: Section) -> Tuple[float, float]:
    print("-" * 30)
    print(section.name)
    if section.note:
        print(f"  note: {section.note}")

    subtotal_min = 0.0
    subtotal_max = 0.0

    for item in section.items:
        cost = None
        if item.product.unit_price_eur is not None:
            cost = item.units * float(item.product.unit_price_eur)
            subtotal_max += cost
            if not item.optional:
                subtotal_min += cost

        note = "" if item.note is None else f" ({item.note})"
        optional = " [optional]" if item.optional else ""
        price = (
            "unknown"
            if item.product.unit_price_eur is None
            else f"{item.product.unit_price_eur:.2f} EUR"
        )

        print(f"  - {item.product.name}{optional}{note}")
        line = f"    {item.units} x {item.product.unit_name} ({price})"
        if cost is None:
            line += " -> unknown EUR"
        else:
            line += f" -> {cost:.2f} EUR"
        print(line)
        if item.product.url:
            print(f"    {item.product.url}")
        print()

    if section.include_in_grand_total:
        print(
            f"  {section.name} subtotal min..max: "
            f"{subtotal_min:.2f} .. {subtotal_max:.2f} EUR"
        )
    else:
        print("  excluded from grand total (alternative path / measurement-only section)")
    print("-" * 30, "\n")
    return subtotal_min, subtotal_max


def main() -> None:
    print("12V Victron-oriented van electronics shopping baseline")
    print("Store focus: Suomen Akut, Renogy, and nearby Finnish accessory sources")
    print()
    print("Scope assumptions")
    print("  - New independent 12V house bank for fan, remote-work loads, and future house loads.")
    print("  - Baseline battery bank is now 2 x 12.8V 200Ah Renogy Pro BT/Heat batteries.")
    print("  - Existing old auxiliary system is left physically in place for now.")
    print("  - Do not tie old auxiliary battery directly to the new house battery.")
    print("  - Copper cable lengths / lug counts are intentionally left out until runs are measured.")
    print()

    battery_renogy_pro_200 = Product(
        name="Renogy 12V 200Ah Pro Lithium self-heating, BT",
        url=(
            "https://renogy.fi/tuotteet/renogy/akut/"
            "12v-200ah-pro-lithium-self-heating--bt-_-P2043351"
        ),
        unit_name="pc",
        unit_price_eur=1199.90,
    )
    battery_power_plus_200 = Product(
        name="Power Plus LFP12-200EV akku12,8V200Ah",
        url=(
            "https://www.suomenakut.fi/akut-ja-paristot/"
            "power-plus-lfp12-200ev-akku12-8v200ah-501x186x240-lifepo4-2560wh-bt-heat/"
            "p/700221/"
        ),
        unit_name="pc",
        unit_price_eur=890.0,
    )
    battery_victron_superpack_200 = Product(
        name="Victron SuperPack akku 12,8V/200Ah",
        url=(
            "https://www.suomenakut.fi/akut-ja-paristot/"
            "victron-superpack-akku-12-8v-200ah-520x208x269-lifepo4/p/8719076047568/"
        ),
        unit_name="pc",
        unit_price_eur=1099.0,
    )
    battery_victron_smart_100 = Product(
        name="Victron LiFePO4 akku 12,8V/100Ah Smart",
        url=(
            "https://www.suomenakut.fi/akut-ja-paristot/"
            "victron-lifepo4-akku-12-8v-100ah-smart-321152197-lifepo4/p/8719076043041/"
        ),
        unit_name="pc",
        unit_price_eur=790.0,
    )
    smartshunt_500 = Product(
        name="Victron SmartShunt 500A/50mV",
        url=(
            "https://www.suomenakut.fi/lisavarusteet/"
            "victron-smartshunt-500a-50mv-9-90vdc-bluetooth-ve-direct/p/8719076044253/"
        ),
        unit_name="pc",
        unit_price_eur=120.0,
    )
    orion_tr_smart_30 = Product(
        name="Victron energy Orion-Tr Smart DC Laturi 12/12-30A Non isolated",
        url=(
            "https://www.suomenakut.fi/laturit-ja-lataustarvikkeet/"
            "victron-energy-orion-tr-smart-dc-laturi-12-12-30a-360w-non-isolated/"
            "p/8719076048954/"
        ),
        unit_name="pc",
        unit_price_eur=225.0,
    )
    orion_xs_50 = Product(
        name="Victron energy Orion XS Smart DC Laturi 12/12-50A IP65",
        url=(
            "https://www.suomenakut.fi/laturit-ja-lataustarvikkeet/"
            "victron-energy-orion-xs-smart-dc-laturi-12-12-50a-700w-ip65/"
            "p/8719076068501/"
        ),
        unit_name="pc",
        unit_price_eur=339.0,
    )
    blue_smart_ip22_12_30_1 = Product(
        name="Victron Blue Smart IP22 Laturi 12/30 1-ulostulo",
        url=(
            "https://www.suomenakut.fi/laturit-ja-lataustarvikkeet/"
            "victron-blue-smart-ip22-laturi-12-30-1-ulostulo-bluetooth/p/8719076052364/"
        ),
        unit_name="pc",
        unit_price_eur=225.0,
    )
    smartsolar_100_30 = Product(
        name="Victron SmartSolar MPPT 100/30 säädin",
        url=(
            "https://www.suomenakut.fi/aurinkoenergia/"
            "victron-smartsolar-mppt-100-30-saadin-bluetooth/p/8719076040170/"
        ),
        unit_name="pc",
        unit_price_eur=130.0,
    )
    main_switch_275 = Product(
        name="Victron päävirtakytkin ON/OFF 275A",
        url=(
            "https://www.suomenakut.fi/aurinkoenergia/"
            "victron-paavirtakytkin-on-off-275a-275a-450a-1min-max-48vdc/"
            "p/8719076052258/"
        ),
        unit_name="pc",
        unit_price_eur=37.0,
    )
    mega_holder = Product(
        name="Victron sulakepesä megasulakkeelle",
        url=(
            "https://www.suomenakut.fi/aurinkoenergia/"
            "victron-sulakepesa-megasulakkeelle/p/8719076021704/"
        ),
        unit_name="pc",
        unit_price_eur=17.9,
    )
    mega_fuse_40 = Product(
        name="Megasulake 40A/80V",
        url=(
            "https://www.suomenakut.fi/aurinkoenergia/"
            "megasulake-40a-80v-1kpl-victron/p/8719076062707/"
        ),
        unit_name="pc",
        unit_price_eur=15.0,
    )
    mega_fuse_60 = Product(
        name="Megasulake 60A/80V",
        url=(
            "https://www.suomenakut.fi/aurinkoenergia/"
            "megasulake-60a-80v-1kpl-victron/p/8719076061649/"
        ),
        unit_name="pc",
        unit_price_eur=15.0,
    )
    mega_fuse_150 = Product(
        name="Megasulake 150A/32V",
        url=(
            "https://www.suomenakut.fi/aurinkoenergia/"
            "megasulake-150a-32v-1kpl-victron/p/8719076016601/"
        ),
        unit_name="pc",
        unit_price_eur=13.5,
    )
    busbar_250_6p_cover = Product(
        name="Victron kytkentäkisko 250A 6P + suoja",
        url=(
            "https://www.suomenakut.fi/aurinkoenergia/"
            "victron-kytkentakisko-250a-6p-suoja/p/8719076056416/"
        ),
        unit_name="pc",
        unit_price_eur=69.0,
    )
    lynx_distributor = Product(
        name="Victron Lynx Distributor - DC-jakokisko",
        url=(
            "https://www.suomenakut.fi/aurinkoenergia/"
            "victron-lynx-distributor-dc-jakokisko-290-x-170-x-80-m10/"
            "p/8719076057628/"
        ),
        unit_name="pc",
        unit_price_eur=210.0,
    )
    busbar_150_6p = Product(
        name="Victron kytkentäkisko 6-paikkainen 150A",
        url=(
            "https://www.suomenakut.fi/aurinkoenergia/"
            "victron-kytkentakisko-6-paikkainen-150a/p/8719076033004/"
        ),
        unit_name="pc",
        unit_price_eur=50.0,
    )
    busbar_cover_150_6p = Product(
        name="Victron kytkentäkisko 150A 6P + suoja",
        url=(
            "https://www.suomenakut.fi/aurinkoenergia/"
            "victron-kytkentakisko-150a-6p-suoja/p/8719076052203/"
        ),
        unit_name="pc",
        unit_price_eur=32.0,
    )
    fuse_block_10 = Product(
        name="Sulakepesä autosulakkeille 10-paikkainen",
        url=(
            "https://www.suomenakut.fi/aurinkoenergia/"
            "sulakepesa-autosulakkeille-10-paikkainen-max-30a-32vdc/p/670003/"
        ),
        unit_name="pc",
        unit_price_eur=35.0,
    )
    blade_fuse_assortment = Product(
        name="Autosulakelajitelma 88kpl",
        url=(
            "https://www.suomenakut.fi/lisavarusteet/"
            "autosulakelajitelma-88kpl-11-9mm-19mm-29mm/p/100275563430013/"
        ),
        unit_name="box",
        unit_price_eur=25.0,
    )
    battery_cable_pair_50_100cm = Product(
        name="Akkukaapeli pari 50mm2 100cm, silmukat 8mm ja 10mm",
        url=(
            "https://www.suomenakut.fi/aurinkoenergia/"
            "akkukaapeli-pari-50mm2-100cm-kaapelisilmukat-8mm-ja-10mm/p/9723/"
        ),
        unit_name="pair",
        unit_price_eur=40.0,
    )
    battery_parallel_pair_50_30cm = Product(
        name="Rinnankytkentäkaapelipari 50mm2 30cm, silmukka 8mm",
        url=(
            "https://www.suomenakut.fi/aurinkoenergia/"
            "rinnankytkentakaapelipari-50mm2-30cm-kaapelisilmukka-8mm/p/9705/"
        ),
        unit_name="pair",
        unit_price_eur=24.0,
    )
    lug_50_m8 = Product(
        name="Kaapelisilmukka 50mm2 M8 Ouneva",
        url=(
            "https://www.suomenakut.fi/akut-ja-paristot/"
            "kaapelisilmukka-50mm2-8mm-reialla-50-8-ouneva/p/6410052011451/"
        ),
        unit_name="pc",
        unit_price_eur=3.70,
    )
    lug_50_m10 = Product(
        name="50mm2 M10 cable lug placeholder",
        url="https://www.puuilo.fi/autotarvikkeet/autosahko/liittimet-katkaisimet-releet-ja-tarvikkeet/kaapelikengat",
        unit_name="pc",
        unit_price_eur=4.19,
    )
    heatshrink_black_large = Product(
        name="Kutisteletku musta 2:1 50.8mm-25.4mm 1m",
        url=(
            "https://www.suomenakut.fi/lisavarusteet/ajoneuvojen-lisavarusteet/"
            "kutistesukat-ja-suojaputket/c/6803/"
        ),
        unit_name="m",
        unit_price_eur=10.0,
    )
    heatshrink_red_large = Product(
        name="Kutisteletku punainen 2:1 38.1mm-19mm 1m",
        url=(
            "https://www.suomenakut.fi/lisavarusteet/ajoneuvojen-lisavarusteet/"
            "kutistesukat-ja-suojaputket/c/6803/"
        ),
        unit_name="m",
        unit_price_eur=4.0,
    )
    cable_spiral_8mm = Product(
        name="Kaapelinsuojaspiraali 8mm musta",
        url=(
            "https://www.suomenakut.fi/lisavarusteet/ajoneuvojen-lisavarusteet/"
            "kutistesukat-ja-suojaputket/c/6803/"
        ),
        unit_name="m",
        unit_price_eur=0.95,
    )
    duplex_wire_2x15_10m = Product(
        name="Johto 2-napainen 2 x 1.5mm2 10m",
        url=(
            "https://www.motonet.fi/tuoteryhmat/autotarvikkeet/autosahko/"
            "johdot-ja-asennustarvikkeet/johdot?category=3c2316ba-b240-11e5-88f1-730a0916b598"
        ),
        unit_name="roll",
        unit_price_eur=13.90,
    )
    lug_assortment_small = Product(
        name="Kaapelikenkälajitelma 60-os. 6-25mm2",
        url="https://www.puuilo.fi/autotarvikkeet/autosahko/liittimet-katkaisimet-releet-ja-tarvikkeet/kaapelikengat",
        unit_name="set",
        unit_price_eur=14.99,
    )
    install_consumables = Product(
        name="Cable ties, mounts, labels, abrasion protection, grommets allowance",
        url=None,
        unit_name="allowance",
        unit_price_eur=35.0,
    )
    crimper_6_50 = Product(
        name="Kramfors kaapeliliittimen puristuspihti 6-50mm2",
        url="https://www.puuilo.fi/kramfors-kaapeliliittimen-puristuspihti-6-50mm2",
        unit_name="pc",
        unit_price_eur=25.29,
    )
    fluke_365_clamp_meter = Product(
        name="Fluke-365/E pihtimittari",
        url=(
            "https://www.suomenakut.fi/akut-ja-paristot/"
            "fluke-365-e-pihtimittari/p/95969559874/"
        ),
        unit_name="pc",
        unit_price_eur=599.0,
    )

    sections = [
        Section(
            name="recommended_core_12v_house_bank",
            note=(
                "Recommended first build: 400Ah / 5120Wh nominal battery bank, 30A DC-DC charging, "
                "Victron monitoring, Victron high-current distribution, and a separate blade-fuse block "
                "for MaxxFan and other 12V loads. Battery-parallel fuse/bus topology is provisional "
                "until physical layout is settled."
            ),
            items=[
                LineItem(
                    battery_renogy_pro_200,
                    units=2,
                    note=(
                        "Chosen for now over cheaper unknowns: 12.8V 200Ah / 2560Wh each, "
                        "Bluetooth, self-heating, 200A max continuous discharge, and documented parallel support."
                    ),
                ),
                LineItem(
                    smartshunt_500,
                    units=1,
                    note="Battery monitor on the house-bank negative side.",
                ),
                LineItem(
                    main_switch_275,
                    units=1,
                    note="House-bank master disconnect.",
                ),
                LineItem(
                    mega_holder,
                    units=4,
                    note=(
                        "Provisional: two battery-positive fuses, one common main fuse, "
                        "and one starter-side Orion input fuse. Confirm exact topology before purchase."
                    ),
                ),
                LineItem(
                    mega_fuse_150,
                    units=3,
                    note=(
                        "Provisional battery-bank protection: battery A, battery B, and common main. "
                        "May change if terminal fuses or another battery-combiner layout is selected."
                    ),
                ),
                LineItem(
                    mega_fuse_40,
                    units=2,
                    note="Provisional 40A fuses: starter-side Orion input and Lynx branch to Orion output. Confirm against final cable size and manual before install.",
                ),
                LineItem(
                    orion_tr_smart_30,
                    units=1,
                    note="Recommended alternator charger for the new 12V house bank.",
                ),
                LineItem(
                    busbar_250_6p_cover,
                    units=1,
                    note=(
                        "Provisional battery-combiner busbar for two-battery layout before common main protection."
                    ),
                ),
                LineItem(
                    lynx_distributor,
                    units=1,
                    note="Positive fused distribution for Orion output, fuse-block feed, shore charger, solar controller, and future inverter branch.",
                ),
                LineItem(
                    busbar_150_6p,
                    units=1,
                    note="Negative return bus after the SmartShunt.",
                ),
                LineItem(
                    busbar_cover_150_6p,
                    units=1,
                    note="Protective cover for the negative busbar.",
                ),
                LineItem(
                    fuse_block_10,
                    units=1,
                    note="12V branch circuits for MaxxFan, lights, USB, heater controls, etc.",
                ),
                LineItem(
                    blade_fuse_assortment,
                    units=1,
                    note="Branch fuses for MaxxFan and other low-current loads.",
                ),
            ],
        ),
        Section(
            name="recommended_wiring_accessories_and_cable_rough_in",
            note=(
                "FarOutRide-style accessory pass: cable, lugs, heat shrink, abrasion protection, "
                "and branch wiring. Quantities are rough until the electrical box location and cable runs are measured."
            ),
            items=[
                LineItem(
                    battery_cable_pair_50_100cm,
                    units=4,
                    note=(
                        "Rough allowance for 50mm2 positive/negative trunks and equal-length battery-bank leads. "
                        "Final lengths and lug hole sizes still need measurement."
                    ),
                ),
                LineItem(
                    battery_parallel_pair_50_30cm,
                    units=2,
                    note="Short 50mm2 jumpers/spares for the two-battery parallel layout if geometry allows.",
                ),
                LineItem(
                    lug_50_m8,
                    units=8,
                    note="Spare/custom 50mm2 M8 lugs for battery, busbar, shunt, and Lynx terminations.",
                ),
                LineItem(
                    lug_50_m10,
                    units=4,
                    note="Placeholder for 50mm2 M10 lugs if final hardware requires M10 instead of M8.",
                ),
                LineItem(
                    heatshrink_black_large,
                    units=2,
                    note="Large black heat shrink for high-current cable ends.",
                ),
                LineItem(
                    heatshrink_red_large,
                    units=2,
                    note="Large red heat shrink / polarity marking for high-current cable ends.",
                ),
                LineItem(
                    cable_spiral_8mm,
                    units=10,
                    note="Abrasion protection where cables pass near wood, metal, or sharp edges.",
                ),
                LineItem(
                    duplex_wire_2x15_10m,
                    units=1,
                    note="Small-load branch wiring allowance for MaxxFan/USB/control circuits.",
                ),
                LineItem(
                    lug_assortment_small,
                    units=1,
                    note="Small ring/fork lugs for branch circuits; exact terminals depend on the fuse block and outlets.",
                ),
                LineItem(
                    install_consumables,
                    units=1,
                    note="Budget placeholder for ties, mounts, labels, loom, grommets, tape, and small fasteners.",
                ),
            ],
        ),
        Section(
            name="optional_shore_power",
            note="Useful if you want clean mains-powered charging when parked or when jamming on hookup.",
            items=[
                LineItem(
                    blue_smart_ip22_12_30_1,
                    units=1,
                    optional=True,
                    note="Single-output 230V shore charger for the new house bank.",
                ),
                LineItem(
                    mega_fuse_40,
                    units=1,
                    optional=True,
                    note="Provisional Lynx branch fuse for the IP22 output; confirm against final cable sizing.",
                ),
            ],
        ),
        Section(
            name="optional_solar_controller_only",
            note="Controller only. Solar panels, roof gland, PV cable, and roof mounting still need a measured parts pass.",
            items=[
                LineItem(
                    smartsolar_100_30,
                    units=1,
                    optional=True,
                    note="Good starting controller for a modest 12V roof solar array.",
                ),
                LineItem(
                    mega_fuse_40,
                    units=1,
                    optional=True,
                    note="Provisional Lynx branch fuse for the MPPT output; confirm against final cable sizing.",
                ),
            ],
        ),
        Section(
            name="optional_measurement_tools",
            include_in_grand_total=False,
            note=(
                "Diagnostic tools are kept separate from the build BOM. "
                "This was the only clamp-style current meter found on Suomen Akut at the time of checking."
            ),
            items=[
                LineItem(
                    crimper_6_50,
                    units=1,
                    optional=True,
                    note=(
                        "One-time tool for 6-50mm2 uninsulated tube lugs. "
                        "A shop-made cable set or borrowed hydraulic crimper may be better for final install."
                    ),
                ),
                LineItem(
                    fluke_365_clamp_meter,
                    units=1,
                    optional=True,
                    note=(
                        "Clamp meter for current measurement without opening the cable. "
                        "Functionally suitable, but priced like a pro tool rather than a casual garage buy."
                    ),
                ),
            ],
        ),
        Section(
            name="optional_upgrades_and_alternatives",
            include_in_grand_total=False,
            note=(
                "Alternative paths that replace or extend the recommended baseline rather than stacking on top of it."
            ),
            items=[
                LineItem(
                    battery_power_plus_200,
                    units=2,
                    optional=True,
                    note=(
                        "Cheaper 2 x 200Ah BT/Heat alternative if two identical units are actually available."
                    ),
                ),
                LineItem(
                    battery_victron_superpack_200,
                    units=2,
                    optional=True,
                    note="Premium Victron 2 x 200Ah path with larger capacity and integrated protection.",
                ),
                LineItem(
                    battery_victron_smart_100,
                    units=1,
                    optional=True,
                    note="Not plug-and-play. Requires a separate Victron BMS that is not yet priced in this script.",
                ),
                LineItem(
                    orion_xs_50,
                    units=1,
                    optional=True,
                    note="Upgrade path if alternator headroom is proven and faster charging becomes worthwhile.",
                ),
                LineItem(
                    mega_fuse_60,
                    units=2,
                    optional=True,
                    note="Likely starter-side and house-side branch fuses for the Orion XS path; confirm against manual and cable selection.",
                ),
            ],
        ),
    ]

    grand_min = 0.0
    grand_max = 0.0
    for section in sections:
        sub_min, sub_max = print_section(section)
        if section.include_in_grand_total:
            grand_min += sub_min
            grand_max += sub_max

    print(f"Grand total (recommended core + optional sections, min..max): {grand_min:.2f} .. {grand_max:.2f} EUR")
    print()
    print("Not yet priced in this script")
    print("  - Exact copper cable lengths and final lug hole sizes: must be measured on-van first.")
    print("  - Starter-battery side mechanical routing parts and pass-through protection.")
    print("  - Solar panels, roof gland, PV cable, and mounting hardware.")
    print("  - Shore-power inlet, AC protection, and outlet hardware if shore is added.")
    print()
    print("Current open technical question")
    print(
        "  - The observed Wehrle/Wurth relay hardware near the passenger-seat battery area does not yet prove "
        "the alternator charging topology. Treat the old auxiliary charging path as unresolved until it is traced."
    )


if __name__ == "__main__":
    main()
