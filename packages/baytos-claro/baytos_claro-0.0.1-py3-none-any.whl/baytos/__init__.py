# Namespace package for Baytos SDKs
# This allows multiple Baytos packages to coexist (e.g., baytos.claro, baytos.future_product)
__path__ = __import__("pkgutil").extend_path(__path__, __name__)
