# data/raw — weekly measurement drops

One folder per week, e.g. `2026-W28/`, containing that week's raw files:

- DAQ973A desiccant logger: `Trace NN.csv` (Keysight export, do not rename —
  the trace number NN controls voltage-conversion behaviour)
- UVR solar controller: semicolon-separated CSV (German decimals)

Never edit files in here. The pipeline treats this folder as immutable input.
