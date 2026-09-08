# UI Pattern Catalog

Use this generated index to find canonical cards by name, Chinese name, type, status, platform, or path. Read [schema.md](schema.md) before adding or moving knowledge.

Do not edit the tables manually. Run `python3 ../ui-knowledge-curator/scripts/rebuild_catalog.py` from this skill's directory or use the curator workflow.

## Components

| Pattern | Chinese | Aliases | Tags | Kind | Term status | Platforms | Path |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [Animated Text Disclosure](components/disclosure/animated-text-disclosure.md) | 动画文本展开 | animated-read-more, expandable-text, 展开全文 | disclosure, text, expand, collapse | `component` | `descriptive` | ios, android, web | `components/disclosure/animated-text-disclosure.md` |
| [Autocomplete](components/selection/autocomplete.md) | 自动补全 | typeahead, suggestions, 输入建议 | input, suggestions, search, completion | `component` | `standard` | ios, android, web | `components/selection/autocomplete.md` |
| [Combobox](components/selection/combobox.md) | 组合框 | editable-select, input-with-listbox, 输入选择框 | selection, input, popup, listbox | `component` | `standard` | ios, android, web | `components/selection/combobox.md` |
| [Determinate Progress](components/feedback/loading/determinate-progress.md) | 确定型进度 | measured-progress, progress-bar, 可量化进度 | loading, progress, measurable, feedback | `feedback-pattern` | `standard` | ios, android, web | `components/feedback/loading/determinate-progress.md` |
| [Expanding Tag Selection](components/selection/expanding-tag-selection.md) | 标签展开选择 | expanding-chip-selection, selectable-tag-expansion, 标签选择展开 | selection, tag, chip, expansion | `component` | `descriptive` | ios, android, web | `components/selection/expanding-tag-selection.md` |
| [Indeterminate Progress](components/feedback/loading/indeterminate-progress.md) | 不确定型进度 | indeterminate-bar, ongoing-progress, 未知进度 | loading, progress, indeterminate, feedback | `feedback-pattern` | `standard` | ios, android, web | `components/feedback/loading/indeterminate-progress.md` |
| [Liquid Tab Indicator](components/navigation/liquid-tab-indicator.md) | 液态标签指示器 | fluid-tab-indicator, morphing-tab-indicator, 液态Tab | navigation, tabs, indicator, morphing | `component` | `common-informal` | ios, android, web | `components/navigation/liquid-tab-indicator.md` |
| [Menu](components/selection/menu.md) | 菜单 | action-menu, command-menu, 操作菜单 | commands, actions, overlay | `component` | `standard` | ios, android, web | `components/selection/menu.md` |
| [Pull to Refresh](components/feedback/loading/pull-to-refresh.md) | 下拉刷新 | swipe-to-refresh, 下拉更新 | loading, gesture, refresh, scroll | `interaction-pattern` | `standard` | ios, android, web | `components/feedback/loading/pull-to-refresh.md` |
| [Ripple Feedback for Related Switches](components/selection/ripple-feedback-for-related-switches.md) | 关联开关涟漪反馈 | related-toggle-ripple, 关联切换反馈 | selection, switch, dependency, ripple | `feedback-pattern` | `descriptive` | ios, android, web | `components/selection/ripple-feedback-for-related-switches.md` |
| [Select](components/selection/select.md) | 选择器 | select-control, single-choice-picker, 单选选择器 | selection, form, bounded-options | `component` | `standard` | ios, android, web | `components/selection/select.md` |
| [Skeleton Screen](components/feedback/loading/skeleton-screen.md) | 骨架屏 | content-placeholder, skeleton-loader, 内容占位骨架 | loading, placeholder, content, layout | `feedback-pattern` | `standard` | ios, android, web | `components/feedback/loading/skeleton-screen.md` |
| [Spinner](components/feedback/loading/spinner.md) | 加载旋转指示器 | activity-indicator, loading-spinner, 加载菊花 | loading, indeterminate, loop, feedback | `feedback-pattern` | `standard` | ios, android, web | `components/feedback/loading/spinner.md` |
| [Spring Stepper Progress](components/feedback/spring-stepper-progress.md) | 弹簧步骤进度 | animated-step-progress, 弹性步骤条 | feedback, stepper, progress, spring | `feedback-pattern` | `descriptive` | ios, android, web | `components/feedback/spring-stepper-progress.md` |

## Interactions

| Pattern | Chinese | Aliases | Tags | Kind | Term status | Platforms | Path |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [Curved Card Deletion](interactions/destructive-actions/curved-card-deletion.md) | 曲线卡片删除 | curved-swipe-delete, arcing-card-dismissal, 曲线滑动删除 | destructive, card, swipe, dismissal | `interaction-pattern` | `descriptive` | ios, android, web | `interactions/destructive-actions/curved-card-deletion.md` |
| [Drag-to-Reorder](interactions/direct-manipulation/drag-to-reorder.md) | 拖拽排序 | reorderable-list, sortable-list, 拖动重排 | gesture, reorder, list, direct-manipulation | `interaction-pattern` | `standard` | ios, android, web | `interactions/direct-manipulation/drag-to-reorder.md` |
| [Gesture-driven Transition](interactions/navigation/gesture-driven-transition.md) | 手势驱动转场 | interactive-transition, gesture-controlled-navigation, 交互式转场 | gesture, navigation, transition, interactive | `interaction-pattern` | `standard` | ios, android, web | `interactions/navigation/gesture-driven-transition.md` |
| [Stacked Card Scroll](interactions/navigation/stacked-card-scroll.md) | 堆叠卡片滚动 | card-stack-scroll, stacking-cards, 卡片堆叠滚动 | scroll, cards, stacking, navigation | `interaction-pattern` | `common-informal` | ios, android, web | `interactions/navigation/stacked-card-scroll.md` |
| [Staggered Bulk Selection](interactions/selection/staggered-bulk-selection.md) | 错峰批量勾选 | staggered-select-all, animated-bulk-selection, 批量选择级联反馈 | selection, bulk-action, stagger, feedback | `interaction-pattern` | `descriptive` | ios, android, web | `interactions/selection/staggered-bulk-selection.md` |
| [Velocity-based Slider Snap](interactions/direct-manipulation/velocity-based-slider-snap.md) | 速度感知滑杆吸附 | velocity-aware-slider-snap, momentum-slider-snap, 速度吸附滑杆 | slider, velocity, snap, gesture | `interaction-pattern` | `descriptive` | ios, android, web | `interactions/direct-manipulation/velocity-based-slider-snap.md` |

## Motion

| Pattern | Chinese | Aliases | Tags | Kind | Term status | Platforms | Path |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [Center-focus Scaling](motion/attention/center-focus-scaling.md) | 中心聚焦缩放 | center-emphasis-scaling, 中心项放大 | attention, carousel, focus, scale | `motion-pattern` | `descriptive` | ios, android, web | `motion/attention/center-focus-scaling.md` |
| [Collision and Spring Response](motion/physics/collision-and-spring-response.md) | 碰撞与弹簧回弹 | spring-collision-response, 碰撞回弹 | physics, collision, spring, drag | `motion-pattern` | `descriptive` | ios, android, web | `motion/physics/collision-and-spring-response.md` |
| [Layered Parallax](motion/depth/layered-parallax.md) | 分层视差 | 3d-parallax, 多层视差 | depth, parallax, scroll, pointer | `motion-pattern` | `standard` | ios, android, web | `motion/depth/layered-parallax.md` |
| [Magnetic Attraction](motion/attention/magnetic-attraction.md) | 磁吸效果 | magnetic-hover, magnetic-button, 磁性吸附 | attention, pointer, proximity, transform | `motion-pattern` | `common-informal` | ios, android, web | `motion/attention/magnetic-attraction.md` |
| [Radial Theme Transition](motion/transitions/radial-theme-transition.md) | 圆形主题切换 | circular-theme-reveal, radial-reveal, 圆形揭示切换 | transition, theme, reveal, origin | `motion-pattern` | `descriptive` | ios, android, web | `motion/transitions/radial-theme-transition.md` |
| [Shared-element Image Expansion](motion/transitions/shared-element-image-expansion.md) | 共享元素图片展开 | shared-element-transition, hero-image-transition, 图片连续展开 | transition, continuity, image, navigation | `motion-pattern` | `common-informal` | ios, android, web | `motion/transitions/shared-element-image-expansion.md` |
| [Velocity-driven Deformation](motion/physics/velocity-driven-deformation.md) | 速度驱动形变 | velocity-based-deformation, 速度形变 | physics, gesture, velocity, deformation | `motion-pattern` | `descriptive` | ios, android, web | `motion/physics/velocity-driven-deformation.md` |
