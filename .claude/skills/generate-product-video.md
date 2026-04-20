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

### PHASE 2 — Generate Video on Higgsfield (Playwright) — FAST MODE
Once the user picks a scenario, execute these steps as fast as possible — minimal screenshots, no waiting unless necessary:

1. **Download the image first** (do this before opening Higgsfield):
   - `browser_navigate` to the image URL directly
   - Right-click the image → Save Image As → save to Desktop as `product.jpg`
   - This avoids upload failures later

2. **Open Higgsfield in same tab**:
   - `browser_navigate` to https://higgsfield.ai/create/video
   - Do NOT take screenshots unless something looks wrong
   - If redirected to login page: tell user to log in, then navigate back to https://higgsfield.ai/create/video

3. **Configure in one pass** (no screenshots between steps):
   - Select **Seedance 2.0** from model dropdown
   - Switch to **Image-to-Video** mode
   - Click upload zone → select the `product.jpg` saved on Desktop
   - Set duration to **15 seconds**
   - Set aspect ratio to **9:16**
   - Paste the `seedance_prompt` into the prompt field

4. **Generate**:
   - Click Generate button
   - Take ONE screenshot to confirm generation started
   - Wait silently — only check every 60 seconds (not 30)
   - Take screenshot only when progress bar looks complete

5. **Grab the video URL**:
   - Right-click the completed video → Copy video address
   - OR click the download button and extract the CDN URL from the network request
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
- **UGC Ads always have voiceover** — a real person talking on camera
- **Minimize screenshots** — only take when confirming generation started and when done
- **Check every 60 seconds** not 30 — video generation takes 2-4 minutes
- Higgsfield session persists after first manual login — fully automatic after that
- Always show image URLs as plain text so user can verify the right image is used
