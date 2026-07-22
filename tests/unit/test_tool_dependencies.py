"""Tests to reproduce the plan validation/dependency bug (Issue #54).

These tests prove that the Orchestrator currently constructs and executes plans
sequentially without validating prerequisites, topological order, or circular dependencies.
"""

import pytest

from agent.orchestrator import Orchestrator
from agent.tools.market_analyzer import MarketAnalyzer
from agent.tools.readme_scorer import ReadmeScorer
from agent.tools.skill_extractor import SkillExtractor
from agent.tools.tech_detector import TechDetector


@pytest.mark.unit
class TestOrchestratorDependencyBug:
    """Test suite demonstrating the lack of tool prerequisite validation."""

    @pytest.fixture
    def tools(self):
        """Create dictionary of real tool instances."""
        return {
            "tech_detector": TechDetector(),
            "readme_scorer": ReadmeScorer(),
            "skill_extractor": SkillExtractor(),
            "market_analyzer": MarketAnalyzer(),
        }

    @pytest.fixture
    def orchestrator(self, tools):
        """Create an Orchestrator instance with the tools."""
        return Orchestrator(tools=tools)

    def test_orchestrator_runs_with_missing_dependencies(self, orchestrator):
        """Proves that Orchestrator runs tools without satisfying their dependencies.

        In this test, we run 'market_analyzer' directly via a profile that has no preceding
        tools in the execution plan to supply skills (e.g. no resume_text provided).
        The orchestrator executes 'market_analyzer' successfully without any validation warning
        or exception, even though 'market_analyzer' has no skills to analyze.
        """
        # Profile has no files or resume_text, meaning tech_detector
        # and skill_extractor won't be planned, but because plan is non-empty,
        # we trigger the market_analyzer directly.
        # Let's inspect _build_plan:
        # If profile_data is empty, _build_plan returns an empty plan.
        # Let's pass a profile with only "github_username" and "projects".
        # This will plan "github_tool" and "market_analyzer".
        # Let's see if we can provide resume_text but we manually craft or trigger a plan.
        profile_data = {
            "github_username": "testuser",
            "projects": [{"github_repo": "testrepo"}],
            # Note: No files, No resume_text.
            # So tech_detector and skill_extractor are NOT planned.
            # But market_analyzer WILL be planned because 'plan' is non-empty (due to github_tool),
            # but since we didn't register github_tool, let's see. If github_tool is not in tools,
            # _execute_tool raises ValueError. But we can register a dummy/mock/stub tool.
        }

        # Let's mock _build_plan or pass a custom plan to prove the execution loop runs.
        # Alternatively, we can patch _build_plan to return a plan with unsatisfied dependencies:
        plan = [("market_analyzer", {"detected_skills": {}})]
        orchestrator._build_plan = lambda x: plan

        # Execute orchestrator. It should fail or raise a validation error, but currently it runs
        # and returns a successful result for market_analyzer with empty data.
        result = orchestrator.run("profile_1", profile_data)

        # Confirm that orchestrator ran without raising any validation error
        assert "market_analyzer" in result["tool_results"]
        # The tool result is successful but empty
        assert result["tool_results"]["market_analyzer"]["market_alignment_score"] == 0.0

    def test_orchestrator_runs_out_of_order(self, orchestrator):
        """Proves that Orchestrator runs tools in an invalid topological order.

        If we provide a plan where 'market_analyzer' runs before 'skill_extractor',
        the orchestrator executing the plan sequentially does not detect the invalid ordering.
        It runs 'market_analyzer' with empty context, then runs 'skill_extractor'.
        """
        # Out-of-order plan: dependent tool 'market_analyzer' runs BEFORE 'skill_extractor'
        plan = [
            ("market_analyzer", {"detected_skills": {}}),
            ("skill_extractor", {"resume_text": "Python, SQL, React", "repo_metadata": {}}),
        ]
        orchestrator._build_plan = lambda x: plan

        # Execute orchestrator. No validation exception is raised.
        result = orchestrator.run("profile_2", {})

        # Confirm that orchestrator successfully ran both tools in the wrong order
        assert "market_analyzer" in result["tool_results"]
        assert "skill_extractor" in result["tool_results"]
        # market_analyzer should have analyzed the extracted skills, but because of wrong order,
        # it has an empty alignment score.
        assert result["tool_results"]["market_analyzer"]["market_alignment_score"] == 0.0
