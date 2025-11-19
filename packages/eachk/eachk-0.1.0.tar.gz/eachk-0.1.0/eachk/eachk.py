class EachK:
    """Use to skip all except every k-th time.
    e.g. EachK(5) will skip 4 out of 5 times in the loop.
    each5 = EachK(5)
    if each5:
        # do something
    """

    def __init__(self, k: int, first_true=True):
        """Initialize the EachK object.

        Args:
            k (int): The interval at which to return True.
            first_true (bool, optional): Whether the first call should return True.
             Otherwise, the last one will be used.
        """
        self.k = k
        self.true_if_k = 0 if first_true else self.k - 1
        self.count = 0

    def __bool__(self):
        self.count += 1
        return self.count % self.k == self.true_if_k
