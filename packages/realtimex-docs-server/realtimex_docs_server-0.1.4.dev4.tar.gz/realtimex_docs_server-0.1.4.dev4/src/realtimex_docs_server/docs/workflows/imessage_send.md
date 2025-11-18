# Workflow: iMessage Send Message

## Overview
Send a user-provided message to a specified phone number using the Messages app on macOS. The user is already signed into iMessage; do not attempt any login or account actions. All interactions rely on image-based validation.

## Prerequisites
- Messages app installed and configured with a signed-in iMessage account.
- Phone number (international or domestic formatting) provided by the user.
- Message content supplied verbatim by the user.
- Screen layout consistent with standard macOS Messages (no custom themes or window arrangements that hide critical UI elements).

## Reference Images (Use with `wait_for_element`)
| Image Name | Purpose | Timeout |
| --- | --- | --- |
| `imessage/new_message_button.png` | “New Message” button visible. | 10s |
| `imessage/to_field.png` | “To:” recipient field available and focused. | 10s |
| `imessage/message_field.png` | Message composer area visible. | 10s |
| `imessage/sent_confirmation.png` (optional) | “Delivered” indicator beneath the sent bubble. | 10s |
| `imessage/read_confirmation.png` (optional) | “Read” indicator beneath the sent bubble. | 10s |

> If any image fails to match the current UI, pause and request updated assets before proceeding.

## Step-by-Step Procedure
Each interaction MUST follow the sequence `wait_for_element` → `move_mouse` (using the `(x, y)` returned by detection) → `click_mouse` → `type_text` (if applicable) → `wait` (only if explicitly stated).

1. **Launch Messages**
   - Call `open_application("Messages")`.
   - Confirm the app is running with `verify_application("Messages")`. If verification fails, STOP. No additional window validation is needed (conversation lists vary by user).

2. **Start a New Message & Enter Recipient**
   - Validate and click the New Message button: `wait_for_element("imessage/new_message_button.png", timeout=10)` → click using returned coordinates.
   - Validate the “To:” field: `wait_for_element("imessage/to_field.png", timeout=10)` → click using returned coordinates.
   - Type the phone number exactly as provided using `type_text`, then press Enter via `press_key("enter")` to confirm the recipient.

3. **Compose Message**
   - Validate the message composer: `wait_for_element("imessage/message_field.png", timeout=10)`. Use the returned `(x, y)` to focus via `move_mouse` → `click_mouse`.
   - Type the user’s message. If the user gave explicit text, type it verbatim. If the user asked you to draft a message (e.g., “Draft a friendly check-in message…”), write a concise, context-appropriate sentence that fulfills the request.

4. **Send Message**
   - Press Enter via `press_key("enter")` to send the message. DO NOT search for a Send button (it may be hidden in some layouts).
   - Confirmation (if assets are available):
     - `wait_for_element("imessage/sent_confirmation.png", timeout=10)` for “Delivered,” or
     - `wait_for_element("imessage/read_confirmation.png", timeout=10)` for “Read.”
     - If both confirmation attempts fail twice, STOP and report the failure. If no confirmation assets are available, skip this step.

5. **Completion**
   - Report success, including the recipient phone number and a short acknowledgement that the message was sent. Do not echo the full message unless the user explicitly requests it.

## Recovery Guidance
- If any `wait_for_element` call fails twice, STOP and report the missing image (e.g., “`imessage/to_field.png` not detected; workflow terminated.”).
- If `verify_application("Messages")` fails, instruct the user to ensure Messages is installed and accessible, then STOP.
- If typing fails or the wrong content appears (e.g., due to sticky keys), STOP and report the issue instead of retyping blindly.
- If the user provides no phone number or message content, STOP and request clarification.

## Completion Criteria
- The specified message is sent to the requested phone number.
- Final report confirms: Messages app launched, recipient field filled with the correct number, message typed verbatim, send action completed, and (if available) confirmation observed.
- No additional text beyond the requested message was sent.***
