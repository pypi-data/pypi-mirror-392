from setuptools import setup, find_packages

setup(
    name="metaflowx",
    version="0.1.5",
    packages=find_packages(),  # Automatically discovers everything under 'metaflowx'
    install_requires=[
        "numpy",
        "scipy",
        "pandas",
        "autograd",
        "statsmodels",
        "pmdarima",
        "jinja2",
        "tqdm",
    ],
    author="ml_lab",
    description="Numerical optimization toolkit — BFGS, CG, Newton, Steepest Descent, and more.",
    python_requires=">=3.7",
)