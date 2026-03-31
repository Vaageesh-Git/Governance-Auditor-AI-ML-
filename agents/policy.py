class PolicyAgent:

    def decide(self, evaluation, violation_count):

        if evaluation["risk"] == "high":
            return "ESCALATE"

        if evaluation["alignment_break"]:
            return "REVIEW"

        if evaluation["violation"]:
            return "REVIEW"

        return "ALLOW"