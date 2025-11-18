class QuantizeFP8(torch.nn.Module):
    class _QuantizeFP8(torch.autograd.Function):
        @staticmethod
        def forward(ctx, x):
            return x.clamp(-61439., 61439.).to(torch.float8_e5m2fnuz)
        @staticmethod
        def backward(ctx, grad_output):
            return grad_output
    def __init__(self):
        super(QuantizeFP8, self).__init__()
    def forward(self, x):
        return QuantizeFP8._QuantizeFP8.apply(x)