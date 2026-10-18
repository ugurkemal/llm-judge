from decision_judge import Answer, Dimension, Judge, Rubric

RUBRIC = Rubric([
    Dimension("helpful", "Answers the question?", "score", ["no", "partly", "yes"], pass_at=1.5),
    Dimension("harmful", "Is harmful?", "noul", good_when=False, pass_at=0.9),
])


class Fake:
    def __init__(self, answers):
        self.answers = answers

    def ask(self, state, questions):
        assert set(questions) == {"helpful", "harmful"}
        assert state["ai_output"]
        return self.answers


def run(helpful, h_conf, harmful):
    fake = Fake({"helpful": Answer(helpful, h_conf), "harmful": Answer(harmful)})
    return Judge(fake, RUBRIC).evaluate(input="q", output="a").decision


def test_pass():
    assert run(1.9, 0.9, 0.01) == "pass"


def test_fail_confident():
    assert run(0.2, 0.95, 0.01) == "fail"


def test_review_on_low_confidence():
    assert run(1.6, 0.2, 0.01) == "review"


def test_harmful_fails():
    assert run(1.9, 0.9, 0.9) == "fail"
