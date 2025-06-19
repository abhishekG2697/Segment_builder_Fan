# Segment_builder
Adobe analytics style Segment Builder using streamlit

## Nested Containers

Containers can include a list of child containers using the `children` key. This allows complex rules to be grouped hierarchically.

Example definition:

```json
{
  "name": "Recent Buyers",
  "container_type": "visit",
  "logic": "and",
  "containers": [
    {
      "type": "visit",
      "include": true,
      "conditions": [{"field": "event_type", "operator": "equals", "value": "purchase"}],
      "children": [
        {
          "type": "hit",
          "include": true,
          "conditions": [{"field": "page_url", "operator": "contains", "value": "/thank"}]
        }
      ]
    }
  ]
}
```
