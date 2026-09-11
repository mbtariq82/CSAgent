from pydantic import ValidationError

from security_agent.domain import CodeEvidence, Confidence, Finding, Severity
from security_agent.domain import Scope


def make_evidence() -> CodeEvidence:
    return CodeEvidence(
        file_path="src/auth.py",
        line_start=10,
        line_end=12,
        explanation="Untrusted input reaches query construction.",
    )


def test_scope_accepts_an_absolute_root_without_accessing_it(tmp_path):
    # Use tmp_path / "repository-that-does-not-exist".
    # Construct Scope successfully even though the directory does not exist.
    scope = Scope(root = tmp_path / "repository-that-does-not-exist")
    # Assert scope.root equals the supplied absolute path.
    assert scope.root == tmp_path / "repository-that-does-not-exist"

def test_scope_rejects_a_relative_root():
    # Scope(root=Path("relative/repository")) must raise ValidationError.
    try:
        Scope(root="relative/repository")
    except ValidationError as e:
        assert "Scope root must be an absolute path" in str(e)

def test_valid_hypothesis_round_trips_through_json_data():
    # Construct a HYPOTHESIS Finding with confidence but no evidence.
    # Dump it with model_dump(mode="json").
    # Rebuild it with Finding.model_validate(...).
    # Assert the rebuilt finding equals the original finding.
    finding = Finding(
        summary="Test finding",
        severity=Severity.LOW,
        confidence=0.8,
    )
    json_data = finding.model_dump(mode="json")
    rebuilt_finding = Finding.model_validate(json_data)
    assert rebuilt_finding == finding

def test_confidence_is_bounded():
    # Parameterize at least one value below 0 and one above 1.
    try:
        Confidence(-0.1)
    except ValidationError as e:
        assert "ensure this value is greater than or equal to 0.0" in str(e)
    try:
        Confidence(1.1)
    except ValidationError as e:
        assert "ensure this value is less than or equal to 1.0" in str(e)

def test_evidence_rejects_unsafe_paths():
    # Parameterize at least these inputs:
    # /etc/passwd
    # C:\\Windows\\system.ini
    # src/../../secret.txt
    
    raise NotImplementedError("TO DO")








def test_evidence_normalizes_windows_separators():
    # src\\auth.py must become src/auth.py.
    raise NotImplementedError("TO DO")


def test_evidence_requires_an_ordered_line_range():
    # line_start=12 and line_end=10 must raise ValidationError.
    raise NotImplementedError("TO DO")


def test_supported_finding_requires_evidence():
    # SUPPORTED with evidence=() must raise ValidationError.
    raise NotImplementedError("TO DO")


def test_supported_finding_accepts_evidence():
    # SUPPORTED with make_evidence() must be valid.
    raise NotImplementedError("TO DO")


def test_unknown_fields_are_rejected():
    # Pass an invented field to Confidence and expect ValidationError.
    raise NotImplementedError("TO DO")


def test_domain_models_are_frozen():
    # Construct Confidence, try assigning a new score, and expect ValidationError.
    raise NotImplementedError("TO DO")
