from agents import Agent, Runner, WebSearchTool, CodeInterpreterTool, trace
import asyncio 
from pydantic import BaseModel

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

class differentialsOutput(BaseModel):
    differentials: list[str]

differentials_agent = Agent (
    name="DifferentialsAssistant",
    handoff_description="This agent generates a list of differential diagnoses based on the provided clinical presentation. ",
    instructions="Act as a professor/consultant in Emergency Medicine. " \
    "Your task is to generate a list of differential diagnoses based " \
    "on the provided clinical presentation given to you in JSON format." \
    "Context: You are part of a Clinical Decision Support application that mitigates " \
    "for human factors in Doctors assessing patients in the Emergency Department. Your differentials " \
    "shall guide the calculations made by the calculator agent.",
    output_type= differentialsOutput,
    model="gpt-5",
)

class preTestProbabilityOutput(BaseModel):  
    differential: str
    pre_test_probability: float
    reference: str

pre_test_probability_agent = Agent (
    name="PreTestProbabilityAssistant",
    handoff_description="This agent identifies the pre-test probability of a condition",
    instructions= "Act as a senior professor of evidence-based medicine and an experienced statistician."
    "Your task is to identify the pre-test probability of a condition given the presenting complaint, age and gender of the patient"
    "Context: You are part of a Clinical Decision Support application that mitigates "
    "for human factors in Doctors assessing patients in the Emergency Department. Your pre-test probability "
    "shall guide the calculations made by the calculator agent.",
    output_type= preTestProbabilityOutput,
    tools=[WebSearchTool(), CodeInterpreterTool()],
    model="gpt-5",
)

class DifferentialFeature(BaseModel):
    feature: str                         # name of clinical feature
    lr_type: Literal["LR+", "LR-"]       # whether using LR+ or LR-
    likelihood_ratio: float              # numeric LR value applied
    direction: Literal["increase", "decrease", "neutral"]
    evidence_ids: List[str]

    class Config:
        extra = "forbid"


class LikelihoodRatiosOutput(BaseModel):
    likelihood_ratios: List[DifferentialFeature]

    
likelihood_ratios_agent = Agent (
    name="LikelihoodRatiosAssistant",
    handoff_description="This agent identifies the likelihood ratios for a given condition",
    instructions= "Act as a senior professor of evidence-based medicine and an experienced statistician."
    "Your task is to identify all the likelihood ratios for a given condition given the clinical features, both positive and negative."
    "Context: You are part of a Clinical Decision Support application that mitigates "
    "for human factors in Doctors assessing patients in the Emergency Department. Your likelihood ratios "
    "shall guide the calculations made by the calculator agent to calculate the probability of this differential given this clinical picture." \
    "Please output as a JSON object with clinical feature as the key and likelihood ratio as the value." \
    "Make sure to specify if the likelihood ratio is positive or negative.",
    output_type= likelihoodRatiosOutput,
    tools=[WebSearchTool(), CodeInterpreterTool()],
    model="gpt-5",  
)

class calculatorOutput(BaseModel):
    differential: str
    post_test_probability: float
calculator_agent = Agent (  
    name="CalculatorAssistant",
    handoff_description="This agent calculates the post-test probability of a condition given the pre-test probability and likelihood ratios.",
    instructions= "Act as a senior professor of evidence-based medicine and an experienced statistician."
    "Your task is to calculate the post-test probability of a condition given the pre-test probability and likelihood ratios."
    "Context: You are part of a Clinical Decision Support application that mitigates "
    "for human factors in Doctors assessing patients in the Emergency Department. Your calculations "
    "shall guide the final diagnosis made by the system.",
    output_type= calculatorOutput,
    model="gpt-5",  
    tools=[CodeInterpreterTool(),WebSearchTool()]
)

from pydantic import BaseModel, Field
from typing import List, Dict, Literal


# -----------------------------
# Applied Features
# -----------------------------
class AppliedFeature(BaseModel):
    condition: str
    feature: str
    value: str
    likelihood_ratio: float
    direction: Literal["increase", "decrease", "neutral"]
    evidence_ids: List[str]

    class Config:
        extra = "forbid"


# -----------------------------
# Differentials
# -----------------------------
class Differential(BaseModel):
    rank: int = Field(..., ge=1)
    diagnosis: str
    probability: float = Field(..., ge=0, le=1)
    feature_notes: str
    evidence_ids: List[str]
    confidence: Literal["high", "medium", "low"]

    class Config:
        extra = "forbid"


# -----------------------------
# Recommended Investigations Subtypes
# -----------------------------
class InvestigationItem(BaseModel):
    test: str
    priority: int = Field(..., ge=1)
    rationale: str
    targets: List[str] = Field(..., min_items=1)
    safety_priority: bool
    evidence_ids: List[str]

    class Config:
        extra = "forbid"


class RecommendedInvestigations(BaseModel):
    bloods: List[InvestigationItem]
    bedside: List[InvestigationItem]
    radiology: List[InvestigationItem]

    class Config:
        extra = "forbid"


# -----------------------------
# Main Model
# -----------------------------
class DifferentialProbabilityAssessment(BaseModel):
    case_id: str
    applied_features: List[AppliedFeature]
    differentials: List[Differential]
    recommended_investigations: RecommendedInvestigations
    missing_fields: List[str]

    class Config:
        extra = "forbid"
        # strict mode equivalent
        validate_assignment = True


gathering_agent = Agent (
    name="GatheringAssistant",
    handoff_description="This agent gathers all the differentials, their likelihood ratios and their post-test probabilities, ranks the likelihoods" \
    "and recommends investigations.",
    instructions= "Act as a senior professor of evidence-based medicine and an emergency medicine consultant." \
    "Your task is to gather all the differentials and their applied LRs and post-test probabilities, rank the conditions based on likelihood" \
    "and recommend investigations to confirm or rule out any differentials with probability >= 2%." \
    "Context: You are part of a Clinical Decision Support application that mitigates " \
    "for human factors in Doctors assessing patients in the Emergency Department. Your recommendations " \
    "shall guide the diagnosis made by the doctor.",   
    model="gpt-5",  
    tools=[WebSearchTool(), CodeInterpreterTool()],
    output_type= DifferentialProbabilityAssessment,
)

async def main():
    msg = """ {
    "presenting_complaint": "Chest Pain",
    "age": 66,
    "gender": "male",
    "past_medical_history": "high cholesterol, angina, high blood pressure, PAD, smoker, drinker, NAFLD, AF",
    "drug_history": "statin, apixaban, ramipril, bisoprolol",
    "obs_hr": 120,
    "obs_temp": 37.0,
    "obs_sats": 96,
    "obs_rr": 27,
    "obs_dbp": 70,
    "obs_sbp": 100,
    "site_of_pain": "retrosternal",
    "onset_timing": "sudden (seconds\u2013minutes)",
    "character_of_pain": [
      "tearing/ripping"
    ],
    "radiation": [
      "back (interscapular)"
    ],
    "exertional_pain": false,
    "compare_with_prior_angina": "similar to prior ischemia",
    "radiation_both_arms_specific": false,
    "diaphoresis_present": true,
    "nausea_vomiting_present": false,
    "pleuritic_pain": false,
    "positional_worse_supine": false,
    "pain_reproducible_by_palpation": false,
    "sudden_tearing_quality": true,
    "syncope_with_pain": false,
    "hemoptysis_present": false,
    "sudden_unilateral_pleuritic_pain": false,
    "sudden_or_progressive_dyspnoea": "sudden onset",
    "gi_features_reflux": [],
    "msk_modifiers": [],
    "fever_history": false,
    "time_course_pattern": "constant",
    "severity_nrs": 9,
    "cv_review": [],
    "resp_review": [],
    "gi_review": [],
    "neuro_review": [],
    "cv_risk_pmhx": [
      "hypertension",
      "hyperlipidaemia",
      "known CAD/angina",
      "connective tissue disorder"
    ],
    "pe_risk_history": [],
    "resp_pmhx": [],
    "current_medicines": "as history",
    "drug_allergies": "nkda",
    "smoking_status": "never",
    "pack_years": 0,
    "alcohol_intake": 0,
    "recreational_drugs": "none",
    "recent_travel_immobility": "no",
    "recent_surgery_or_cancer_treatment": "none",
    "heart_rate": 120,
    "resp_rate": 27,
    "oxygen_saturation": 96,
    "temperature": 36.7,
    "systolic_bp_right": 98,
    "systolic_bp_left": 66,
    "bp_or_pulse_differential": true,
    "general_appearance": [
      "diaphoretic"
    ],
    "chest_wall_tenderness_exam": false,
    "heart_sounds_s3": false,
    "murmurs": [
      "new diastolic murmur of aortic regurgitation"
    ],
    "lung_auscultation": [
      "clear bilaterally"
    ],
    "chest_percussion": [
      "normal"
    ],
    "trachea_position": "midline",
    "leg_exam_for_dvt": [
      "no swelling/tenderness"
    ],
    "describe_ecg": "",
    "hemodynamic_instability": true,
    "sudden_tearing_pain_redflag": true,
    "pulse_or_bp_differential_redflag": true,
    "new_neuro_deficit_redflag": false,
    "syncope_with_chest_pain": false,
    "severe_hypoxia_redflag": false,
    "tension_pneumothorax_signs": false,
    "massive_hemoptysis": false
  } """
   # Step 1 — Get differentials
    with trace("Differential Diagnoses Agent"):
        differentials_result = await Runner.run_async(differentials_agent, msg)

    print("Differentials:", differentials_result.final_output.differentials)


    # Step 2 — Build ALL tasks for ALL differentials before awaiting anything
    tasks = []

    with trace("Building Parallel Diagnostic Tasks"):
        for dx in differentials_result.final_output.differentials:
            tasks.append(
                asyncio.gather(
                    Runner.run(
                        pre_test_probability_agent,
                        f"""
                        Given the presenting complaint of "Chest Pain"
                        and the differential diagnosis "{dx}",
                        provide the pre-test probability as a float between 0 and 1
                        along with a reference.
                        """
                    ),
                    Runner.run(
                        likelihood_ratios_agent,
                        f"""
                        Given the presenting complaint of "Chest Pain"
                        and the differential diagnosis "{dx}",
                        provide all relevant positive and negative likelihood ratios
                        based on the clinical features.
                        """
                    )
                )
            )


    # Step 3 — Execute EVERYTHING in parallel
    with trace("Executing All Differential Tasks in Parallel"):
        results = await asyncio.gather(*tasks)

    calcs = []
    # Step 4 — Unpack results
    for dx, (pretest, lrs) in zip(differentials_result.final_output.differentials, results):
        print(f"\n===== {dx} =====")
        print("Pre-test probability:", pretest.final_output)
        print("Likelihood ratios:", lrs.final_output)
    
    # Step 5 — Calculate post-test probability
    with trace("Calculating Post-Test Probabilities"):
        for dx, (pretest, lrs) in zip(differentials_result.final_output.differentials, results):
            calcs.append(
                asyncio.gather(
                    Runner.run(
                        calculator_agent,
                        f"""
                        Given the pre-test probability of {pretest.final_output.pre_test_probability} and the likelihood ratios
                        {', '.join([f"{feature.feature}: {feature.likelihood_ratio} ({feature.lr_type})" for feature in lrs.final_output.likelihood_ratios])},
                        calculate the post-test probability for the differential "{dx}".
                        """
                    )
                )
            calc_result = await asyncio.gather(*calcs)
            for dx, calc in zip(differentials_result.final_output.differentials, calc_result):
                print(f"Post-test probability for {dx}: {calc.final_output.post_test_probability}")