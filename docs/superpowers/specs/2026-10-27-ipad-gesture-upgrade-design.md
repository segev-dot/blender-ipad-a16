# iPad Gesture Upgrade Design

## Intent

Ship a Blender 5.0 iOS build based on the supplied IOS5.0.0 source snapshot. It must add native three-finger viewport pan and a two-second direct-finger context-menu press without changing Blender's modeling, rendering, mouse, keyboard, or Apple Pencil pathways.

## Goals

- One direct-finger stationary hold for two seconds emits a cursor move followed by a right-button press and release.
- Three direct fingers produce an iOS trackpad scroll event marked as three-finger input and route to `ViewOpsType_move` (viewport pan).
- Two fingers retain their existing orbit route and pinch retains its existing magnify route.
- TouchView's iOS right-click operator returns `PASSTHROUGH`, preventing its fullscreen mapping from consuming the native context click.
- The installed application contains the patched TouchView script and is packaged as `Blender-iPad-A16-gestures.ipa`.

## Non-goals

- No replacement of Blender's keymap system, UI, renderer, or model data.
- No assertion that gestures work on physical hardware before iPad A16 testing.
- No Apple signing credentials in the repository.

## Approaches considered

1. Python-only gesture handling: rejected because UIKit recognizer data and native right-button delivery are not available reliably in the add-on layer.
2. Native recognizers plus TouchView passthrough: selected. It preserves Blender's existing input dispatch and makes the smallest platform-specific changes.
3. Redesign TouchView: rejected because it would replace working behavior beyond the requested gesture fixes.

## Design decisions

- Use UIKit recognizers in `GHOST_WindowIOS.mm`, direct touches only for the new gestures, and `cancelsTouchesInView = false` to preserve ordinary selection/Pencil input.
- Route long-press events through `generateUserInputEvents` so cursor/right-button events are serialized with all other iOS input. The right-button pair uses `GHOST_TABLET_DATA_NONE`.
- Keep the supplied Shift modifier route for standard Blender navigation. If an inverted `use_v3d_mmb_pan` configuration dispatches a three-finger event through rotate, `viewrotate_invoke` reroutes it to `ViewOpsType_move`.
- Rely on the existing CMake installation of the `scripts` directory; add a workflow assertion that the patched TouchView script is present in the staged `.app` before packaging.

## Validation

- Apply-check the supplied native patch before editing.
- Run static source contract checks and Python syntax compilation for the TouchView package on Windows.
- Build the arm64 iPhoneOS app with the existing GitHub Actions workflow, verify the artifact contains the expected patched script, then structurally verify the exported IPA.
- Mark every gesture as pending physical iPad A16 testing.
