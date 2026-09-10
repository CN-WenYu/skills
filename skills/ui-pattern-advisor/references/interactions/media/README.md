# Image Interaction Selection

Choose an image interaction from the user's task, the relationship between the images, the available input methods, and the product's tolerance for decorative motion. Do not layer effects merely because they can be rendered together.

| User task | Prefer | Key boundary |
| --- | --- | --- |
| Compare aligned versions of the same scene | [Image Comparison Slider](../../components/media/image-comparison-slider.md) | Both images must share meaningful spatial registration. |
| Explore a hidden image or layer through a movable aperture | [Mask Reveal](mask-reveal.md) | Essential information cannot depend on precision dragging alone. |
| Transition between related images with an intentionally stylized replacement | [Pixelated Image Transition](../../motion/transitions/pixelated-image-transition.md) | Preserve a simple fallback and a deterministic final frame. |
| Add localized responsive distortion to imagery | [Ripple Distortion](../../motion/physics/ripple-distortion.md) | Keep text, controls, and identity-critical details readable. |
| Reveal content through a peelable top layer | [Sticker Peel](sticker-peel.md) | The layer relationship and completion threshold must be clear. |
| Leave short-lived image echoes behind pointer movement | [Image Trail](../../motion/attention/image-trail.md) | Use only on roomy pointer-oriented showcases. |
| Add a restrained reflective cue to a card on hover | [Glare Hover](../../motion/attention/glare-hover.md) | The effect must not obscure content or imply unsupported touch behavior. |

If none clarifies comparison, reveal, continuity, feedback, or exploration, keep the image static. Mobile and accessibility alternatives must be selected from the interaction contract rather than mechanically reproducing hover or precision-pointer behavior.
