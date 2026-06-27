<!--
* Use this issue template for managing project risks.

* The text contained within the HTML comment tags will not be displayed in the GitLab UI.
  It provides information on the expected contents of the different sections.

* Sections not relevant or applicable to the current risk
  can be left open, stated as not applicable (N/A) or removed.
-->

## Risk description

Describe the risk.

## Risk consequences

Describe the impact of the risk.

## Risk estimation

| Probability | Severity | Rating |
| :---:       | :---:    | :---:  |
|             |          |        |


- Assign Probability between Low (1), Medium (2), High (3)
- Assign Severity between Low (1), Medium (2), High (3)
- Compute Probability * Severity:
    - If 1 or 2: assign a "Low" rating
    - If 3 or 4: assign a "Medium" rating
    - If 6 or 9: assign a "High" rating

- Add the label corresponding to the Rating: ~Risk::Rating::Low , ~Risk::Rating::Medium , or ~Risk::Rating::High

For example: The risk is estimated to have a Medium probability of occurrence (2) and a Medium severity (2). The overall rating is thus 2 * 2 = 4. Add the ~Risk::Rating::Medium label to the risk.

## Linked mitigation actions

Risks rated High must have related actions. Actions for risks rated Medium or Low are not mandatory but recommended.

<!-- The relate quick action can be used to link directly to the actions:
/relate #
-->

/label ~Risk
