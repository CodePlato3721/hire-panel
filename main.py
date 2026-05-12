# main.py
from tests.integration.test_jd_flow import run_jd_flow
from tests.integration.test_resume_flow import run_resume_flow
from tests.integration.test_feedback_flow import run_feedback_flow

if __name__ == "__main__":
    criteria = run_jd_flow()
    resumes = run_resume_flow(criteria)
    run_feedback_flow(criteria, resumes)