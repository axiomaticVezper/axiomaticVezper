import os
from PIL import Image, ImageFilter, ImageOps
import numpy as np

def generate_banner(is_dark=True):
    # Palette definition
    if is_dark:
        bg_color = "#0A101F"
        terminal_bg = "#060B14"
        border_color = "#1E293B"
        title_color = "#94A3B8"
        chrome_color = "#22D3EE"
        portrait_color = "#A78BFA"
        accent_color = "#10B981"
        text_label_color = "#64748B"
        text_val_color = "#F8FAFC"
        dots_leader_color = "#1E293B"
        pill_bg = "#1E1B4B"
        pill_text = "#A78BFA"
        status_bg = "#064E3B"
    else:
        bg_color = "#F8FAFC"
        terminal_bg = "#FFFFFF"
        border_color = "#E2E8F0"
        title_color = "#475569"
        chrome_color = "#0891B2"
        portrait_color = "#7C3AED"
        accent_color = "#059669"
        text_label_color = "#64748B"
        text_val_color = "#0F172A"
        dots_leader_color = "#CBD5E1"
        pill_bg = "#EDE9FE"
        pill_text = "#6D28D9"
        status_bg = "#D1FAE5"

    # 1. Process portrait from profile.png
    img_path = "profile.png"
    portrait_svg_paths = ""
    
    if os.path.exists(img_path):
        img = Image.open(img_path)
        # Convert to grayscale
        gray = img.convert("L")
        
        # Target grid: 250 x 285 to keep SVG snappy and under 800KB
        target_w, target_h = 240, 272
        gray_resized = gray.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # Contrast & sharpness adjustment as per Master Prompt
        # Autocontrast + unsharp mask
        gray_adjusted = ImageOps.autocontrast(gray_resized, cutoff=1)
        gray_adjusted = gray_adjusted.filter(ImageFilter.UnsharpMask(radius=2, percent=130))
        
        # Mask out background (pixels close to dark navy)
        rgb_arr = np.array(img.resize((target_w, target_h), Image.Resampling.LANCZOS))
        is_bg = (rgb_arr[:, :, 0] < 22) & (rgb_arr[:, :, 1] < 32) & (rgb_arr[:, :, 2] < 45)
        
        # Floyd-Steinberg dither (1-bit)
        dithered = gray_adjusted.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
        dither_arr = np.array(dithered) # True = bright, False = dark
        
        if is_dark:
            # In dark mode: lit subject = dots (bright pixels, excluding background)
            target_dots = dither_arr & (~is_bg)
        else:
            # In light mode: subject rendered with deep purple dots against clean background
            # Within the subject mask, darker tones or key facial contours are drawn
            target_dots = dither_arr & (~is_bg)
        
        # Map to SVG coordinates within portrait frame:
        # Frame is at x=45, y=70, w=380, h=490
        # Portrait inner box: x=55, y=100, w=360, h=440
        x_offset = 55
        y_offset = 100
        step_x = 360.0 / target_w
        step_y = 440.0 / target_h
        
        path_cmds = []
        for r in range(target_h):
            for c in range(target_w):
                if target_dots[r, c]:
                    # Draw a crisp square dot
                    x = x_offset + c * step_x
                    y = y_offset + r * step_y
                    path_cmds.append(f"M{x:.1f},{y:.1f}h1.2v1.2h-1.2Z")
        
        dot_path_str = "".join(path_cmds)
        portrait_svg_paths = f'<path d="{dot_path_str}" fill="{portrait_color}" shape-rendering="crispEdges"/>'

    # Dotted leaders & metadata rows
    rows = [
        ("Subject", "Sahil Singh"),
        ("Role", "Generative AI Engineer"),
        ("Origin", "Chennai, Tamil Nadu, IN"),
        ("Education", "B.Tech CSE (VIT) · B.S. Data Science (IITM)"),
        ("Status", "Building + Learning + Shipping"),
        ("ToolChain", "PyTorch · LangChain · Docker · Git · Linux"),
        ("Core.Lang", "Python · Java · TypeScript · C++ · SQL · R"),
        ("Core.AI", "LLMs · RAG · Agents · Fine-Tuning · LLMOps"),
        ("Core.Backend", "FastAPI · REST APIs · Node.js"),
        ("Core.Database", "Qdrant · PostgreSQL · FAISS · ChromaDB"),
        ("Core.Infra", "Docker · GitHub Actions · AWS · GCP"),
        ("Grid.Focus", "Quantum ML · Neural Networks · Evaluation"),
        ("Grid.Mail", "singhsahil2910@gmail.com"),
        ("Grid.LinkedIn", "in/sahil-singh-4554a3339"),
        ("Grid.GitHub", "@axiomaticVezper"),
    ]

    # Generate rows SVG
    row_start_y = 115
    row_height = 29
    rows_svg = []
    
    # Leader dots line calculation
    for i, (label, val) in enumerate(rows):
        y = row_start_y + i * row_height
        label_x = 485
        # compute approx length to generate clean dotted leader
        dots_start_x = label_x + len(label) * 8.5 + 14
        dots_end_x = 1130 - len(val) * 8.2 - 14
        
        # Leader line with svg dasharray
        leader_svg = f'<line x1="{dots_start_x:.0f}" y1="{y-4}" x2="{dots_end_x:.0f}" y2="{y-4}" stroke="{dots_leader_color}" stroke-width="1.5" stroke-dasharray="2,6"/>'
        
        label_svg = f'<text x="{label_x}" y="{y}" fill="{text_label_color}" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="13" font-weight="600">{label}</text>'
        val_svg = f'<text x="1135" y="{y}" text-anchor="end" fill="{text_val_color}" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="13">{val}</text>'
        rows_svg.append(f"{label_svg}\n    {leader_svg}\n    {val_svg}")
        
    all_rows = "\n    ".join(rows_svg)

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="1180" height="610">
  <defs>
    <linearGradient id="chromeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{chrome_color}" />
      <stop offset="100%" stop-color="{portrait_color}" />
    </linearGradient>
    <radialGradient id="particleGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{chrome_color}" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="{chrome_color}" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- Outer Canvas -->
  <rect width="1180" height="610" rx="14" fill="{bg_color}" />

  <!-- Terminal Window Container -->
  <rect x="15" y="15" width="1150" height="580" rx="10" fill="{terminal_bg}" stroke="{border_color}" stroke-width="1.5" />

  <!-- Window Header Bar -->
  <line x1="15" y1="52" x2="1165" y2="52" stroke="{border_color}" stroke-width="1.5" />
  
  <!-- Window Controls -->
  <circle cx="38" cy="33" r="5" fill="#EF4444" />
  <circle cx="56" cy="33" r="5" fill="#F59E0B" />
  <circle cx="74" cy="33" r="5" fill="#10B981" />

  <!-- Terminal Title -->
  <text x="100" y="38" fill="{title_color}" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="13" font-weight="500">profile.sh --live</text>

  <!-- LIVE Pulse Badge -->
  <g transform="translate(940, 24)">
    <rect width="70" height="20" rx="10" fill="{status_bg}" />
    <circle cx="12" cy="10" r="4" fill="#EF4444">
      <animate attributeName="opacity" values="1;0.2;1" dur="1.4s" repeatCount="indefinite" />
    </circle>
    <text x="24" y="14" fill="{accent_color}" font-family="ui-monospace, monospace" font-size="11" font-weight="700">LIVE</text>
  </g>

  <!-- Handle Pill -->
  <g transform="translate(1022, 24)">
    <rect width="130" height="20" rx="10" fill="{pill_bg}" />
    <text x="65" y="14" text-anchor="middle" fill="{pill_text}" font-family="ui-monospace, monospace" font-size="11" font-weight="600">@axiomaticVezper</text>
  </g>

  <!-- LEFT PANEL: VISUAL.MAP (Portrait Frame) -->
  <rect x="42" y="68" width="395" height="505" rx="8" fill="none" stroke="{border_color}" stroke-width="1.2" stroke-dasharray="4,4" />
  
  <!-- Panel Corner Accents -->
  <path d="M42,82 V68 H56" stroke="{chrome_color}" stroke-width="2" fill="none" />
  <path d="M423,82 V68 H409" stroke="{chrome_color}" stroke-width="2" fill="none" />
  <path d="M42,559 V573 H56" stroke="{chrome_color}" stroke-width="2" fill="none" />
  <path d="M423,559 V573 H409" stroke="{chrome_color}" stroke-width="2" fill="none" />

  <!-- Left Header -->
  <text x="56" y="88" fill="{chrome_color}" font-family="ui-monospace, monospace" font-size="12" font-weight="700" letter-spacing="1.5">VISUAL.MAP</text>
  <text x="375" y="88" fill="{title_color}" font-family="ui-monospace, monospace" font-size="11">DITHER_v2</text>

  <!-- Dithered Portrait Dots -->
  <g id="portrait-layer">
    {portrait_svg_paths}
  </g>

  <!-- Quantum / Neural Symbol Overlay Glow in bottom-left corner of frame -->
  <g transform="translate(70, 520)" opacity="0.85">
    <circle cx="15" cy="15" r="14" fill="none" stroke="{chrome_color}" stroke-width="1" stroke-dasharray="3,3">
      <animateTransform attributeName="transform" type="rotate" from="0 15 15" to="360 15 15" dur="12s" repeatCount="indefinite"/>
    </circle>
    <ellipse cx="15" cy="15" rx="14" ry="5" fill="none" stroke="{portrait_color}" stroke-width="1">
      <animateTransform attributeName="transform" type="rotate" from="45 15 15" to="405 15 15" dur="8s" repeatCount="indefinite"/>
    </ellipse>
    <circle cx="15" cy="15" r="2.5" fill="{accent_color}"/>
    <text x="38" y="19" fill="{title_color}" font-family="ui-monospace, monospace" font-size="10" letter-spacing="1">QUANTUM-NEURAL KERNEL</text>
  </g>

  <!-- RIGHT PANEL: SYSTEM.INFO -->
  <!-- Right Header -->
  <text x="485" y="88" fill="{chrome_color}" font-family="ui-monospace, monospace" font-size="13" font-weight="700" letter-spacing="1.5">SYSTEM.INFO</text>
  <line x1="485" y1="96" x2="1135" y2="96" stroke="{border_color}" stroke-width="1" />

  <!-- System Info Dotted Leader Rows -->
  <g id="info-rows">
    {all_rows}
  </g>

  <!-- Bottom Accent / Terminal Status Line -->
  <line x1="485" y1="565" x2="1135" y2="565" stroke="{border_color}" stroke-width="1" />
  <circle cx="492" cy="578" r="3" fill="{accent_color}" />
  <text x="502" y="582" fill="{title_color}" font-family="ui-monospace, monospace" font-size="11">KERNEL: ONLINE · LATENCY: 12ms · INTEGRITY: 100% · SECURE</text>
</svg>
"""
    return svg_content

if __name__ == "__main__":
    print("Generating dark.svg...")
    dark_svg = generate_banner(is_dark=True)
    with open("dark.svg", "w", encoding="utf-8") as f:
        f.write(dark_svg)
    print(f"dark.svg written ({len(dark_svg)/1024:.1f} KB)")

    print("Generating light.svg...")
    light_svg = generate_banner(is_dark=False)
    with open("light.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)
    print(f"light.svg written ({len(light_svg)/1024:.1f} KB)")
    print("Done!")
