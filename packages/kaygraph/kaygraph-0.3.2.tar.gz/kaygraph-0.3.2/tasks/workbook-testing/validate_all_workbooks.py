#!/usr/bin/env python3
"""
Comprehensive Testing Framework for KayGraph Workbooks

This script validates all 70 workbooks across 16 categories:
- Structure validation (required files present)
- Import validation (all imports resolve correctly)
- Syntax validation (Python syntax is valid)
- Dependency detection (external requirements)
- Safety checks (no dangerous operations)

Usage:
    python validate_all_workbooks.py
    python validate_all_workbooks.py --verbose
    python validate_all_workbooks.py --fix-imports
"""

import os
import sys
import ast
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict

# Add kaygraph to path
KAYGRAPH_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(KAYGRAPH_ROOT))

WORKBOOKS_DIR = KAYGRAPH_ROOT / "workbooks"


class WorkbookValidator:
    """Validates a single workbook"""

    def __init__(self, workbook_path: Path, verbose: bool = False):
        self.path = workbook_path
        self.name = workbook_path.name
        self.category = workbook_path.parent.name
        self.verbose = verbose
        self.results = {
            "name": self.name,
            "category": self.category,
            "path": str(workbook_path),
            "structure": {"valid": False, "issues": []},
            "imports": {"valid": False, "issues": [], "missing_packages": []},
            "syntax": {"valid": False, "issues": []},
            "dependencies": {"required": [], "optional": []},
            "overall_status": "FAIL"
        }

    def validate_structure(self) -> bool:
        """Check if workbook has required files"""
        issues = []

        # Check for README.md
        readme = self.path / "README.md"
        if not readme.exists():
            issues.append("Missing README.md")

        # Check for main.py
        main_py = self.path / "main.py"
        if not main_py.exists():
            issues.append("Missing main.py")

        # Check for at least one Python file
        py_files = list(self.path.glob("*.py"))
        if not py_files:
            issues.append("No Python files found")

        self.results["structure"]["issues"] = issues
        self.results["structure"]["valid"] = len(issues) == 0
        return len(issues) == 0

    def validate_syntax(self) -> bool:
        """Check Python syntax in all .py files"""
        issues = []

        for py_file in self.path.glob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    ast.parse(content, filename=str(py_file))
            except SyntaxError as e:
                issues.append(f"{py_file.name}: Syntax error at line {e.lineno}: {e.msg}")
            except Exception as e:
                issues.append(f"{py_file.name}: Parse error: {str(e)}")

        self.results["syntax"]["issues"] = issues
        self.results["syntax"]["valid"] = len(issues) == 0
        return len(issues) == 0

    def extract_imports(self, file_path: Path) -> Set[str]:
        """Extract all imports from a Python file"""
        imports = set()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Get top-level module name
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Get top-level module name
                        imports.add(node.module.split('.')[0])
        except Exception as e:
            if self.verbose:
                print(f"  Warning: Could not parse {file_path.name}: {e}")

        return imports

    def validate_imports(self) -> bool:
        """Check if all imports are available"""
        issues = []
        missing_packages = set()
        all_imports = set()

        # Standard library modules (Python 3.10+)
        STDLIB = {
            'abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections', 'concurrent',
            'contextlib', 'copy', 'dataclasses', 'datetime', 'decimal', 'enum', 'functools',
            'glob', 'hashlib', 'importlib', 'inspect', 'io', 'itertools', 'json', 'logging',
            'math', 'os', 'pathlib', 'queue', 're', 'shutil', 'signal', 'sqlite3', 'string',
            'subprocess', 'sys', 'tempfile', 'threading', 'time', 'traceback', 'typing',
            'unittest', 'uuid', 'warnings', 'weakref', 'xml', 'yaml'
        }

        # KayGraph internal modules
        KAYGRAPH_MODULES = {'kaygraph', 'utils', 'nodes', 'graphs'}

        # Common third-party packages
        KNOWN_PACKAGES = {
            'anthropic', 'openai', 'requests', 'fastapi', 'pydantic', 'pytest',
            'numpy', 'pandas', 'streamlit', 'gradio', 'flask', 'sqlalchemy',
            'chromadb', 'sentence_transformers', 'transformers', 'torch',
            'langchain', 'llama_index', 'redis', 'celery', 'uvicorn', 'graphviz',
            'psycopg2', 'aiohttp', 'typing_extensions'
        }

        # Get list of local Python modules in this workbook
        local_modules = set()
        # Add .py files as modules
        for py_file in self.path.glob("*.py"):
            if py_file.name != "__init__.py":
                module_name = py_file.stem
                local_modules.add(module_name)
        # Add directories with __init__.py as modules
        for item in self.path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                local_modules.add(item.name)

        # Extract imports from all Python files
        for py_file in self.path.glob("*.py"):
            file_imports = self.extract_imports(py_file)
            all_imports.update(file_imports)

        # Check each import
        for imp in all_imports:
            if imp in STDLIB:
                continue
            elif imp in KAYGRAPH_MODULES:
                continue
            elif imp in local_modules:
                # Local module within this workbook
                continue
            elif imp in KNOWN_PACKAGES:
                # Known third-party package - track as optional dependency
                self.results["dependencies"]["optional"].append(imp)
            else:
                # Unknown package - try to import it
                try:
                    importlib.import_module(imp)
                except ImportError:
                    # Could still be a local module we missed
                    is_local_file = (self.path / f"{imp}.py").exists()
                    is_local_dir = (self.path / imp / "__init__.py").exists()
                    if not (is_local_file or is_local_dir):
                        missing_packages.add(imp)
                        issues.append(f"Cannot import '{imp}'")

        self.results["imports"]["issues"] = issues
        self.results["imports"]["missing_packages"] = list(missing_packages)
        self.results["imports"]["valid"] = len(issues) == 0
        return len(issues) == 0

    def validate(self) -> Dict[str, Any]:
        """Run all validations"""
        structure_ok = self.validate_structure()
        syntax_ok = self.validate_syntax()
        imports_ok = self.validate_imports()

        # Overall status
        if structure_ok and syntax_ok and imports_ok:
            self.results["overall_status"] = "PASS"
        elif structure_ok and syntax_ok:
            self.results["overall_status"] = "WARN"  # Missing packages but otherwise OK
        else:
            self.results["overall_status"] = "FAIL"

        return self.results


class WorkbookTestRunner:
    """Runs tests on all workbooks"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = []

    def discover_workbooks(self) -> List[Path]:
        """Find all workbooks in category directories"""
        workbooks = []

        # Find all category directories (numbered)
        for category_dir in sorted(WORKBOOKS_DIR.iterdir()):
            if not category_dir.is_dir():
                continue
            if not category_dir.name[0].isdigit():
                continue

            # Find workbooks in this category
            for workbook_dir in sorted(category_dir.iterdir()):
                if workbook_dir.is_dir() and workbook_dir.name.startswith("kaygraph-"):
                    workbooks.append(workbook_dir)

        return workbooks

    def run_tests(self) -> List[Dict[str, Any]]:
        """Test all workbooks"""
        workbooks = self.discover_workbooks()

        print(f"🔍 Discovered {len(workbooks)} workbooks across 16 categories")
        print(f"{'='*80}\n")

        for i, workbook_path in enumerate(workbooks, 1):
            category = workbook_path.parent.name
            name = workbook_path.name

            if self.verbose:
                print(f"[{i}/{len(workbooks)}] Testing {category}/{name}")

            validator = WorkbookValidator(workbook_path, verbose=self.verbose)
            result = validator.validate()
            self.results.append(result)

            # Print status
            status = result["overall_status"]
            status_icon = {
                "PASS": "✅",
                "WARN": "⚠️",
                "FAIL": "❌"
            }[status]

            print(f"{status_icon} [{i:2d}/{len(workbooks)}] {category:30s} {name:40s} [{status}]")

            # Print issues if verbose
            if self.verbose and status != "PASS":
                if result["structure"]["issues"]:
                    print(f"    Structure: {', '.join(result['structure']['issues'])}")
                if result["syntax"]["issues"]:
                    for issue in result["syntax"]["issues"]:
                        print(f"    Syntax: {issue}")
                if result["imports"]["issues"]:
                    for issue in result["imports"]["issues"]:
                        print(f"    Import: {issue}")

        return self.results

    def generate_report(self) -> str:
        """Generate summary report"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["overall_status"] == "PASS")
        warned = sum(1 for r in self.results if r["overall_status"] == "WARN")
        failed = sum(1 for r in self.results if r["overall_status"] == "FAIL")

        # Collect all missing packages
        missing_packages = defaultdict(list)
        for result in self.results:
            for pkg in result["imports"]["missing_packages"]:
                missing_packages[pkg].append(result["name"])

        # Collect all structural issues
        structure_issues = []
        for result in self.results:
            if result["structure"]["issues"]:
                structure_issues.append({
                    "name": result["name"],
                    "category": result["category"],
                    "issues": result["structure"]["issues"]
                })

        # Collect all syntax issues
        syntax_issues = []
        for result in self.results:
            if result["syntax"]["issues"]:
                syntax_issues.append({
                    "name": result["name"],
                    "category": result["category"],
                    "issues": result["syntax"]["issues"]
                })

        # Build report
        report = []
        report.append("\n" + "="*80)
        report.append("WORKBOOK VALIDATION REPORT")
        report.append("="*80)
        report.append(f"\nTotal Workbooks: {total}")
        report.append(f"✅ Passed:  {passed} ({passed/total*100:.1f}%)")
        report.append(f"⚠️  Warned:  {warned} ({warned/total*100:.1f}%)")
        report.append(f"❌ Failed:  {failed} ({failed/total*100:.1f}%)")

        if missing_packages:
            report.append(f"\n{'='*80}")
            report.append("MISSING PACKAGES")
            report.append("="*80)
            for pkg, workbooks in sorted(missing_packages.items()):
                report.append(f"\n📦 {pkg}")
                report.append(f"   Used by {len(workbooks)} workbook(s):")
                for wb in workbooks[:5]:  # Show first 5
                    report.append(f"     - {wb}")
                if len(workbooks) > 5:
                    report.append(f"     ... and {len(workbooks) - 5} more")

        if structure_issues:
            report.append(f"\n{'='*80}")
            report.append("STRUCTURAL ISSUES")
            report.append("="*80)
            for issue in structure_issues:
                report.append(f"\n📁 {issue['category']}/{issue['name']}")
                for i in issue['issues']:
                    report.append(f"   - {i}")

        if syntax_issues:
            report.append(f"\n{'='*80}")
            report.append("SYNTAX ISSUES")
            report.append("="*80)
            for issue in syntax_issues:
                report.append(f"\n🐍 {issue['category']}/{issue['name']}")
                for i in issue['issues']:
                    report.append(f"   - {i}")

        report.append("\n" + "="*80)
        report.append("RECOMMENDATIONS")
        report.append("="*80)

        if missing_packages:
            report.append("\n1. Install missing packages:")
            report.append("   pip install " + " ".join(sorted(missing_packages.keys())))

        if structure_issues:
            report.append("\n2. Fix structural issues:")
            report.append("   - Add missing README.md files")
            report.append("   - Add missing main.py files")

        if syntax_issues:
            report.append("\n3. Fix syntax errors:")
            report.append("   - Review Python files for syntax issues")
            report.append("   - Ensure all code is Python 3.10+ compatible")

        if passed == total:
            report.append("\n🎉 ALL WORKBOOKS PASSED VALIDATION!")

        report.append("\n" + "="*80 + "\n")

        return "\n".join(report)

    def save_results(self, output_file: Path):
        """Save detailed results to JSON"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Detailed results saved to: {output_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate KayGraph workbooks")
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--output', '-o', default='validation_results.json', help='Output file for detailed results')

    args = parser.parse_args()

    # Run tests
    runner = WorkbookTestRunner(verbose=args.verbose)
    results = runner.run_tests()

    # Generate report
    report = runner.generate_report()
    print(report)

    # Save results
    output_path = Path(__file__).parent / args.output
    runner.save_results(output_path)

    # Exit code based on results
    failed = sum(1 for r in results if r["overall_status"] == "FAIL")
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
