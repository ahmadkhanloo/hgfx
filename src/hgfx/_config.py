def enable_x64() -> None:
    """Enable JAX 64-bit mode for scientific validation."""
    import jax
    jax.config.update("jax_enable_x64", True)
