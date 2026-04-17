# /generate-product-video

## Description
Full pipeline: Shopify product → detailed 15-second Ad/UGC scenario → Higgsfield Seedance video (via browser) → post to social via Simplified.

## Full Pipeline Steps

### PHASE 1 — Get Product & Scenarios
1. Call `get_viral_products` to show the user available products with image URLs
2. Ask the user which product they want to make a video for
3. Call `generate_video_scenarios` with that product_id
4. Present ALL 3 scenarios in full detail — each includes:
   - **Ad type** (Paid Ad / UGC Ad / Cinematic)
   - **Full 15-second script** (shot-by-shot: [0-3s], [3-7s], [7-11s], [11-15s])
   - **Seedance prompt** (5+ sentence director's brief)
   - **Audio type** — voiceover (UGC) or music (cinematic/paid)
   - **Voiceover script** if audio_type is voiceover
   - **Music direction** if audio_type is music
   - **Hook** (first 3s scroll-stopper)
   - **CTA** (end card text)
   - **Recommended image URL** (show as plain text)
   - Caption + hashtags
5. Ask the user: "Which scenario? (1, 2, or 3)" and "Which image?"

### PHASE 2 — Generate Video on Higgsfield (Playwright)
Once the user picks a scenario:

1. **Open Higgsfield**:
   - `browser_navigate` to https://higgsfield.ai
   - Take a screenshot to check login state
   - If not logged in: navigate to https://higgsfield.ai/login → tell user to log in

2. **Go to video generation**:
   - Navigate to https://higgsfield.ai/create/video
   - Take a screenshot to confirm the UI
   - Select **Seedance 2.0** from the model dropdown

3. **Set up Image-to-Video**:
   - Switch to Image-to-Video mode
   - **Download the image first**: use `browser_navigate` to open the image URL directly in the browser, then use `browser_save_as` or right-click → Save Image As to save it locally to the Desktop or Downloads folder
   - Then click the Higgsfield upload zone and select the locally saved image file
   - **Set duration: 15 seconds** (always — never use 5s)
   - Set aspect ratio: 9:16 (vertical for social)

4. **Enter the Seedance prompt**:
   - Paste the exact `seedance_prompt` from the chosen scenario

5. **Generate**:
   - Click the Generate button
   - Take screenshots every 30 seconds to monitor progress
   - Wait until fully rendered (progress bar complete / preview visible)

6. **Grab the video URL**:
   - Right-click the video → Copy video address
   - OR inspect the download button to extract the CDN URL (e.g. `cloudfront.net/...`)
   - **This URL is the bridge to Phase 3**

### PHASE 3 — Post to Social via Simplified
With the video CDN URL from Phase 2:

1. Call `get_social_accounts` to list connected platforms
2. Show the user the accounts and ask which to post to
3. Use the caption + hashtags from the chosen scenario
4. Call `post_to_social` with:
   - `account_id`: the selected account
   - `caption`: scenario caption + hashtags
   - `media_urls`: [the Higgsfield CDN video URL]
   - `action`: "add_to_queue" (or "schedule" if user gives a time)
   - `pinterest_link`: the product store URL
5. Confirm: "Video posted to [platform] ✅"

## Parameters
- `product_id` (optional): skip product selection if already known
- `scenario_number` (optional): skip scenario selection if already chosen
- `image_url` (optional): override the image used
- `account_id` (optional): skip account selection

## Key Notes
- **Always use 15 seconds** — never 5s or 10s
- **UGC Ads always have voiceover** — a real person talking on camera, use the voiceover_script
- **Cinematic/Paid Ads use music** — describe mood to user so they can add it in post
- Higgsfield session persists after first manual login — fully automatic after that
- The CDN video URL from Higgsfield is public and passes directly to Simplified
- Always show image URLs as plain text so user can verify the right image is used
- If Higgsfield UI changes, take a screenshot and adapt to what's visible
