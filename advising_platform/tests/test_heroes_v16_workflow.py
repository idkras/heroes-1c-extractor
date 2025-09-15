#!/usr/bin/env python3
"""
TDD Tests for HeroesGPT MCP Workflow v1.6 Implementation
Based on TDD Documentation Standard 22 May 2025 1830 CET

JTBD: Я хочу убедиться, что MCP workflow реализует все требования Standard v1.6,
чтобы анализ лендингов соответствовал enhanced quality criteria и gap coverage validation.

Test Coverage for Standard v1.6 Enhancements:
- Gap Coverage Analysis (Stage 7.5)
- Enhanced Offer Generation (60+ offers)
- Typography Standards Integration
- Enhanced Validation (90/100 scoring)
"""

import pytest
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List
import sys

sys.path.insert(0, '/home/runner/workspace')

from advising_platform.src.mcp.workflows.heroes_gpt_landing_analysis import HeroesGPTMCPWorkflow

class TestHeroesGPTV16Workflow:
    """Test suite for HeroesGPT v1.6 Standard compliance"""
    
    @pytest.fixture
    def workflow(self):
        """Create workflow instance"""
        return HeroesGPTMCPWorkflow()
    
    @pytest.fixture
    def sample_input(self):
        """Sample input data for testing"""
        return {
            "landing_url": "https://test-landing.com",
            "business_context": {
                "type": "saas",
                "target": "b2b",
                "industry": "productivity"
            },
            "analysis_depth": "full"
        }

    # === CRITICAL TEST: Gap Coverage Analysis ===
    
    @pytest.mark.asyncio
    async def test_gap_coverage_validation_stage_exists(self, workflow):
        """
        JTBD: Test that Stage 7.5 Gap Coverage Validation is implemented
        Standard v1.6 requirement: Systematic gap-to-offer mapping
        """
        # RED: This should fail initially
        assert hasattr(workflow, '_stage_7_5_gap_coverage_validation')
        
        # Verify stage is in workflow_stages definition
        assert "stage_7_5_gap_coverage" in workflow.workflow_stages
        
        gap_stage = workflow.workflow_stages["stage_7_5_gap_coverage"]
        assert "decision_journey_matrix" in gap_stage
        assert "minefield_mitigation_mapping" in gap_stage
        assert "b2b_role_coverage" in gap_stage
        assert "gap_coverage_report" in gap_stage

    @pytest.mark.asyncio 
    async def test_decision_journey_coverage_matrix(self, workflow, sample_input):
        """
        JTBD: Test Decision Journey Coverage Matrix creation
        Standard v1.6: ≥80% coverage requirement for each priority segment
        """
        # Mock data for testing
        segments = [
            {"id": 1, "name": "Tech Founders", "priority": 5},
            {"id": 2, "name": "Sales Teams", "priority": 4}
        ]
        offers = [{"id": i, "text": f"Offer {i}", "stage": i%8+1} for i in range(20)]
        
        matrix = await workflow._create_decision_journey_matrix(segments, offers)
        
        # Validate matrix structure
        assert "segments" in matrix
        assert len(matrix["segments"]) == 2
        
        for segment_data in matrix["segments"]:
            assert "coverage_percentage" in segment_data
            assert segment_data["coverage_percentage"] >= 80  # Standard requirement
            assert "stage_coverage" in segment_data
            assert len(segment_data["stage_coverage"]) == 8  # 8 decision stages

    @pytest.mark.asyncio
    async def test_minefield_mitigation_mapping(self, workflow):
        """
        JTBD: Test Minefield Mitigation Mapping creation
        Standard v1.6: 2 offers per identified mine (prevention + recovery)
        """
        minefields = [
            {"type": "Decision Fatigue", "severity": "high"},
            {"type": "Present Bias", "severity": "medium"},
            {"type": "Status Quo Bias", "severity": "high"}
        ]
        
        mitigation_map = await workflow._create_minefield_mitigation_mapping(minefields)
        
        # Validate mapping structure
        assert "mine_mitigation_pairs" in mitigation_map
        assert len(mitigation_map["mine_mitigation_pairs"]) == 3
        
        for mine_data in mitigation_map["mine_mitigation_pairs"]:
            assert "prevention_offer" in mine_data
            assert "recovery_offer" in mine_data
            assert "effectiveness_score" in mine_data
            assert 1 <= mine_data["effectiveness_score"] <= 5

    # === CRITICAL TEST: Enhanced Offer Generation ===
    
    @pytest.mark.asyncio
    async def test_offer_formula_60_minimum(self, workflow, sample_input):
        """
        JTBD: Test new offer generation formula
        Standard v1.6: (segments × 8 stages) + (6 mines × 2) + 5 risk + 3 competitive = 60+ offers
        """
        # Execute offer generation
        offer_result = await workflow._enhanced_offer_generation(sample_input)
        
        # Validate minimum quantity
        total_offers = len(offer_result["generated_offers"])
        assert total_offers >= 60, f"Expected ≥60 offers, got {total_offers}"
        
        # Validate formula components
        formula_breakdown = offer_result["formula_breakdown"]
        assert formula_breakdown["segment_journey_matrix"] >= 40
        assert formula_breakdown["minefield_mitigation"] == 12  # 6 × 2
        assert formula_breakdown["risk_reducers"] == 5
        assert formula_breakdown["competitive_differentiation"] == 3

    @pytest.mark.asyncio
    async def test_systematic_offer_generation_workflow(self, workflow):
        """
        JTBD: Test 5-phase systematic offer generation
        Standard v1.6: Core Segments → Journey → Mine → Competitive → Risk phases
        """
        phases_result = await workflow._execute_systematic_offer_workflow()
        
        # Validate all 5 phases executed
        assert "phase_a_core_segments" in phases_result
        assert "phase_b_journey_completion" in phases_result  
        assert "phase_c_mine_mitigation" in phases_result
        assert "phase_d_competitive_positioning" in phases_result
        assert "phase_e_risk_reduction" in phases_result
        
        # Validate phase sequencing
        for phase in phases_result.values():
            assert phase["status"] == "completed"
            assert "offers_generated" in phase
            assert phase["offers_generated"] > 0

    # === CRITICAL TEST: Typography Standards ===
    
    @pytest.mark.asyncio
    async def test_typography_cleanup_implementation(self, workflow):
        """
        JTBD: Test Russian typography standards implementation
        Standard v1.6: Post-Analysis Typography Cleanup Checklist
        """
        sample_text = '''
        Это "тестовый" текст с неправильной типографикой.
        Дефисы - вместо тире, проценты 15% без пробелов.
        Сокращения т.е. и т.д. неправильно оформлены.
        '''
        
        cleaned_text = await workflow._apply_typography_cleanup(sample_text)
        
        # Validate typography corrections
        assert "«тестовый»" in cleaned_text  # кавычки ёлочки
        assert " — " in cleaned_text  # тире вместо дефисов  
        assert "15 %" in cleaned_text  # неразрывный пробел в процентах
        assert "т. е." in cleaned_text  # правильное оформление сокращений
        assert "т. д." in cleaned_text

    @pytest.mark.asyncio
    async def test_typography_cleanup_checklist(self, workflow):
        """
        JTBD: Test Post-Analysis Typography Cleanup Checklist validation
        Standard v1.6: 5-point checklist completion
        """
        # Mock final document
        document_content = {
            "title": "Анализ лендинга",
            "content": "Финальный отчет с «правильными» кавычками и тире —",
            "tables": ["Таблица оферов", "JTBD дерево"],
            "recommendations": "Рекомендации по улучшению"
        }
        
        checklist_result = await workflow._validate_typography_checklist(document_content)
        
        # Validate checklist structure
        assert "quotes_checked" in checklist_result
        assert "dashes_corrected" in checklist_result
        assert "non_breaking_spaces" in checklist_result
        assert "numeric_values" in checklist_result
        assert "abbreviations" in checklist_result
        
        # All items should pass for properly formatted content
        for check_name, passed in checklist_result.items():
            assert passed, f"Typography check failed: {check_name}"

    # === CRITICAL TEST: Enhanced Validation ===
    
    @pytest.mark.asyncio
    async def test_enhanced_scoring_system_90_target(self, workflow, sample_input):
        """
        JTBD: Test Enhanced Scoring System with 90/100 target
        Standard v1.6: 30+25+25+20 points breakdown
        """
        # Execute full workflow to generate data for scoring
        workflow_result = await workflow.execute_workflow(sample_input)
        
        # Calculate enhanced score
        scoring_result = await workflow._calculate_enhanced_score(workflow_result)
        
        # Validate scoring breakdown
        assert "completeness_coverage" in scoring_result  # 30 points
        assert "analysis_depth_insight" in scoring_result  # 25 points  
        assert "implementation_quality" in scoring_result  # 25 points
        assert "professional_presentation" in scoring_result  # 20 points
        
        # Validate point allocation
        assert scoring_result["completeness_coverage"] <= 30
        assert scoring_result["analysis_depth_insight"] <= 25
        assert scoring_result["implementation_quality"] <= 25
        assert scoring_result["professional_presentation"] <= 20
        
        total_score = sum([
            scoring_result["completeness_coverage"],
            scoring_result["analysis_depth_insight"], 
            scoring_result["implementation_quality"],
            scoring_result["professional_presentation"]
        ])
        
        # Target score validation
        assert total_score >= 90, f"Expected ≥90/100, got {total_score}"

    @pytest.mark.asyncio
    async def test_jtbd_tree_validation_20_elements(self, workflow):
        """
        JTBD: Test JTBD Tree Validation with 20+ elements requirement
        Standard v1.6: Big (3-7) + Medium (15-35) + Small (60-140) = 20+ total
        """
        # Generate JTBD tree
        jtbd_tree = await workflow._generate_enhanced_jtbd_tree()
        
        # Validate element counts
        big_count = len(jtbd_tree["big_jtbd"])
        medium_count = len(jtbd_tree["medium_jtbd"])
        small_count = len(jtbd_tree["small_jtbd"])
        
        # Validate ranges per standard
        assert 3 <= big_count <= 7, f"Big JTBD count {big_count} outside 3-7 range"
        assert 15 <= medium_count <= 35, f"Medium JTBD count {medium_count} outside 15-35 range"
        assert 60 <= small_count <= 140, f"Small JTBD count {small_count} outside 60-140 range"
        
        # Validate total minimum
        total_elements = big_count + medium_count + small_count
        assert total_elements >= 20, f"Total JTBD elements {total_elements} < 20 minimum"

    @pytest.mark.asyncio
    async def test_segment_analysis_completeness(self, workflow):
        """
        JTBD: Test Segment Analysis Completeness requirements
        Standard v1.6: 5+ segments with viral potential, fears, triggers
        """
        segment_analysis = await workflow._enhanced_segment_analysis()
        
        segments = segment_analysis["segments"]
        
        # Validate segment count
        assert len(segments) >= 5, f"Expected ≥5 segments, got {len(segments)}"
        
        # Validate segment data completeness
        for segment in segments:
            assert "viral_potential_score" in segment
            assert 1 <= segment["viral_potential_score"] <= 5
            assert "primary_fear" in segment
            assert "secondary_fear" in segment
            assert "morning_thoughts" in segment
            assert "evening_fears" in segment
            assert "trigger_situations" in segment
            assert len(segment["trigger_situations"]) >= 3

    # === INTEGRATION TEST: Full Standard v1.6 Compliance ===
    
    @pytest.mark.asyncio
    async def test_full_v16_workflow_compliance(self, workflow, sample_input):
        """
        JTBD: Test complete workflow compliance with Standard v1.6
        Integration test covering all enhancements
        """
        # Execute full workflow
        result = await workflow.execute_workflow(sample_input)
        
        # Validate all new stages present
        assert "stage_7_5_gap_coverage" in result["stages"]
        
        # Validate enhanced offer generation
        offers_count = len(result["final_output"].get("generated_offers", []))
        assert offers_count >= 60
        
        # Validate typography compliance
        final_document = result["final_output"]["formatted_document"]
        assert workflow._validate_typography_compliance(final_document)
        
        # Validate enhanced scoring
        final_score = result["final_output"]["enhanced_score"]["total"]
        assert final_score >= 90
        
        # Validate v1.6 standard loading
        assert result["standard_content"]["version"] == "1.6"
        
        # Validate reflections include gap coverage
        gap_coverage_reflection = any(
            "gap coverage" in r["question"].lower() 
            for r in result["reflections"]
        )
        assert gap_coverage_reflection

if __name__ == "__main__":
    pytest.main([__file__, "-v"])