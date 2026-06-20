# Story Structuring Prompt

I'll provide a rough story about something I did at work. Write it up in the following YAML format:

```yaml
- company: ""
  feature: ""
  scenario: ""
  questions: ""
  skills: ""
  situation: |

  action: |

  result: |
```

## Instructions

- **Company:** Name of the company.
- **Feature:** Name of the feature, project, or initiative.
- **Scenario:** One-line summary of what was owned end-to-end.
- **Questions:** List of behavioral questions this story can answer (refer to `behavioral_questions.md` for verbatim phrasing). One story can map to one or multiple questions.
- **Skills:** Comma-separated list that maps directly to what the actions demonstrate.
- **Situation:** Set up the context, the problem or opportunity, and why it mattered in 2-3 sentences.
- **Action:** Chronological bullets covering the full arc from discovery to execution. Start each bullet with an action verb — no "I" at the start. Each bullet should show clear ownership and decision-making.
- **Result:** Specific, quantifiable outcomes and any lasting or systemic impact. Every result should trace back to an action.
