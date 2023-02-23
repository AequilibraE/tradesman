from tqdm import tqdm


class TqdmUpTo(tqdm):
    """
    Provides `update_to(n)` which uses `tqdm.update(delta_n)`.

    This class was provided by TQDM documentation: <https://github.com/tqdm/tqdm#hooks-and-callbacks>
    """

    def update_to(self, b=1, bsize=1, tsize=None):
        """
        Creates a progress bar which indicates the size and remaining time to download a file.

        Parameters:
             *b*(:obj:`int`): Number of blocks transferred so far [default: 1].
             *bsize*(:obj:`int`): Size of each block (in tqdm units) [default: 1].
             *tsize*(:obj:`int`): Total size (in tqdm units). If [default: None] remains unchanged.
        """
        if tsize is not None:
            self.total = tsize
        return self.update(b * bsize - self.n)  # also sets self.n = b * bsize
