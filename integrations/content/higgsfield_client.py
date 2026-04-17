"""
Higgsfield video generation is handled via Playwright MCP (browser automation).
The Higgsfield REST API does not expose video models — only image generation.

Flow:
  Playwright opens higgsfield.ai → uploads product image → generates Seedance video
  → grabs the CDN video URL → passes to simplified_client.create_post()

See: .claude/skills/generate-product-video.md
"""
