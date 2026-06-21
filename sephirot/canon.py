"""Canonical Sephirot, Qliphoth, and path profiles."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SephiraProfile:
    number: int
    name: str
    ascent_order: int
    focus_value: str
    kg_role: str
    qliphoth: str
    failure_mode: str


@dataclass(frozen=True)
class PathProfile:
    number: int
    source: str
    target: str
    cq: str
    correspondence_layer: tuple[str, ...]


SEPHIROT: tuple[SephiraProfile, ...] = (
    SephiraProfile(
        1,
        "Kether",
        10,
        "Objective Coherence",
        "Target definition and final success condition",
        "Thaumiel",
        "Split goals, contradictory incentives",
    ),
    SephiraProfile(
        2,
        "Chokmah",
        9,
        "Generative Insight",
        "Possibility space, intuition, creative alternatives",
        "Ghogiel",
        "Noise, confusion, ungrounded ideation",
    ),
    SephiraProfile(
        3,
        "Binah",
        8,
        "Structural Understanding",
        "Constraints, categories, rules, boundaries of meaning",
        "Satariel",
        "Hidden assumptions, opacity, concealed defects",
    ),
    SephiraProfile(
        4,
        "Chesed",
        7,
        "Value Expansion",
        "Resources, generosity, leverage, opportunity creation",
        "Gha'agsheblah",
        "Waste, over-expansion, blind resource consumption",
    ),
    SephiraProfile(
        5,
        "Geburah",
        6,
        "Discipline and Judgment",
        "Risk gates, prioritization, rejection, enforcement",
        "Golachab",
        "Destructive severity, punitive control, over-pruning",
    ),
    SephiraProfile(
        6,
        "Tiferet",
        5,
        "Integration",
        "Central judgment, balance, synthesis, strategy",
        "Thagirion",
        "Ego distortion, false center, performative harmony",
    ),
    SephiraProfile(
        7,
        "Netzach",
        4,
        "Endurance",
        "Motivation, persistence, long-horizon momentum",
        "A'arab Zaraq",
        "Scattered desire, obsession, vanity momentum",
    ),
    SephiraProfile(
        8,
        "Hod",
        3,
        "Analysis and Communication",
        "Models, language, metrics, documentation, explanation",
        "Samael",
        "Poisoned logic, misleading analysis, rationalization",
    ),
    SephiraProfile(
        9,
        "Yesod",
        2,
        "Foundation",
        "Operating substrate, readiness, interfaces, habits",
        "Gamaliel",
        "Illusion of readiness, unstable foundation, fantasy plan",
    ),
    SephiraProfile(
        10,
        "Malkuth",
        1,
        "Execution Reality",
        "Current state, material evidence, actual behavior",
        "Lilith / Nahemoth",
        "Disconnected execution, surface-level activity, drift",
    ),
)


PATHS: tuple[PathProfile, ...] = (
    PathProfile(11, "Kether", "Chokmah", "What possibilities express the target without betraying its core intent?", ("crown", "insight")),
    PathProfile(12, "Kether", "Binah", "What constraints make the target concrete, bounded, and verifiable?", ("crown", "structure")),
    PathProfile(13, "Kether", "Tiferet", "What central principle keeps decisions aligned with the target state?", ("crown", "integration")),
    PathProfile(14, "Chokmah", "Binah", "Which ideas survive structural validation and become usable options?", ("insight", "understanding")),
    PathProfile(15, "Chokmah", "Tiferet", "Which insight should become the central strategy?", ("insight", "strategy")),
    PathProfile(16, "Chokmah", "Chesed", "Which opportunities deserve expansion, resources, or sponsorship?", ("insight", "expansion")),
    PathProfile(17, "Binah", "Tiferet", "Which constraints must be integrated into the main plan?", ("structure", "integration")),
    PathProfile(18, "Binah", "Geburah", "Which rules, risks, or boundaries prevent invalid execution?", ("structure", "discipline")),
    PathProfile(19, "Chesed", "Geburah", "How should expansion be balanced with discipline?", ("mercy", "severity", "polarity")),
    PathProfile(20, "Chesed", "Tiferet", "Which value-producing actions serve the integrated strategy?", ("expansion", "integration")),
    PathProfile(21, "Chesed", "Netzach", "Which growth bets require long-term commitment?", ("expansion", "endurance")),
    PathProfile(22, "Geburah", "Tiferet", "Which risks should reshape the central judgment?", ("discipline", "integration")),
    PathProfile(23, "Geburah", "Hod", "Which controls must be represented in data, metrics, or process?", ("discipline", "analysis")),
    PathProfile(24, "Tiferet", "Netzach", "What sustained behavior keeps the strategy alive?", ("integration", "endurance")),
    PathProfile(25, "Tiferet", "Yesod", "What foundation must exist before the plan can manifest?", ("pathwork", "foundation", "manifestation")),
    PathProfile(26, "Tiferet", "Hod", "What explanation, model, or metric proves the decision is coherent?", ("integration", "communication")),
    PathProfile(27, "Netzach", "Hod", "How do motivation and analysis correct each other?", ("endurance", "analysis", "polarity")),
    PathProfile(28, "Netzach", "Yesod", "What routines convert persistence into readiness?", ("endurance", "foundation")),
    PathProfile(29, "Netzach", "Malkuth", "Which sustained actions are visible in the real world?", ("endurance", "execution")),
    PathProfile(30, "Hod", "Yesod", "Which specifications, tools, or protocols make the plan executable?", ("analysis", "foundation")),
    PathProfile(31, "Hod", "Malkuth", "What evidence in the current state confirms or falsifies the analysis?", ("analysis", "execution")),
    PathProfile(32, "Yesod", "Malkuth", "What minimum viable foundation enables the next concrete step?", ("foundation", "execution")),
)


SEPHIROT_BY_NAME = {profile.name: profile for profile in SEPHIROT}
PATHS_BY_NUMBER = {profile.number: profile for profile in PATHS}
ASCENT_SEPHIROT = tuple(sorted(SEPHIROT, key=lambda item: item.ascent_order))
