"""
WBP Data Models - Dataclass definitions for Work and Budget Plan data structures.

These models represent all extractable data from COST WBP documents:
- Action Profile (Page 1)
- Working Groups (Page 2)
- MoU Objectives (Pages 3-4)
- Deliverables (Page 4)
- Grant Period Goals/GAPGs (Pages 5-6)
- Budget Summary (Page 7)
- Meeting Details (Pages 8-20)
- Training Schools (Pages 21-25)
- Mobility (STSM/VM) (Page 26)
- Conference Presentations (Page 27)
- Dissemination Products (Page 28)
- OERSA (Page 29)
"""

from dataclasses import dataclass, field
from typing import Optional
from decimal import Decimal
from datetime import date


@dataclass
class ActionProfile:
    """Page 1: Action Profile information."""
    action_code: str  # e.g., "CA19130"
    action_title: str  # e.g., "Fintech and Artificial Intelligence in Finance"
    chair_name: str
    chair_institution: str
    chair_country: str
    grant_period: int  # 1-5
    start_date: date
    end_date: date
    total_grant: Decimal
    participating_cost_countries: int
    participating_near_neighbour_countries: int
    participating_international_partner_countries: int


@dataclass
class WorkingGroup:
    """Page 2: Working Group information."""
    wg_number: int  # 1, 2, or 3
    wg_name: str
    wg_leader_name: str
    wg_leader_institution: str
    wg_leader_country: str
    member_count: Optional[int] = None


@dataclass
class MoUObjective:
    """Pages 3-4: MoU Objective (Secondary Objectives)."""
    objective_number: int  # 1-16
    objective_text: str
    category: str  # "capacity building", "research", "dissemination", etc.


@dataclass
class Deliverable:
    """Page 4: Deliverable item."""
    deliverable_number: int
    deliverable_title: str
    deliverable_description: str
    target_gp: Optional[int] = None  # Which GP this deliverable targets


@dataclass
class GrantPeriodGoal:
    """Pages 5-6: Grant Agreement Period Goal (GAPG)."""
    gapg_number: int
    gapg_title: str
    gapg_description: str
    mou_objectives: list[int] = field(default_factory=list)  # Links to MoU objective numbers
    grant_period: int = 0


@dataclass
class BudgetCategory:
    """Budget category with planned amount."""
    category_name: str
    planned_amount: Decimal
    description: Optional[str] = None


@dataclass
class BudgetSummary:
    """Page 7: Budget Summary for a Grant Period."""
    grant_period: int
    total_grant: Decimal
    meetings: Decimal
    training_schools: Decimal
    mobility: Decimal  # STSM + VM combined (GP4+) or separate STSM (GP1-3)
    conference_presentations: Decimal  # ITC Conference (GP1-3) or Conference Presentations (GP4+)
    dissemination: Decimal
    oersa: Decimal
    total_science: Decimal  # Sum of above
    fsac: Decimal  # Fixed Science Activities Contribution
    stsm: Optional[Decimal] = None  # Separate STSM for GP1-3
    itc_grants: Optional[Decimal] = None  # ITC Conference Grants for GP1-3


@dataclass
class MeetingPlan:
    """Pages 8-20: Planned meeting details from WBP."""
    meeting_number: int
    title: str
    meeting_type: str  # "Core Group", "Working Group", "Management Committee", "Workshop/Conference"
    start_date: date
    end_date: date
    location: str
    country: str
    itc_country: bool
    planned_cost: Decimal
    expected_participants: int
    expected_reimbursed: int
    grant_period: int
    description: Optional[str] = None
    expected_outputs: Optional[str] = None


@dataclass
class TrainingSchoolPlan:
    """Pages 21-25: Planned training school details from WBP."""
    school_number: int
    title: str
    institution: str
    location: str
    country: str
    start_date: date
    end_date: date
    planned_cost: Decimal
    expected_trainers: int
    expected_trainees: int
    grant_period: int
    description: Optional[str] = None
    topics: Optional[str] = None


@dataclass
class STSMPlan:
    """Page 26: STSM planning information."""
    grant_period: int
    total_budget: Decimal
    expected_stsm_count: int
    average_duration_days: int
    average_grant: Decimal
    host_countries: list[str] = field(default_factory=list)


@dataclass
class VirtualMobilityPlan:
    """Page 26: Virtual Mobility planning information."""
    grant_period: int
    total_budget: Decimal
    expected_vm_count: int
    average_grant: Decimal


@dataclass
class ConferencePresentationPlan:
    """Page 27: Conference Presentation planning."""
    grant_period: int
    total_budget: Decimal
    expected_presentations: int
    average_grant: Decimal
    target_conferences: list[str] = field(default_factory=list)


@dataclass
class DisseminationProduct:
    """Page 28: Dissemination and Communication Product."""
    product_number: int
    product_type: str  # "Website", "Social Media", "Publication", etc.
    title: str
    description: str
    planned_cost: Decimal
    grant_period: int


@dataclass
class OERSAItem:
    """Page 29: Other Expenses Related to Scientific Activities."""
    item_number: int
    title: str
    description: str
    planned_cost: Decimal
    grant_period: int


@dataclass
class WBPFullExtraction:
    """Complete extraction from a single WBP document."""
    grant_period: int
    action_profile: ActionProfile
    working_groups: list[WorkingGroup]
    mou_objectives: list[MoUObjective]
    deliverables: list[Deliverable]
    gapgs: list[GrantPeriodGoal]
    budget_summary: BudgetSummary
    meetings: list[MeetingPlan]
    training_schools: list[TrainingSchoolPlan]
    stsm_plan: Optional[STSMPlan] = None
    vm_plan: Optional[VirtualMobilityPlan] = None
    conference_presentations: Optional[ConferencePresentationPlan] = None
    dissemination_products: list[DisseminationProduct] = field(default_factory=list)
    oersa_items: list[OERSAItem] = field(default_factory=list)
    source_file: str = ""
