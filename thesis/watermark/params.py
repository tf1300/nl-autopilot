SR = 44100
FRAME = 2048           # ~46.4 ms
HOP = 1024             # 50% overlap
SYNC_CHIPS = 64        # per frame
EMBED_PERIOD_S = 5     # payload repetition
ALPHA = 0.05          # embed strength (tune later)
BANDS = (3000, 6000)   # Hz sub-band for spread
TAG_BITS = 64          # HMAC tag truncation