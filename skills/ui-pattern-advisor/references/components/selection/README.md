# Selection Controls

Choose by semantics, not by the fact that an overlay appears below a trigger. "Dropdown" is an ambiguous visual description rather than one canonical control.

| User need | Pattern | Key distinction |
| --- | --- | --- |
| Choose one value from a bounded list | [Select](select.md) | The chosen value persists as form or setting state |
| Invoke an action from a compact list | [Menu](menu.md) | Items are commands, not a stored value |
| Choose or enter a value through one field | [Combobox](combobox.md) | Input and popup form one composite control |
| Receive suggestions while typing | [Autocomplete](autocomplete.md) | Suggestions assist text entry and may not constrain the final value |

Use [Expanding Tag Selection](expanding-tag-selection.md) only when selection exposes attached context. [Ripple Feedback for Related Switches](ripple-feedback-for-related-switches.md) explains dependency between nearby switches; it is not a replacement for normal switch feedback.
