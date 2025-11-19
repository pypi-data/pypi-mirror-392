import torch
from torch import Tensor


class GaussianMixture:
    """
    Gaussian Mixture Class.

    Parameters (6):
    - n_components (int)
    - dim (int)
    - weights (Tensor) shape (n_components,)
    - means (Tensor) shape (n_components, dim)
    - covariances (Tensor) shape (n_components, dim, dim)
    - device (torch.device or str)
    """

    def __init__(  # noqa: PLR0913
        self,
        n_components: int = 1,
        dim: int = 1,
        weights: Tensor | None = None,
        means: Tensor | None = None,
        covariances: Tensor | None = None,
        device: torch.device | str = "cpu",
    ) -> None:
        self.device = torch.device(device)
        self.n_components = n_components
        self.dim = dim

        if weights is None:
            weights = torch.full((n_components,), 1.0 / n_components, device=self.device)
        if means is None:
            means = torch.zeros((n_components, dim), device=self.device)
        if covariances is None:
            covariances = torch.stack(
                [torch.eye(dim, device=self.device) for _ in range(n_components)]
            )

        self.n_components = self._validate_n_components(n_components)
        self.dim = self._validate_dim(dim)
        self.weights = self._validate_weights(weights)
        self.means = self._validate_means(means)
        self.covariances = self._validate_covariances(covariances)

    def _validate_n_components(self, k: int) -> int:
        if not isinstance(k, int) or k <= 0:
            msg = "n_components must be a positive integer"
            raise ValueError(msg)
        return k

    def _validate_dim(self, d: int) -> int:
        if not isinstance(d, int) or d <= 0:
            msg = "dim must be a positive integer"
            raise ValueError(msg)
        return d

    def _validate_weights(self, w: Tensor) -> Tensor:
        if w.ndim != 1 or w.shape[0] != self.n_components:
            msg = "weights must have shape (n_components,)"
            raise ValueError(msg)
        w = w.to(self.device)
        w_sum = w.sum()
        if not torch.isclose(w_sum, torch.tensor(1.0, device=self.device)):
            msg = "weights must sum to 1.0"
            raise ValueError(msg)
        if torch.any(w < 0):
            msg = "weights must be non-negative"
            raise ValueError(msg)
        if w_sum <= 0:
            msg = "weights must sum to a positive value"
            raise ValueError(msg)
        return (w / w_sum).clone()

    def _validate_means(self, m: Tensor) -> Tensor:
        mean_tensor_order = 2
        if m.ndim != mean_tensor_order or m.shape != (self.n_components, self.dim):
            msg = "means must have shape (n_components, dim)"
            raise ValueError(msg)
        return m.to(self.device).clone()

    def _validate_covariances(self, c: Tensor) -> Tensor:
        covariance_tensor_order = 3
        if c.ndim != covariance_tensor_order or c.shape != (self.n_components, self.dim, self.dim):
            msg = "covariances must have shape (n_components, dim, dim)"
            raise ValueError(msg)
        c = c.to(self.device).clone()
        # Basic positive-definite check (diagonal > 0 if diagonal matrix)
        for i in range(self.n_components):
            matrix = c[i, :, :]
            eigenvalues = torch.linalg.eigvalsh(matrix)
            if torch.any(eigenvalues <= 0):
                msg = "Covariance matrices must be positive definite"
                raise ValueError(msg)
        return c

    def __repr__(self) -> str:
        return (
            f"GaussianMixture(n_components={self.n_components}, "
            f"dim={self.dim} ,"
            f"weights_shape={tuple(self.weights.shape)}, "
            f"means_shape={tuple(self.means.shape)}, "
            f"covariances_shape={tuple(self.covariances.shape)}, device={self.device})"
        )
