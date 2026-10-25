import re

ANSWER = re.compile(r"<answer>\s*([01](?:\.\d+)?)\s*</answer>")
FORMAT = re.compile(r"^\s*<think>.+?</think>\s*<answer>.+?</answer>\s*$", re.S)

def _text(c):
    return c[0]["content"] if isinstance(c, list) else c

def format_reward(completions, **kw):
    return [1.0 if FORMAT.match(_text(c)) and ANSWER.search(_text(c)) else 0.0
            for c in completions]

def accuracy_reward(completions, truth, **kw):
    out = []
    for c, t in zip(completions, truth):
        m = ANSWER.search(_text(c))
        if not m:
            out.append(0.0)
            continue
        p = min(max(float(m.group(1)), 0.0), 1.0)
        out.append(1.0 - abs(p - t))   # in [0,1], linear
    return out