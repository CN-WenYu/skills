# Backgrounds, Gradients and SVG Support

Read when artwork has a background, gradient, transparency or unsupported vector effects.

## Background Scope and Artwork Roles

1. Source background: preserve or remove pixels/shapes from the supplied artwork.
2. Preview matte: a viewing aid outside the animation.
3. Export background: transparent canvas or a real background layer in the JSON.

A gradient brand backplate can remain part of a logo while everything outside is transparent. Preserve the supplied icon background by default; ask only when its role is genuinely ambiguous or a change is requested. Do not classify all rear shapes as disposable background. A preview color never implies an exported color.

The icon backplate is a separate object within the retained artwork. Do not bundle its retention and full-canvas background into a single yes/no question. Record `artwork.existing_wordmark` (`absent|symbols|preserve`) and `artwork.backplate`; these decisions replace the old boolean confirmation. Pictorial letters may express a concept without being an existing brand wordmark; record `symbols` in that case. Existing brand lettering can be part of the logo. If an additional name is requested while existing lettering is retained, explicitly establish that relationship before adding it twice.

Backplate modes:

- `none`: the source has no icon backplate. All source shapes are the foreground.
- `embedded`: map visible backplate geometry to explicit `element_ids` in a reviewed SVG. IDs may select individual shapes or semantic groups; descendants inherit the selection. All other visible shapes remain foreground. The plate must already paint behind the foreground; otherwise splitting is rejected. If IDs are absent, label the reviewed elements without changing their geometry, then record those IDs. Do not guess by path count, color, or first/last path.
- `generated`: the source is explicitly confirmed as foreground-only; generate a plate over its full normalized SVG viewport from confirmed `paint` and `corners`. Foreground position and scale within that viewport are preserved. Paint uses the solid/linear/radial schema below, in source SVG coordinates. This is not foreground extraction and must not be used to hide an existing source background.

`normalized.svg` contains the complete static icon. For generated plates, reproduce from the original foreground source and saved config; using the combined normalized SVG as foreground would add the plate twice.

## Corners and Clipping

Every retained/generated plate records `corners`: `{"mode":"preserve"}`, `{"mode":"square"}`, or `{"mode":"rounded","radius":20}`. Radius is in normalized source SVG units, not preview CSS pixels. Reuse an explicit user decision or verified project splash radius; otherwise ask preserve/square/rounded together with other visual choices. Existing square pixels do not answer whether the animation should have rounded corners. For requested rounding, propose a concrete radius if the user has not specified one. Generated plates require square or rounded because there are no source corners to preserve.

Corner editing supports one untransformed rectangle selected by its own ID; complex paths, multiple shapes or transformed rectangles need reviewed source geometry. Arbitrary existing plate geometry may be preserved. Generated plates support ordinary rounded rectangles. This does not implement platform-specific continuous corners or a general clipping mask.

Changing a plate's radius is not equivalent to clipping its foreground. The tool rejects foreground motion whose conservative bounds cross a rectangular/rounded plate boundary. Do not silently crop, reposition or shrink the foreground to make it fit. For arbitrary plate contours, only bounding-box containment is automatic; actual contour containment remains a visual review requirement. Names remain outside the plate and must never be included in icon corner clipping.

## Export Background Parameters

Retained icon plates need authored opacity entrance tracks from zero; their geometry can stay fixed while they appear. A first-frame-visible plate needs a `user_request` quote on its track (or the explicit static preset). Preserving a background is not an instruction to make it static.

Visible exported full-canvas backgrounds fade from zero by default over .3 seconds. Optional `motion: {"start":0,"duration":0.4}` changes this timing; `duration:0` with `start:0` and an actual `user_request` keeps it visible from frame zero. These fields belong only to `export_background`, not generated plate paint. Transparent exports have no canvas layer to animate. A fixed host page/preview matte is not an exported background.

Transparent: `{"type":"transparent"}`. Solid: `{"type":"solid","color":"#E23C29"}`.

Linear, in composition coordinates:

```json
{"type":"linear","start":[0,0],"end":[512,512],"stops":[
  {"offset":0,"color":"#163060","opacity":1},
  {"offset":1,"color":"#6f2c91","opacity":1}
]}
```

Radial: `{"type":"radial","center":[256,256],"radius":256,"stops":[...]}` with the same stop schema. At least two sorted stops are required, with offsets/opacity in [0,1]. Use user-confirmed values; raster colors/angles inferred visually are proposals until accepted.

A vector gradient is independent of foreground extraction. For a flattened gradient image, obtain a transparent/vector foreground or agree a separate extraction strategy. V1 does not automatically fit gradients, remove gradient backgrounds, install segmentation models, simplify mesh gradients, or embed the original image as a fallback.

## Supported SVG Subset

Paths including quadratic curves and elliptical arcs, rect/rounded rect, circle, ellipse, line, polyline and polygon; inherited inline fill/stroke styling; affine group transforms; nonzero/evenodd fills; ordinary stroke caps/joins; native linear and circular radial gradients with opacity stops.

The parser preserves painter order and converts geometry to cubic paths. It normalizes the viewBox origin, keeps visible colors and provides conservative bounds. Optimization must not merge semantic groups, remove IDs needed for mapping, or change winding rules.

Explicitly reject unsupported visual semantics, including filters, masks, clipping, images, text not yet outlined, use/symbol references, stylesheets/classes, external resources, SVG animation, repeating gradients, elliptical/off-center radial gradients, nonuniformly transformed strokes and overlapping group compositing. Some gradient transforms are supported when mathematically representable; never approximate the others silently.

Source artwork extending beyond its viewport requires a reviewed viewBox/cropping decision. Unsupported SVGs must be simplified or outlined only after explaining the exact effect to the user. Native-vector quality takes precedence over nominal conversion success.
