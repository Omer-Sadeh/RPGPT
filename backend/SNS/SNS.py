import logging
import backend.SNS.Checks as Checks
from backend.SNS.I_Check import Check, EditCheck

"""
Security and Safety checks service.
"""


class FinalDecision:
    """
    Final decision object.
    Can be used to store the decision, updated request, and reason for the decision., and be addressed as a boolean.

    :param decision: The decision.
    :param updated_req: The updated request.
    :param reason: The reason for the decision.

    :return: The final decision object.
    """
    def __init__(self, decision: bool, updated_req: str, reason: str):
        self.decision: bool = decision
        self.updated_req: str = updated_req
        self.reason: str = reason

    def __str__(self):
        return f"Decision: {self.decision}, Reason: {self.reason}"

    def __repr__(self):
        return self.__str__()

    def __bool__(self):
        return self.decision

    def to_dict(self):
        return {"decision": self.decision, "updated_req": self.updated_req, "reason": self.reason}


def _process_checks(req: str, checks: list[Check]) -> FinalDecision:
    """
    Process the checks for the request.

    :param req: The request to check.
    :param checks: The checks to run.
    :return: True if the request passes the checks, False otherwise.
    """
    updated_req = req
    decision = True
    msg = "All checks passed."

    for control in checks:
        try:
            if isinstance(control, EditCheck):
                updated_req = control.run(updated_req)
                logging.info(f"Updated request: {updated_req}")
            elif isinstance(control, Check):
                if not control.run(updated_req):
                    decision = False
                    msg = control.block_msg
                    break
            else:
                raise ValueError("Invalid check type.")
        except Exception as e:
            decision = False
            msg = "Internal error occurred for the check: " + str(e)
            break

    return FinalDecision(decision, updated_req, msg)


def llm_input(req: str) -> FinalDecision:
    """
    Check an input for a LLM.

    :param req: The request to check.
    :return: The final decision object.
    """
    logging.info(f"Checking guardrails for input: {req}")

    checks: list[Check] = [
        Checks.LengthCheck(100),
        Checks.InvalidCharsCheck(["[", "]", "{", "}", "<", ">", ";", "/", "\\", "|", "@", "#", "%", "^", "&", "*", "~", "`"]),
        Checks.InvalidExpressionsCheck(["ignore all previous"])
    ]

    return _process_checks(req, checks)


def save_system(req: str) -> FinalDecision:
    """
    Check the input for file system files.

    :param req: The input to check.
    :return: The final decision object.
    """
    logging.info(f"Checking guardrails for input: {req}")

    checks: list[Check] = [
        Checks.LengthCheck(8),
        Checks.SpecialCharsCheck(mask='X')
    ]

    return _process_checks(req, checks)
