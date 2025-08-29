import hmac, hashlib, struct
def load_key(path="/run/secrets/aead_key"): return open(path,"rb").read()
def frame_tag(secret, track_id:int, frame_idx:int, pn:bytes, tag_bits=64):
    msg = struct.pack(">QQ", track_id, frame_idx) + bytes((x+1)//2 for x in pn)
    tag = hmac.new(secret, msg, hashlib.sha256).digest()
    nbytes = tag_bits//8
    return tag[:nbytes]  # transmit/verify truncated tag
def verify_tag(secret, track_id, frame_idx, pn, tag):
    return hmac.compare_digest(frame_tag(secret, track_id, frame_idx, pn, len(tag)*8), tag)