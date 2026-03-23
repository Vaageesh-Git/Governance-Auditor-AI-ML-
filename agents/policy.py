class PolicyAgent:

    def decide(self, evaluation, violation_count):

        # Hard rules
        if evaluation["risk"] == "high":
            return "ESCALATE"

        if violation_count > 3:
            return "CRITICAL"

        if evaluation["violation"]:
            return "REVIEW"

        return "ALLOW"