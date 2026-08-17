from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass
class Load:
    name: str
    watts: float
    hours_per_day: float
    enabled: bool = True
    note: Optional[str] = None

    @property
    def watt_hours_per_day(self) -> float:
        return self.watts * self.hours_per_day if self.enabled else 0.0


@dataclass
class Battery:
    name: str
    nominal_voltage: float
    amp_hours: float
    usable_fraction: float
    recommended_discharge_amps: float
    max_continuous_discharge_amps: float
    main_fuse_amps: float

    @property
    def nominal_watt_hours(self) -> float:
        return self.nominal_voltage * self.amp_hours

    @property
    def usable_watt_hours(self) -> float:
        return self.nominal_watt_hours * self.usable_fraction


def fmt_wh(value: float) -> str:
    if value >= 1000:
        return f"{value / 1000:.2f} kWh"
    return f"{value:.0f} Wh"


def fmt_w(value: float) -> str:
    if value >= 1000:
        return f"{value / 1000:.2f} kW"
    return f"{value:.0f} W"


def print_loads(loads: Iterable[Load]) -> float:
    total = 0.0
    print("Daily load assumptions")
    print("  Edit LOADS in this file as real usage becomes clearer.")
    print()
    for load in loads:
        status = "" if load.enabled else " [disabled]"
        note = "" if load.note is None else f" ({load.note})"
        wh = load.watt_hours_per_day
        total += wh
        print(
            f"  - {load.name}{status}: {load.watts:.0f} W x "
            f"{load.hours_per_day:.1f} h = {fmt_wh(wh)}{note}"
        )
    print(f"\n  daily total: {fmt_wh(total)}")
    return total


def print_battery_runtime(battery: Battery, daily_wh: float) -> None:
    days = battery.usable_watt_hours / daily_wh if daily_wh else 0.0
    print("\nBattery capacity")
    print(f"  battery: {battery.name}")
    print(
        f"  nominal: {battery.nominal_voltage:.1f} V x "
        f"{battery.amp_hours:.0f} Ah = {fmt_wh(battery.nominal_watt_hours)}"
    )
    print(
        f"  planning usable capacity: {battery.usable_fraction:.0%} = "
        f"{fmt_wh(battery.usable_watt_hours)}"
    )
    print(f"  runtime at this load: {days:.1f} days")
    print(f"  runtime at this load: {days * 24:.0f} hours")


def print_current_limits(battery: Battery) -> None:
    recommended_watts = battery.nominal_voltage * battery.recommended_discharge_amps
    max_watts = battery.nominal_voltage * battery.max_continuous_discharge_amps
    fused_watts = battery.nominal_voltage * battery.main_fuse_amps

    print("\nDischarge current limits")
    print(
        f"  battery recommended discharge: "
        f"{battery.recommended_discharge_amps:.0f} A ~= {fmt_w(recommended_watts)} continuous power"
    )
    print(
        f"  battery max continuous discharge: "
        f"{battery.max_continuous_discharge_amps:.0f} A ~= {fmt_w(max_watts)} continuous power"
    )
    print(
        f"  planned main fuse: "
        f"{battery.main_fuse_amps:.0f} A ~= {fmt_w(fused_watts)} allowed system power"
    )
    print()
    print("  Interpretation:")
    print("  - The fuse can be lower than the battery max; that is normal.")
    print("  - The fuse defines the system limit and protects the downstream cable.")
    print("  - Daily 12V loads here are far below 100A unless a large inverter is added.")


def print_charging_reference(daily_wh: float) -> None:
    print("\nCharging reference")
    print("  These are idealized DC numbers before real-world losses and charge taper.")
    charge_sources = [
        ("Orion-Tr 12/12-30A while driving", 12.8 * 30),
        ("Future Orion XS 12/12-50A while driving", 12.8 * 50),
        ("IP22 12/30 shore charger", 12.8 * 30),
    ]
    for name, watts in charge_sources:
        hours = daily_wh / watts if watts else 0.0
        print(f"  - {name}: {watts:.0f} W equivalent -> {hours:.1f} h to replace one modeled day")

    solar_wh = 400 * 4
    print(
        f"  - Future 400W solar at 4 peak-sun-hours: {fmt_wh(solar_wh)} per good day "
        f"({solar_wh / daily_wh:.1f} modeled days replaced)"
    )


# Baseline: current plan is tech work without a large inverter.
LOADS: List[Load] = [
    Load("Primary laptop via USB-C PD", watts=65, hours_per_day=8),
    Load("Second laptop / guest workstation", watts=65, hours_per_day=6, enabled=True),
    Load("Phone + small USB devices", watts=15, hours_per_day=4),
    Load("Raspberry Pi / car computer", watts=8, hours_per_day=24),
    Load("MaxxFan average use", watts=18, hours_per_day=8, note="speed-dependent"),
    Load("Diesel heater electrical average", watts=20, hours_per_day=8, note="startup spike excluded"),
    Load("LED lights", watts=15, hours_per_day=4),
    Load("Fridge placeholder", watts=40, hours_per_day=8, enabled=False),
    Load("Starlink placeholder", watts=50, hours_per_day=8, enabled=False),
]

BATTERY = Battery(
    name="Power Plus LFP12-200EV",
    nominal_voltage=12.8,
    amp_hours=200,
    usable_fraction=0.85,
    recommended_discharge_amps=100,
    max_continuous_discharge_amps=200,
    main_fuse_amps=150,
)


def main() -> None:
    print("Remote-work van power budget")
    print("=" * 29)
    daily_wh = print_loads(LOADS)
    print_battery_runtime(BATTERY, daily_wh)
    print_current_limits(BATTERY)
    print_charging_reference(daily_wh)


if __name__ == "__main__":
    main()
