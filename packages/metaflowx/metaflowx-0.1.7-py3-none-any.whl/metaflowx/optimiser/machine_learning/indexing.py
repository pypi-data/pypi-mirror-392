import pkgutil
import importlib
import inspect
import pandas as pd
import metaflowx

def indexing():
    """
    Recursively scan the entire metaflowx package hierarchy and return a
    DataFrame listing packages, modules, and functions with their descriptions.
    """

    records = []

    def scan(package, path):
        package_name = package.__name__

        for finder, module_name, is_pkg in pkgutil.iter_modules(path):
            full_mod = f"{package_name}.{module_name}"

            # Identify module or package
            if is_pkg:
                records.append({
                    "Path": full_mod,
                    "Type": "package",
                    "Description": "Python package"
                })
                sub_pkg = importlib.import_module(full_mod)
                scan(sub_pkg, sub_pkg.__path__)
            else:
                records.append({
                    "Path": full_mod,
                    "Type": "module",
                    "Description": "Python module"
                })
                module = importlib.import_module(full_mod)

                # List functions in this module
                for name, obj in inspect.getmembers(module, inspect.isfunction):
                    records.append({
                        "Path": f"{full_mod}.{name}",
                        "Type": "function",
                        "Description": inspect.getdoc(obj).split("\n")[0] if inspect.getdoc(obj) else "No description available"
                    })

                # List classes in this module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if obj.__module__.startswith(full_mod):
                        records.append({
                            "Path": f"{full_mod}.{name}",
                            "Type": "class",
                            "Description": inspect.getdoc(obj).split("\n")[0] if inspect.getdoc(obj) else "No description available"
                        })

    # Start scanning at the top-level metaflowx package
    scan(metaflowx, metaflowx.__path__)
    return pd.DataFrame(records).sort_values(by="Path").reset_index(drop=True)

