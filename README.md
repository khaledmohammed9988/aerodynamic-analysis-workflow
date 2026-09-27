# Aerodynamic Analysis Workflow

A reproducible, dependency-free Python workflow for early-stage fixed-wing analysis. It converts operating conditions and exported airfoil polar data into reviewable engineering checks: Reynolds and Mach numbers, dynamic pressure, lift requirements, polar interpolation, and mesh-convergence estimates.

The project is deliberately transparent. It does not replace XFOIL, XFLR5, Flow5, or CFD. It validates and summarizes their outputs so assumptions, units, convergence, and design comparisons remain traceable.

## Engineering workflow

1. Define atmosphere, speed, chord, mass, and wing area.
2. Calculate Reynolds number, Mach number, dynamic pressure, and required lift coefficient.
3. Load a polar exported from an aerodynamic solver.
4. Interpolate aerodynamic coefficients at the operating point.
5. Estimate lift, drag, and aerodynamic efficiency.
6. Check mesh convergence using the Grid Convergence Index.
7. Emit a machine-readable JSON report for design reviews and CI.

## Quick start

```bash
python -m aero_workflow.cli examples/case.json
python -m unittest discover -s tests -v
```

## What this demonstrates

- scientific programming with explicit SI units;
- numerical interpolation and validation;
- physical constraints and actionable error messages;
- reproducible terminal workflows;
- automated engineering checks suitable for AI-agent evaluation.

The included polar is a small synthetic demonstration dataset. Replace it with an export from XFOIL, XFLR5, Flow5, or another solver for project use.

## License

MIT
