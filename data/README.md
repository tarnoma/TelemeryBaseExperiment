# Data

`code/analysis.py` expects two Excel files in this folder:

| File | Content |
|---|---|
| `telemetry.xlsx` | Sheet `(01)Rule Based 20 คน`: one row per rule-based encounter. Sheet `(02)22คน Adaptive`: one row per adaptive encounter (rows whose `encounter` starts with `รวม` are per-participant summaries and are removed). Row 1 of each sheet holds field descriptions. Other sheets (event log, overtime) are not used by the analysis. |
| `flow_questionnaire.xlsx` | Sheet 1: adaptive responses; sheet 2: rule-based responses. Columns: timestamp, numeric ID, items 1–24 (1–5). |

Participants are identified only by numeric IDs.
