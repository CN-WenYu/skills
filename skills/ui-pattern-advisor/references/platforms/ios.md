# iOS Mapping

Prefer semantic UIKit or SwiftUI controls and established container behavior before custom drawing. Match the existing project technology rather than translating names mechanically between frameworks.

- Tabs may map to a tab bar, segmented control, picker style, or custom in-content navigation depending on hierarchy; visual similarity does not establish semantics.
- Menus present actions, while pickers and selection controls represent a chosen value.
- Shared-element effects usually require coordinated source and destination geometry; API availability and interruption behavior vary by OS version and framework.
- Respect Reduce Motion, VoiceOver order and announcements, Dynamic Type, pointer/keyboard input where supported, and interactive transition cancellation.
- Validate gesture arbitration with system navigation, scrolling, and sheet dismissal on a real device or simulator.
