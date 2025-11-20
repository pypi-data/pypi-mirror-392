import time
import threading
from gi import GeneralIntelligence, Knowledge
from itertools import combinations

gi = GeneralIntelligence()

# -----------------------------
# ML-Style Additive Knowledge
# -----------------------------
class AdditiveKnowledge(Knowledge):
    """
    Learns additive relationships between input features and targets.
    """

    def __init__(self, n_features):
        self.n_features = n_features
        self.valid_combinations = []

    def on(self, ctx, gi):
        if not hasattr(ctx, "row"):
            return None
        row = ctx.row
        target = getattr(ctx, "target", None)
        is_train = hasattr(ctx, "target") and target is not None

        if is_train:
            # If first row, generate all possible combinations
            if not self.valid_combinations:
                all_combs = []
                for r in range(1, self.n_features + 1):
                    all_combs.extend(combinations(range(self.n_features), r))
                self.valid_combinations = [
                    comb for comb in all_combs if sum(row[i] for i in comb) == target
                ]
            else:
                # Filter combinations to keep only those consistent with this row
                self.valid_combinations = [
                    comb for comb in self.valid_combinations if sum(row[i] for i in comb) == target
                ]
            return None
        else:
            if not self.valid_combinations:
                return None
            # Pick the first combination for demonstration
            comb = self.valid_combinations[0]
            return sum(row[i] for i in comb)


additive = AdditiveKnowledge(n_features=3)
gi.learn(additive)

# Training
class TrainCtx:
    def __init__(self, row, target):
        self.row = row
        self.target = target

for row, target in [([1,2,3], 3), ([0,3,1], 3)]:
    list(gi.on(TrainCtx(row, target)))

# Prediction
class PredictCtx:
    def __init__(self, row):
        self.row = row

prediction_row = [2,1,0]
print("ML Prediction:", next(gi.on(PredictCtx(prediction_row))))


# -----------------------------
# Dialog / Prompt-Response Knowledge
# -----------------------------
class DialogKnowledge(Knowledge):
    def __init__(self):
        self.history = []

    def on(self, ctx, gi):
        if hasattr(ctx, "user"):
            self.history.append(ctx.user)
            return f"Bot: I heard '{ctx.user}'"

dialog = DialogKnowledge()
gi.learn(dialog)

class UserCtx:
    def __init__(self, user):
        self.user = user

for response in gi.on(UserCtx("Hello")):
    print(response)
for response in gi.on(UserCtx("How are you?")):
    print(response)


# -----------------------------
# Autonomous Knowledge Example
# -----------------------------
class TimerKnowledge(Knowledge):
    def __init__(self):
        self.count = 0

    def on_add(self, knowledge, gi):
        if self is knowledge:
            self.running = True
            self.thread = threading.Thread(target=self.run, args=(gi,), daemon=True)
            self.thread.start()

    def on_remove(self, knowledge, gi):
        if self is knowledge:
            self.running = False

    def run(self, gi):
        while getattr(self, "running", False):
            print("Tick:", self.count)
            self.count += 1
            time.sleep(1)

class TickCtx: pass
timer = TimerKnowledge()
gi.learn(timer)

# Let autonomous timer run a few ticks
time.sleep(5)
gi.unlearn(timer)  # stop autonomous loop


# -----------------------------
# Compositional Reasoning
# -----------------------------
class AccumulateKnowledge(Knowledge):
    def compose(self, ctx, composer, gi):
        if not hasattr(ctx, "accum"):
            ctx.accum = []
        ctx.accum.append("step")

acc = AccumulateKnowledge()
gi.learn(acc)

class DummyCtx: pass

def final_composer(ctx):
    return getattr(ctx, "accum", [])

print("Compositional Output:", gi.compose(DummyCtx(), final_composer))  # ['step']
