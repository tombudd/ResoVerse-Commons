import unittest

from resoverse_commons.learning import validate_learning_candidate


def candidate():
    return {"candidateVersion": "1.0", "id": "counterexample-1", "provenance": {"sourceUrl": "https://example.com/source", "license": "Apache-2.0", "authors": ["Contributor"], "rightsToSubmit": True}, "artifacts": [{"path": "fixture.json", "sha256": "a" * 64}], "learningUse": {"consent": "explicit_learning_candidate", "intendedUse": "counterexample", "automaticPromotion": False}, "revocation": {"supported": True, "contact": "security@example.com"}}


class LearningCandidateTests(unittest.TestCase):
    def test_valid_candidate_waits_for_review_without_changing_the_project(self):
        receipt = validate_learning_candidate(candidate())
        self.assertEqual(receipt["status"], "waiting_for_review")
        self.assertFalse(receipt["addedToProject"])
        self.assertFalse(receipt["softwareChanged"])
        self.assertFalse(receipt["codeRun"])

    def test_consent_and_revocation_are_required(self):
        value = candidate()
        value["learningUse"]["consent"] = "implicit"
        value["revocation"]["supported"] = False
        receipt = validate_learning_candidate(value)
        self.assertEqual(receipt["status"], "needs_changes")
        self.assertIn("EXPLICIT_LEARNING_CONSENT_REQUIRED", receipt["reasonCodes"])
        self.assertIn("REVOCATION_PATH_REQUIRED", receipt["reasonCodes"])
