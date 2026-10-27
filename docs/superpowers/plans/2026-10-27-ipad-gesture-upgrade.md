# iPad Gesture Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an arm64 iPadOS Blender 5.0 IPA with native navigation gestures and a preserved Blender context menu.

**Architecture:** UIKit recognizers emit existing GHOST input events. The window manager annotates three-finger trackpad events, and navigation operators select pan even when an alternative Blender keymap initially targets rotate. TouchView remains installed through Blender's normal scripts installation, but does not consume iOS right-clicks.

**Tech Stack:** C++/Objective-C++, UIKit, Blender GHOST/window-manager, Python, CMake/Xcode, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-27-ipad-gesture-upgrade-design.md`

## Global Constraints

- Base every change on the supplied IOS5.0.0 source baseline.
- Preserve ordinary direct touch, Apple Pencil, mouse, and keyboard pathways.
- Do not store signing credentials in Git.
- Produce an unsigned artifact only; physical-device behavior requires user testing.

## Review Focus

- A one-finger drag must cancel long-press recognition instead of emitting a context click.
- A two-finger pan must not be retagged as three-finger input.
- Inverted Blender navigation must route a three-finger event to move rather than rotate.
- The installed script path must contain the iOS TouchView `PASSTHROUGH` behavior.
- The workflow must not package a partial or wrong-named IPA.

---

### Task 1: Native touch input routing

**Files:**
- Modify: `intern/ghost/intern/GHOST_WindowIOS.mm`
- Modify: `source/blender/windowmanager/intern/wm_event_system.cc`
- Modify: `source/blender/editors/space_view3d/view3d_navigate_view_move.cc`
- Modify: `source/blender/editors/space_view3d/view3d_navigate_view_rotate.cc`
- Test: `tests/python/test_ipad_gesture_source_contract.py`

**Interfaces:**
- Consumes: UIKit direct-touch recognizers and `GHOST_EventTrackpad`.
- Produces: `WM_EVENT_MULTITOUCH_THREE_FINGERS` events that select `ViewOpsType_move`.

- [ ] Write source-contract tests for a three-finger direct pan recognizer, two-second direct long press, right-button press/release, three-finger modifier tagging, and rotate-to-move fallback.
- [ ] Run the source-contract tests and observe failure before native changes.
- [ ] Apply the supplied native patch; adapt long press to use serialized GHOST events and add the inverted-keymap move fallback.
- [ ] Run the source-contract tests and the supplied patch apply-check.
- [ ] Commit the native input routing changes.

### Task 2: TouchView and packaging verification

**Files:**
- Modify: `scripts/addons_core/touchview/source/ops/touch.py`
- Modify: `.github/workflows/build-blender-ios.yml`
- Test: `tests/python/test_ipad_gesture_source_contract.py`

**Interfaces:**
- Consumes: TouchView's `TOUCHVIEW_OT_right_click_action.invoke` and the staged Xcode `.app` directory.
- Produces: iOS `PASSTHROUGH` for right clicks and a named uploaded IPA artifact.

- [ ] Extend the source-contract test for iOS `PASSTHROUGH` and workflow app-bundle assertion.
- [ ] Run the test and observe failure before the changes.
- [ ] Add the TouchView iOS guard; rename/package/upload the IPA as `Blender-iPad-A16-gestures.ipa`; assert the installed TouchView script is patched before zipping.
- [ ] Run Python compilation and all source-contract tests.
- [ ] Commit the TouchView and workflow changes.

### Task 3: Cloud compilation and artifact validation

**Files:**
- Modify: `docs/TEST_RESULTS.md`

**Interfaces:**
- Consumes: GitHub Actions workflow artifact.
- Produces: a structurally verified `Blender-iPad-A16-gestures.ipa` and an explicit physical-device test matrix.

- [ ] Push the feature branch and dispatch the macOS workflow.
- [ ] Verify completion, successful Xcode build, artifact name, and IPA `Payload/Blender.app` structure.
- [ ] Record compilation evidence and gesture test status as pending physical iPad A16 validation.
- [ ] Commit test documentation if any local documentation change is required.
