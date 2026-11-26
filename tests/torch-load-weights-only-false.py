import torch

# ruleid: torch-load-weights-only-false
a = torch.load("x.pt", weights_only=False, map_location="cpu")["state_dict"]

# ruleid: torch-load-weights-only-false
b = torch.load("x.pt", map_location="cpu", weights_only=False)

# ok: torch-load-weights-only-false
c = torch.load("x.pt", map_location="cpu")

# ok: torch-load-weights-only-false
d = torch.load("x.pt", weights_only=True)
