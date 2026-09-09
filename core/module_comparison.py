

from dataclasses import dataclass, field
from typing import List, Optional

from core.customer_requirements import (CustomerRequirements, requirements_from_answers)
from core.recommendation_bridge import (ModuleCandidate,recommend_from_answers)


@dataclass
class ComparisonCell:
    module_id: str
    value: str
    status: str
    
@dataclass
class ComparisonRow:
    key: str
    label: str

    requirement_level: str

    cells: List[ComparisonCell] = field(default_factory=list)
    
    
@dataclass
class ComparisonCandidate:
    module_id: str

    rank: int
    eligible: bool

    match_percent: int
    match_strength: str

    recommendation_label: str
    
@dataclass
class ModuleComparison:
    candidates: List[ComparisonCandidate] = field(default_factory=list)
    rows: List[ComparisonRow] = field(default_factory=list)

    @property
    def has_candidates(self) -> bool:
        return bool(self.candidates)

    def get_row(self, key:str) -> Optional[ComparisonRow]:
        for row in self.rows:
            if row.key == key:
                return row
        return None

    def get_cell(self, row_key: str, module_id: str) -> Optional[ComparisonCell]:
        row = self.get_row(row_key)
        if row is None:
            return None
        for cell in row.cells:
            if cell.module_id == module_id:
                return cell
        return None
        
        
def _comparison_status(*, required: bool, mandatory: bool, supported: bool) -> str:
    if required:
        if supported:
            return "MATCH"
        if mandatory:
            return "BLOCKER"
        return "TRADEOFF"
    if supported:
        return "AVAILABLE"
    return "NOT_REQUIRED"
    
def _requirement_level(required: bool, mandatory: bool) -> str:

    if not required:
        return "NOT REQUESTED"

    if mandatory:
        return "MANDATORY"

    return "PREFERRED"
    
    
def _make_boolean_row(*, key: str, label: str, required: bool, mandatory: bool, selected_modules: List[ModuleCandidate],
    capability_name: str) -> ComparisonRow:
    cells = []
    for module in selected_modules:
        supported = bool(getattr(module, capability_name))
        cells.append(ComparisonCell(module_id=module.module_id,
                value=("Yes" if supported else "No"),
                status=_comparison_status(required=required, mandatory=mandatory, supported=supported),
            )
        )
    return ComparisonRow(key=key, label=label,
        requirement_level=( _requirement_level(required, mandatory)),
        cells=cells,
    )
    
def _make_host_interface_row(requirements: CustomerRequirements, selected_modules: List[ModuleCandidate]) -> ComparisonRow:
    required_interface = (requirements.host_interface)
    required = bool(required_interface)
    mandatory = (requirements.host_interface_mandatory)
    cells = []
    for module in selected_modules:
        if module.host_interfaces:
            display_value = ", ".join(module.host_interfaces)
        else:
            display_value = "None"
        if required:
            supported = (required_interface in module.host_interfaces)
        else:
            supported = bool(module.host_interfaces)
        cells.append(ComparisonCell(module_id=module.module_id, value=display_value,
                status=_comparison_status(required=required, mandatory=mandatory, supported=supported),
            )
        )

    return ComparisonRow(key="host_interface", label="Host Interface", requirement_level=(_requirement_level(required, mandatory)),
        cells=cells,
    )
    
def build_module_comparison(answers: dict, modules: List[ModuleCandidate], max_candidates: int = 3,
    include_rejected: bool = False) -> ModuleComparison:
    requirements = (requirements_from_answers(answers))
    shortlist = (recommend_from_answers(answers, modules))
    selected_results = list(shortlist.top_eligible(max_candidates))
    
    if include_rejected:
        selected_ids = {item.module_id for item in selected_results}
        for item in (shortlist.ineligible_results):
            if (len(selected_results) >= max_candidates):
                break
            if (item.module_id not in selected_ids):
                selected_results.append(item)
                selected_ids.add(item.module_id)
                
    module_lookup = {module.module_id: module for module in modules}
    selected_modules = []
    for result in selected_results:
        module = module_lookup.get(result.module_id)
        if module is not None:
            selected_modules.append(module)

    candidates = []
    for result in selected_results:
        if result.eligible:
            if result.rank == 1:
                label = "RECOMMENDED"
            else:
                label = "ALTERNATIVE"
        else:
            label = "NOT ELIGIBLE"

        candidates.append(ComparisonCandidate(module_id=result.module_id, rank=result.rank,
                eligible=result.eligible,
                match_percent=(result.match_percent),
                match_strength=(result.match_strength),
                recommendation_label=label,
            )
        )
        
    rows = []
    rows.append( _make_boolean_row(key="wifi", label="Wi-Fi", required=(requirements.wifi_required),
            mandatory=(requirements.wifi_mandatory), selected_modules=(selected_modules),
            capability_name="wifi",
        )
    )
    
    rows.append(_make_boolean_row(key="ble", label="Bluetooth LE",
            required=(requirements.ble_required),
            mandatory=(requirements.ble_mandatory),
            selected_modules=(selected_modules),
            capability_name="ble",
        )
    )

    rows.append(_make_boolean_row(key="bluetooth_classic", label="Bluetooth Classic",
            required=(requirements.bluetooth_classic_required),
            mandatory=(requirements.bluetooth_classic_mandatory),
            selected_modules=(selected_modules),
            capability_name=("bluetooth_classic"),
        )
    )

    rows.append(_make_boolean_row(key="wifi6", label="Wi-Fi 6",
            required=(requirements.wifi6_required),
            mandatory=(requirements.wifi6_mandatory),
            selected_modules=(selected_modules),
            capability_name="wifi6",
        )
    )
    rows.append(_make_boolean_row(key="high_throughput", label="High Throughput",
            required=(requirements.high_throughput_required),
            mandatory=(requirements.high_throughput_mandatory),
            selected_modules=(selected_modules),
            capability_name=("high_throughput"),
        )
    )

    rows.append(_make_host_interface_row(requirements, selected_modules))

    return ModuleComparison(candidates=candidates, rows=rows)    


def render_comparison_text(comparison: ModuleComparison) -> str:
    if not comparison.has_candidates:
        return ("No eligible modules available "
                "for comparison."
            )

    lines = []
    lines.append("MODULE COMPARISON")
    lines.append("=" * 60)
    for candidate in comparison.candidates:
        lines.append(
            f"{candidate.module_id}: "
            f"{candidate.recommendation_label}, "
            f"{candidate.match_percent}% "
            f"({candidate.match_strength})"
        )
    lines.append("")
    for row in comparison.rows:
        lines.append(
            f"{row.label} "
            f"[{row.requirement_level}]"
        )
        for cell in row.cells:
            lines.append(
                f"  {cell.module_id}: "
                f"{cell.value} "
                f"({cell.status})"
            )
        lines.append("")
    return "\n".join(lines)