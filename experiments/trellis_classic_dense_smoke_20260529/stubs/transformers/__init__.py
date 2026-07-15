class _Dummy:
    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        return cls()
    def eval(self): return self
    def to(self, *args, **kwargs): return self
    def __call__(self, *args, **kwargs):
        raise RuntimeError('transformers stub called unexpectedly')
CLIPTextModel = _Dummy
AutoTokenizer = _Dummy
