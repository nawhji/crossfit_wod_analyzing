from openai import OpenAI
import json
import glob
import os

# file_path = "data/panda/refined_1/020425_0.txt"
# file_name = os.path.basename(file_path)
# d = file_name.replace('.txt', '')
# source = os.path.basename(os.path.dirname(os.path.dirname(file_path)))

# with open(file_path, "r", encoding="utf-8") as f:
#     wod_text = f.read()

system_prompt = """
You are a strict JSON formatter for CrossFit workout data.
Convert any WOD text into a structured JSON using the schema and rules below. Return ONLY a valid JSON object. No explanation or extra text.

SCHEMA
- source (string): Source name (e.g., "panda", "tam", "calgary")

- type_reps (int): Number of workout blocks (e.g., AMRAP + For Time → 2)
- teamwod (bool): true if teamwod
- rest_between (bool): true if rest exists between blocks

- buy_in / buy_out (object):
  - exist (bool)
  - movement (string or null)
  - count (number or string or null)
  - quantity (string or null): "rep", "m", "cal", etc.
  - weight (number or null): in pounds`

- type_rep_1 (object): Describes the first workout block
  - type (string): "AMRAP", "For Time", "EMOM", etc.
  - round (int or null): number of times the full EMOM cycle repeats or number of rounds; must be null if and only if type is "AMRAP"
  - token (int or null): number of minutes per EMOM cycle (e.g., 1 for EMOM, 2 for E2MOM, 4 for E4MOM)
  - emom_cycle_length (int or null): number of distinct movement slots per EMOM token (e.g., "odd/even" = 2, "min 1/2/3" = 3)
  - onoff (bool or null): true only if work/rest repeats exactly
    - on_duration (string or null): "M:SS"
    - off_duration (string or null): "M:SS"
  - time_cap (int or null): duration in minutes; time limit for "For Time", full duration for "AMRAP", or round × token × emom_cycle_length for "EMOM"
  - rest (bool): true if rest appears inside the block
  - movements (array of objects):
    - movement (string): normalized name (e.g., "row", "box jump")
    - ladder (bool): true if reps are like "15-10-5"
    - count:
        - integer if fixed
        - use integer(start count) if ladder = true and type is "AMRAP"
        - string like "15-10-5" if ladder = true and type is "For Time"
        - -1 only if it's "max reps"
    - quantity (string): unit as written in WOD (e.g., "rep", "cal", "m")
    - weight (number or null): use only the men’s weight; must be rounded to the nearest multiple of 5 with no exception
    - increase (bool): true if reps increase per round
      - increase_every (int or null): how much to increase (e.g., +3 → 3)
      - increase_quantity (string or null): unit of increase (e.g., "rep")
      - increase_unit_count (int or null): how often (e.g., every 1 round → 1)
      - increase_unit_type (string or null): "round", "min", etc.

CONVERSION & LOGIC RULES
1. Ignore WOD titles, labels, or box information if they are not part of the actual workout.
2. Do not assume "AMRAP", "For Time", etc. based only on the first line. Always check for on/off patterns and count actual workout blocks to determine type and type_reps.
3. Ignore any additional explanations or alternate scaling options (e.g., weight suggestions for other levels) that appear later in the text, usually at the bottom.
4. Use only the men’s value if multiple weights/distances are given (e.g., 135/95 → use 135).
5. If box jump height or dumbbell weight is missing, use 24 inches and 50 lbs respectively.
6. Use null for missing or unclear values.
7. If onoff timing changes each round, set onoff = false and rest = true.
8. If movement options are given with slashes (e.g., "Row / Run / Bike"), choose only one.
9. For units like distance or time, follow WOD text as-is, except always use "m" for meters.
10. For formats like "10×10m", multiply and record only the total distance (e.g., 100m).
11. If reps are written as a descending pattern (e.g., "8-7…1"), expand the full ladder sequence explicitly (e.g., "8-7-6-5-4-3-2-1") and set ladder = true.
12. For ladder-style rep schemes:
    - If type is "For Time", use the full sequence string for count (e.g., "1-2-3-4") and set ladder = true
    - If type is "AMRAP" and reps increase progressively (e.g., "1-2-3-4..."), set:
      count = 1, ladder = true, increase = true, increase_every = 1, increase_quantity = "rep", increase_unit_count = 1, increase_unit_type = "round"
13. For EMOM-type blocks:
    - round × token × emom_cycle_length must equal time_cap
    - token = number of minutes per EMOM cycle (e.g., 1 for EMOM, 2 for E2MOM)
    - emom_cycle_length = number of distinct movement slots per token (e.g., "odd/even" = 2, "min1/2/3" = 3)
    - round = how many times the token repeats
14. Case of source == calgary, ignore the contents of pre-workout or post-workout.

STRICT OUTPUT FORMAT
- Return valid JSON only
- Follow field names and types exactly
- Use null for missing values
- Use normalized movement names (no synonyms or variations)
"""

datalist = ["calgary", "crossfit.com", "dfs"]
for source in datalist:
    for file_path in glob.glob(f'data/{source}/refined/*.txt'):
        file_name = os.path.basename(file_path)
        d = file_name.replace('.txt', '')

        with open(file_path, "r", encoding="utf-8") as f:
            wod_text = f.read()

        user_prompt = f"""
        The source for this file is "{source}".
        Convert the following WOD text into JSON:

        {wod_text}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": system_prompt.strip()},
                    {"role": "user", "content": user_prompt.strip()}
                ],
                temperature=0
            )

            json_str = response.choices[0].message.content
            structured = json.loads(json_str)

            output_path = f"output/{source}/{d}.json"
            with open(output_path, "w", encoding="utf-8") as out_f:
                json.dump(structured, out_f, indent=2, ensure_ascii=False)

            print(f"{file_name} ✅ done")

        except Exception as e:
            print(f"{file_name} ❌ failed: {e}")
# response = client.chat.completions.create(
#     model="gpt-4-turbo",
#     messages=[
#         {"role": "system", "content": system_prompt.strip()},
#         {"role": "user", "content": user_prompt.strip()}
#     ],
#     temperature=0
# )

# json_str = response.choices[0].message.content
# structured = json.loads(json_str)

# with open(f"test/{source}_{d}.json", "w", encoding="utf-8") as f:
#     json.dump(structured, f, indent=2, ensure_ascii=False)