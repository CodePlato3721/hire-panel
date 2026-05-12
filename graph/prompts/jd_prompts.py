# graph/prompts/jd_prompts.py

EXTRACT_JD_SYSTEM = """You are an expert HR analyst.
Extract 4-6 key scoring criteria from the job description.
Each criterion should be specific and independently assessable.
Return them in order of importance."""

REVISE_CRITERIA_SYSTEM = """You are an expert HR analyst.
Revise the scoring criteria based on HR feedback.
Keep unchanged criteria that were not mentioned."""