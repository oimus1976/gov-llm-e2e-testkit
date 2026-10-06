# Private Knowledge DOM observation (Issue #2)

The upload path is disabled until registration DOM has been observed. Offline tests do not imply live login or upload success.

1. Use the existing local environment configuration with `load_env()`: ENV_PROFILE > env.yaml for profile selection; OS secrets > .env > .env.<profile> for values. Confirm the intended endpoint/profile locally. Do not add profiles or commit credentials. The existing Python/Playwright stack and Chromium must be installed.
2. From the checkout run:

   ```powershell
   .\.venv\Scripts\python.exe scripts/knowledge_upload_probe.py data/knowledge_upload/synthetic.md --synthetic --inspect-ui
   ```

   If Chromium was installed into `out/playwright-browsers`, first set the process-local `PLAYWRIGHT_BROWSERS_PATH` to its absolute path. This is a Playwright runtime setting; do not change .env or env.yaml.
3. LoginPage automatically opens the configured URL, fills existing credentials and waits for `/chat`. Stop on configuration/authentication failure and correct it locally under human control; do not share .env contents or raw login errors.
4. The Playwright Inspector pauses after login. Use its resume/pause and locator picker to observe the path to the registration form. Record each control's role, accessible name, URL path and sanitized DOM fragment. ChatSelectPage is not evidence of registration navigation. Do not select files, upload, delete, replace, or send chats.
5. Observe the file input's owning form, attributes, accepted formats, multiplicity, upload trigger and whether file selection automatically submits. Capture only cropped, redacted screenshots and DOM snippets. Never export full authenticated DOM, cookies, storage state, passwords, private document names or HTTP bodies to GitHub/Drive. Keep original evidence locally under ignored `logs/`.
6. Resume/close the Inspector to finish. Exit 2 means upload automation remains pending. No selection receipt is written. Supply sanitized navigation/form evidence for the next implementation step.

After an evidence-based PrivateKnowledgePage exists, select one synthetic sample only after the upload flag and final literal `UPLOAD` prompt. File selection, HTTP acceptance, list registration and searchability are separate observations. Same-name behavior remains unknown; do not update/replace an entry to test it. Issue #2 prohibits real municipality data, Ready/merge/main updates and deletion.
