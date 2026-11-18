"""GeckoLib animation keyframes ({'vector', 'easing'}) -> dense linear Bedrock keyframes for Cobblemon."""
import json, math

def back(t, n=1.70158):
    return t * t * ((n + 1) * t - n)

def bounce(t, n=0.5):
    one = 121 / 16 * t * t
    two = 121 / 4 * n * (t - 6 / 11) ** 2 + 1 - n
    three = 121 * n * n * (t - 9 / 11) ** 2 + 1 - n * n
    four = 484 * n ** 3 * (t - 10.5 / 11) ** 2 + 1 - n ** 3
    return min(one, two, three, four)

EASE = {
    'linear': lambda t: t, None: lambda t: t,
    'easeInBack': back, 'easeOutBack': lambda t: 1 - back(1 - t), 'easeInOutBack': lambda t: back(2 * t) / 2 if t < .5 else 1 - back(2 - 2 * t) / 2,
    'easeInSine': lambda t: 1 - math.cos(t * math.pi / 2), 'easeOutSine': lambda t: math.sin(t * math.pi / 2),
    'easeInOutSine': lambda t: -(math.cos(math.pi * t) - 1) / 2,
    'easeInBounce': bounce, 'easeOutBounce': lambda t: 1 - bounce(1 - t),
    'easeInCirc': lambda t: 1 - math.sqrt(max(0, 1 - t * t)), 'easeOutCirc': lambda t: math.sqrt(max(0, 1 - (t - 1) ** 2)),
    'easeInQuad': lambda t: t * t, 'easeOutQuad': lambda t: 1 - (1 - t) ** 2,
    'easeInOutQuad': lambda t: 2 * t * t if t < .5 else 1 - (-2 * t + 2) ** 2 / 2,
    'easeInCubic': lambda t: t ** 3, 'easeOutCubic': lambda t: 1 - (1 - t) ** 3,
}

def keys(ch):
    """channel -> sorted [(time, vec, easing)]"""
    if isinstance(ch, dict) and 'vector' in ch:
        return [(0.0, ch['vector'], None)]
    if isinstance(ch, list):
        return [(0.0, ch, None)]
    out = []
    for t, k in ch.items():
        if isinstance(k, dict):
            out.append((float(t), k.get('vector', k.get('post')), k.get('easing')))
        else:
            out.append((float(t), k, None))
    return sorted(out, key=lambda x: x[0])

def value(ks, t):
    if t <= ks[0][0]:
        return list(ks[0][1])
    for (t0, v0, _), (t1, v1, e1) in zip(ks, ks[1:]):
        if t0 <= t <= t1:
            if t1 == t0:
                return list(v1)
            f = EASE[e1]((t - t0) / (t1 - t0))
            return [a + (b - a) * f for a, b in zip(v0, v1)]
    return list(ks[-1][1])

def sample(anim, fps=24, length=None, t0=0.0, speed=1.0, bones=None):
    """GeckoLib animation -> {bone: {channel: [(t_out, vec)]}} sampled at fps (output time = (t - t0) / speed)"""
    L = length if length is not None else anim.get('animation_length', 1.0)
    out = {}
    n = max(1, int(round(L * fps / speed)))
    for b, chans in anim['bones'].items():
        if bones is not None and b not in bones:
            continue
        for c, ch in chans.items():
            ks = keys(ch)
            seq = []
            for i in range(n + 1):
                to = i / fps
                seq.append((round(to, 4), value(ks, t0 + to * speed)))
            out.setdefault(b, {})[c] = seq
    return out, n / fps

def to_bedrock(samples, length, loop):
    bones = {}
    for b, chans in samples.items():
        for c, seq in chans.items():
            vals = [v for _, v in seq]
            if all(max(abs(x - y) for x, y in zip(v, vals[0])) < 1e-4 for v in vals):
                v = [round(x, 3) for x in vals[0]]
                if (c != 'scale' and v == [0, 0, 0]) or (c == 'scale' and v == [1, 1, 1]):
                    continue
                bones.setdefault(b, {})[c] = v
                continue
            # drop samples that a straight line through their neighbours already gives
            keep = [0]
            for i in range(1, len(seq) - 1):
                (ta, va), (tb, vb), (tc, vc) = seq[keep[-1]], seq[i], seq[i + 1]
                f = (tb - ta) / (tc - ta)
                lin = [a + (cc - a) * f for a, cc in zip(va, vc)]
                if max(abs(x - y) for x, y in zip(lin, vb)) > 0.15:
                    keep.append(i)
            keep.append(len(seq) - 1)
            bones.setdefault(b, {})[c] = {f"{seq[i][0]:.4f}".rstrip('0').rstrip('.') if seq[i][0] else "0.0": [round(x, 3) for x in seq[i][1]] for i in keep}
    a = {"animation_length": round(length, 4), "bones": bones}
    if loop is True:
        a["loop"] = True
    elif loop == 'hold':
        a["loop"] = "hold_on_last_frame"
    return a
