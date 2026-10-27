"""Static contracts for the iPad-only gesture implementation.

These tests do not simulate UIKit. They pin the source-level routing that the
macOS arm64 build and physical iPad test plan must validate further.
"""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class IpadGestureSourceContractTest(unittest.TestCase):
    def test_native_three_finger_pan_and_long_press_are_serialized(self):
        source = (ROOT / "intern/ghost/intern/GHOST_WindowIOS.mm").read_text(
            encoding="utf-8"
        )

        for token in (
            "PAN_GESTURE_THREE_FINGERS",
            "minimumNumberOfTouches = 3",
            "maximumNumberOfTouches = 3",
            "minimumPressDuration = 2.0",
            "numberOfTouchesRequired = 1",
            "RIGHT_BUTTON_DOWN",
            "RIGHT_BUTTON_UP",
            "event_info.add_event(UserInputEvent::EventTypes::RIGHT_BUTTON_DOWN)",
            "event_info.add_event(UserInputEvent::EventTypes::RIGHT_BUTTON_UP)",
        ):
            self.assertTrue(token in source, f"missing native gesture token: {token}")

        self.assertTrue(
            "CGPoint translation = [sender getScaledTranslation:window];" in source,
            "UserInputEvent requires a mutable translation pointer",
        )
        self.assertFalse(
            "const CGPoint translation = [sender getScaledTranslation:window];" in source,
            "three-finger translation must not be const",
        )
        self.assertTrue(
            "CGPoint delta = [sender getRelativeTranslation:translation];" in source,
            "UserInputEvent requires a mutable delta pointer",
        )
        self.assertFalse(
            "const CGPoint delta = [sender getRelativeTranslation:translation];" in source,
            "three-finger delta must not be const",
        )
        self.assertTrue(
            "CGPoint point = [sender locationInView:window->getView()];" in source,
            "scalePointToWindow requires a mutable CGPoint lvalue",
        )
        self.assertTrue(
            "point = window->scalePointToWindow(point);" in source,
            "long press must scale its mutable touch point before dispatch",
        )

    def test_three_finger_navigation_is_tagged_and_pan_safe(self):
        event_source = (
            ROOT / "source/blender/windowmanager/intern/wm_event_system.cc"
        ).read_text(encoding="utf-8")
        move_source = (
            ROOT / "source/blender/editors/space_view3d/view3d_navigate_view_move.cc"
        ).read_text(encoding="utf-8")
        rotate_source = (
            ROOT / "source/blender/editors/space_view3d/view3d_navigate_view_rotate.cc"
        ).read_text(encoding="utf-8")

        self.assertIn("WM_EVENT_MULTITOUCH_THREE_FINGERS", event_source)
        self.assertIn("event.modifier |= KM_SHIFT", event_source)
        self.assertIn("WM_EVENT_MULTITOUCH_THREE_FINGERS", move_source)
        self.assertIn("&ViewOpsType_move", rotate_source)
        self.assertIn("WM_EVENT_MULTITOUCH_THREE_FINGERS", rotate_source)

    def test_touchview_does_not_consume_ios_context_clicks(self):
        source = (
            ROOT / "scripts/addons_core/touchview/source/ops/touch.py"
        ).read_text(encoding="utf-8")

        self.assertTrue(
            'if sys.platform == "ios":' in source,
            "TouchView must detect the native iOS build",
        )
        self.assertTrue(
            "return PASSTHROUGH" in source,
            "TouchView must leave the native context click for Blender",
        )

    def test_workflow_packages_named_ipa_and_checks_touchview(self):
        workflow = (ROOT / ".github/workflows/build-blender-ios.yml").read_text(
            encoding="utf-8"
        )

        self.assertTrue(
            "Blender-iPad-A16-gestures.ipa" in workflow,
            "workflow must produce the requested IPA name",
        )
        self.assertTrue(
            "touchview/source/ops/touch.py" in workflow,
            "workflow must validate the staged TouchView file",
        )


if __name__ == "__main__":
    unittest.main()
