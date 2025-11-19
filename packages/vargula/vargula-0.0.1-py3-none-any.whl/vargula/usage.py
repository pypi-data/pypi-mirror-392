"""
Comprehensive usage examples for vargula library with color palette features

This file demonstrates all major features:
- Basic text styling
- Palette generation with color theory
- Accessibility features (WCAG compliance)
- Color blindness simulation
- Color manipulation
- Theme management and persistence
- Real-world use cases
"""

import vargula as vg


def divider(title: str):
    """Print a styled section divider"""
    print("\n" + "=" * 70)
    print(vg.style(f" {title} ", color="#00d9ff", look="bold").center(70))
    print("=" * 70 + "\n")


# ============================================
# 1. BASIC TEXT STYLING
# ============================================

def demo_basic_styling():
    divider("BASIC TEXT STYLING")
    
    # Simple colors
    print("Named colors:")
    print(vg.style("Red text", color="red"))
    print(vg.style("Green background", bg="green"))
    print(vg.style("Bold blue", color="blue", look="bold"))
    
    print("\nHex colors:")
    print(vg.style("Custom orange", color="#FF5733"))
    print(vg.style("Vibrant purple", color="#9b59b6", look="bold"))
    
    print("\nRGB colors:")
    print(vg.style("RGB red", color=(255, 0, 0)))
    print(vg.style("RGB teal", color=(0, 128, 128)))
    
    print("\nCombined styling:")
    print(vg.style("Complete styling", color="#3498db", bg="#ecf0f1", look="bold"))
    
    print("\nMultiple looks:")
    print(vg.style("Bold + Underline", color="cyan", look=["bold", "underline"]))


# ============================================
# 2. MARKUP-STYLE FORMATTING
# ============================================

def demo_markup_formatting():
    divider("MARKUP-STYLE FORMATTING")
    
    # Create custom styles
    vg.create("error", color="red", look="bold")
    vg.create("success", color="green", look="bold")
    vg.create("warning", color="yellow", look="bold")
    vg.create("info", color="cyan")
    
    print("Using custom tags:")
    print(vg.format("Operation <success>successful</success>!"))
    print(vg.format("<error>Error:</error> Connection failed"))
    print(vg.format("<warning>Warning:</warning> Low disk space"))
    print(vg.format("<info>Info:</info> Processing data..."))
    
    print("\nNested tags:")
    print(vg.format("<red>This is <bold>bold red</bold> text</red>"))
    
    print("\nHex color tags:")
    print(vg.format("This is <#FF6B35>custom hex</#FF6B35> color"))
    
    print("\nComplex example:")
    message = """
<bold>System Status Report</bold>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<success>✓</success> Database: Online
<success>✓</success> API Server: Running
<warning>⚠</warning> Cache: 89% full
<error>✗</error> Backup Service: Failed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    print(vg.format(message))


# ============================================
# 3. COLOR PALETTE GENERATION
# ============================================

def demo_palette_generation():
    divider("COLOR PALETTE GENERATION")
    
    print("Random Palette:")
    random_palette = vg.generate_palette(scheme="random", count=6)
    print(vg.preview_palette(random_palette))
    
    print("\n\nMonochromatic (Blue base):")
    mono_palette = vg.generate_palette("#3498db", "monochromatic", 6)
    print(vg.preview_palette(mono_palette))
    
    print("\n\nAnalogous (Red base):")
    analogous_palette = vg.generate_palette("#e74c3c", "analogous", 6)
    print(vg.preview_palette(analogous_palette))
    
    print("\n\nComplementary (Green base):")
    complementary_palette = vg.generate_palette("#2ecc71", "complementary", 6)
    print(vg.preview_palette(complementary_palette))
    
    print("\n\nTriadic (Purple base):")
    triadic_palette = vg.generate_palette("#9b59b6", "triadic", 6)
    print(vg.preview_palette(triadic_palette))
    
    print("\n\nTetradic (Orange base):")
    tetradic_palette = vg.generate_palette("#f39c12", "tetradic", 8)
    print(vg.preview_palette(tetradic_palette))
    
    print("\n\nSplit Complementary (Cyan base):")
    split_comp_palette = vg.generate_palette("#00bcd4", "split_complementary", 6)
    print(vg.preview_palette(split_comp_palette))
    
    print("\n\nSquare (Magenta base):")
    square_palette = vg.generate_palette("#e91e63", "square", 8)
    print(vg.preview_palette(square_palette))


# ============================================
# 4. THEME PALETTES
# ============================================

def demo_theme_palettes():
    divider("THEME PALETTE GENERATION")
    
    print("Generating complementary theme from blue...")
    theme = vg.generate_theme_palette("complementary", "#3498db")
    
    print("\nTheme colors:")
    for name, color in theme.items():
        block = "█" * 20
        styled = vg.style(block, color=color)
        print(f"{name:12s}: {color:8s} {styled}")
    
    print("\n\nApplying theme...")
    vg.apply_palette_theme(theme)
    
    print(vg.format("<primary>Primary action button</primary>"))
    print(vg.format("<secondary>Secondary content</secondary>"))
    print(vg.format("<accent>Accent highlight</accent>"))
    print(vg.format("<success>Operation successful!</success>"))
    print(vg.format("<warning>Warning message</warning>"))
    print(vg.format("<error>Error occurred</error>"))
    print(vg.format("<info>Information notice</info>"))
    
    print("\n\nDynamic theme switching:")
    
    # Sunset theme
    print("\n1. Sunset Theme (Analogous from Orange)")
    sunset_theme = vg.generate_theme_palette("analogous", "#ff6b35")
    vg.apply_palette_theme(sunset_theme)
    print(vg.format("<primary>Warm sunset primary</primary>"))
    print(vg.format("<accent>Vibrant accent</accent>"))
    
    # Ocean theme
    print("\n2. Ocean Theme (Triadic from Teal)")
    ocean_theme = vg.generate_theme_palette("triadic", "#006d77")
    vg.apply_palette_theme(ocean_theme)
    print(vg.format("<primary>Cool ocean primary</primary>"))
    print(vg.format("<accent>Deep accent</accent>"))
    
    # Forest theme
    print("\n3. Forest Theme (Split Complementary from Green)")
    forest_theme = vg.generate_theme_palette("split_complementary", "#2d6a4f")
    vg.apply_palette_theme(forest_theme)
    print(vg.format("<primary>Natural forest primary</primary>"))
    print(vg.format("<accent>Earth accent</accent>"))


# ============================================
# 5. COLOR MANIPULATION
# ============================================

def demo_color_manipulation():
    divider("COLOR MANIPULATION")
    
    base_color = "#3498db"
    print(f"Base color: {vg.style('█' * 30, color=base_color)} {base_color}")
    
    print("\nLighten variations:")
    for i in range(1, 4):
        amount = i * 0.1
        lighter = vg.lighten(base_color, amount)
        print(f"  +{amount:.1f}: {vg.style('█' * 30, color=lighter)} {lighter}")
    
    print("\nDarken variations:")
    for i in range(1, 4):
        amount = i * 0.1
        darker = vg.darken(base_color, amount)
        print(f"  -{amount:.1f}: {vg.style('█' * 30, color=darker)} {darker}")
    
    print("\nSaturate variations:")
    gray = "#8899aa"
    print(f"Base: {vg.style('█' * 30, color=gray)} {gray}")
    for i in range(1, 4):
        amount = i * 0.2
        saturated = vg.saturate(gray, amount)
        print(f"  +{amount:.1f}: {vg.style('█' * 30, color=saturated)} {saturated}")
    
    print("\nDesaturate variations:")
    vibrant = "#e74c3c"
    print(f"Base: {vg.style('█' * 30, color=vibrant)} {vibrant}")
    for i in range(1, 4):
        amount = i * 0.2
        desaturated = vg.desaturate(vibrant, amount)
        print(f"  -{amount:.1f}: {vg.style('█' * 30, color=desaturated)} {desaturated}")
    
    print("\nHue shift:")
    red = "#FF0000"
    print(f"Red (0°):   {vg.style('█' * 30, color=red)} {red}")
    print(f"Yellow (60°): {vg.style('█' * 30, color=vg.shift_hue(red, 60))} {vg.shift_hue(red, 60)}")
    print(f"Green (120°): {vg.style('█' * 30, color=vg.shift_hue(red, 120))} {vg.shift_hue(red, 120)}")
    print(f"Cyan (180°):  {vg.style('█' * 30, color=vg.shift_hue(red, 180))} {vg.shift_hue(red, 180)}")
    print(f"Blue (240°):  {vg.style('█' * 30, color=vg.shift_hue(red, 240))} {vg.shift_hue(red, 240)}")
    print(f"Magenta (300°): {vg.style('█' * 30, color=vg.shift_hue(red, 300))} {vg.shift_hue(red, 300)}")
    
    print("\nColor inversion:")
    colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF"]
    for color in colors:
        inverted = vg.invert(color)
        print(f"{vg.style('█' * 15, color=color)} → {vg.style('█' * 15, color=inverted)}")
    
    print("\nColor mixing:")
    color1 = "#FF0000"  # Red
    color2 = "#0000FF"  # Blue
    print(f"Red:    {vg.style('█' * 30, color=color1)} {color1}")
    print(f"Blue:   {vg.style('█' * 30, color=color2)} {color2}")
    for weight in [0.25, 0.5, 0.75]:
        mixed = vg.mix(color1, color2, weight)
        print(f"Mix {weight:.0%}: {vg.style('█' * 30, color=mixed)} {mixed}")


# ============================================
# 6. ACCESSIBILITY FEATURES
# ============================================

def demo_accessibility():
    divider("ACCESSIBILITY FEATURES (WCAG)")
    
    print("Contrast ratio testing:")
    test_pairs = [
        ("#FFFFFF", "#000000", "Black on white"),
        ("#000000", "#FFFFFF", "White on black"),
        ("#3498db", "#FFFFFF", "Blue on white"),
        ("#e74c3c", "#000000", "Red on black"),
        ("#888888", "#999999", "Gray on gray (poor)"),
    ]
    
    for fg, bg, desc in test_pairs:
        ratio = vg.calculate_contrast_ratio(fg, bg)
        aa_pass = vg.meets_wcag(fg, bg, "AA")
        aaa_pass = vg.meets_wcag(fg, bg, "AAA")
        
        status_aa = vg.style("✓ AA", color="green") if aa_pass else vg.style("✗ AA", color="red")
        status_aaa = vg.style("✓ AAA", color="green") if aaa_pass else vg.style("✗ AAA", color="red")
        
        sample = vg.style("Sample", color=fg, bg=bg)
        print(f"{desc:25s} {sample:20s} Ratio: {ratio:5.2f}:1  {status_aa}  {status_aaa}")
    
    print("\n\nEnsuring contrast (auto-adjustment):")
    background = "#1a1a1a"
    problematic_colors = ["#333333", "#444444", "#555555"]
    
    print(f"Background: {vg.style('█' * 30, color=background)} {background}\n")
    
    for color in problematic_colors:
        adjusted = vg.ensure_contrast(color, background, min_ratio=4.5)
        ratio_before = vg.calculate_contrast_ratio(color, background)
        ratio_after = vg.calculate_contrast_ratio(adjusted, background)
        
        sample_before = vg.style("Before", color=color, bg=background)
        sample_after = vg.style("After ", color=adjusted, bg=background)
        
        print(f"Original: {color} (ratio: {ratio_before:.2f}) {sample_before}")
        print(f"Adjusted: {adjusted} (ratio: {ratio_after:.2f}) {sample_after}")
        print()
    
    print("Generating accessible theme:")
    accessible_theme = vg.generate_accessible_theme(
        base_color="#3498db",
        scheme="complementary",
        background="#ffffff",
        wcag_level="AA"
    )
    
    print("\nAccessible theme on white background:")
    for name, color in list(accessible_theme.items())[:7]:
        ratio = vg.calculate_contrast_ratio(color, "#ffffff")
        meevg = vg.meets_wcag(color, "#ffffff", "AA")
        status = vg.style("✓", color="green") if meevg else vg.style("✗", color="red")
        sample = vg.style("Sample Text", color=color, bg="#ffffff")
        print(f"{name:12s}: {sample:25s} Ratio: {ratio:5.2f}:1 {status}")


# ============================================
# 7. COLOR BLINDNESS SIMULATION
# ============================================

def demo_colorblind_simulation():
    divider("COLOR BLINDNESS SIMULATION")
    
    test_colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"]
    cb_types = ["protanopia", "deuteranopia", "tritanopia"]
    
    print("Original colors:")
    for color in test_colors:
        print(vg.style("█" * 15, color=color), end="  ")
    print(f"\n{'':15s} {'Red':15s} {'Green':15s} {'Blue':15s} {'Yellow':15s} {'Magenta':15s}\n")
    
    for cb_type in cb_types:
        print(f"{cb_type.capitalize():15s}", end="")
        for color in test_colors:
            simulated = vg.simulate_colorblindness(color, cb_type)
            print(vg.style("█" * 15, color=simulated), end="  ")
        print()
    
    print("\n\nPalette color blindness validation:")
    palette = vg.generate_palette("#e74c3c", "triadic", 6)
    
    print("Original palette:")
    print(vg.preview_palette(palette, width=20, show_info=False))
    
    for cb_type in ["deuteranopia", "protanopia", "tritanopia"]:
        is_safe, problems = vg.validate_colorblind_safety(palette, cb_type)
        status = vg.style("✓ SAFE", color="green", look="bold") if is_safe else vg.style("✗ ISSUES", color="red", look="bold")
        print(f"\n{cb_type.capitalize():15s}: {status}")
        if not is_safe:
            print(f"  Problem pairs: {problems}")


# ============================================
# 8. PALETTE PERSISTENCE
# ============================================

def demo_palette_persistence():
    divider("PALETTE PERSISTENCE")
    
    print("Creating and saving palettes...\n")
    
    # Generate a few palettes
    ocean_palette = vg.generate_palette("#006d77", "analogous", 6)
    sunset_palette = vg.generate_palette("#ff6b35", "complementary", 6)
    forest_palette = vg.generate_palette("#2d6a4f", "triadic", 6)
    
    # Save palettes
    vg.save_palette(ocean_palette, "palettes/ocean.json", 
                   metadata={"name": "Ocean Breeze", "scheme": "analogous", "author": "Demo"})
    print("✓ Saved: palettes/ocean.json")
    
    vg.save_palette(sunset_palette, "palettes/sunset.json",
                   metadata={"name": "Sunset Glory", "scheme": "complementary"})
    print("✓ Saved: palettes/sunset.json")
    
    vg.save_palette(forest_palette, "palettes/forest.json",
                   metadata={"name": "Forest Deep", "scheme": "triadic"})
    print("✓ Saved: palettes/forest.json")
    
    # Generate and save theme
    theme = vg.generate_theme_palette("complementary", "#9b59b6")
    vg.save_theme(theme, "themes/purple_reign.json",
                 metadata={"name": "Purple Reign", "description": "Royal purple theme"})
    print("✓ Saved: themes/purple_reign.json")
    
    print("\n\nLoading saved palette...")
    loaded_colors, metadata = vg.load_palette("palettes/ocean.json")
    print(f"Loaded: {metadata['name']} (Scheme: {metadata['scheme']})")
    print(vg.preview_palette(loaded_colors, width=20, show_info=False))
    
    print("\n\nLoading saved theme...")
    loaded_theme, theme_meta = vg.load_theme("themes/purple_reign.json")
    print(f"Loaded: {theme_meta['name']}")
    print(f"Description: {theme_meta['description']}")
    
    vg.apply_palette_theme(loaded_theme)
    print(vg.format("\n<primary>Primary</primary> | <secondary>Secondary</secondary> | <accent>Accent</accent>"))
    print(vg.format("<success>Success</success> | <warning>Warning</warning> | <error>Error</error>"))


# ============================================
# 9. REAL-WORLD USE CASES
# ============================================

def demo_real_world_use_cases():
    divider("REAL-WORLD USE CASES")
    
    # Use case 1: CLI Progress/Status
    print("1. CLI Progress/Status Display\n")
    vg.create("progress", color="#00d9ff", look="bold")
    vg.create("complete", color="#00ff88", look="bold")
    vg.create("pending", color="#ffaa00")
    
    tasks = [
        ("Installing dependencies", "complete"),
        ("Compiling source code", "complete"),
        ("Running tesvg", "progress"),
        ("Building documentation", "pending"),
        ("Deploying to production", "pending"),
    ]
    
    for task, status in tasks:
        if status == "complete":
            icon = vg.format("<complete>✓</complete>")
        elif status == "progress":
            icon = vg.format("<progress>●</progress>")
        else:
            icon = vg.format("<pending>○</pending>")
        print(f"{icon} {task}")
    
    # Use case 2: Log Level Coloring
    print("\n\n2. Log Level Coloring\n")
    vg.create("debug", color="#666666")
    vg.create("info", color="#00d9ff")
    vg.create("warn", color="#ffaa00", look="bold")
    vg.create("err", color="#ff4444", look="bold")
    vg.create("critical", color="white", bg="red", look="bold")
    
    logs = [
        ("DEBUG", "debug", "Loading configuration from config.yaml"),
        ("INFO", "info", "Server started on port 8080"),
        ("WARN", "warn", "Deprecated API endpoint used: /api/v1/users"),
        ("ERROR", "err", "Failed to connect to database: timeout after 30s"),
        ("CRITICAL", "critical", "Out of memory: cannot allocate 4GB"),
    ]
    
    for level, tag, message in logs:
        timestamp = "2024-01-15 10:30:45"
        print(f"[{timestamp}] {vg.format(f'<{tag}>{level:8s}</{tag}>')} {message}")
    
    # Use case 3: Data Visualization
    print("\n\n3. Data Visualization (Sales Performance)\n")
    
    # Generate a blue-to-green gradient theme
    perf_theme = vg.generate_theme_palette("analogous", "#00bcd4")
    vg.apply_palette_theme(perf_theme)
    
    sales_data = [
        ("Q1 2024", 85, "success"),
        ("Q2 2024", 92, "success"),
        ("Q3 2024", 78, "warning"),
        ("Q4 2024", 95, "success"),
    ]
    
    print("Quarterly Sales Performance:")
    for quarter, percentage, status in sales_data:
        bar_length = int(percentage / 2)
        bar = "█" * bar_length
        colored_bar = vg.format(f"<{status}>{bar}</{status}>")
        print(f"{quarter}: {colored_bar} {percentage}%")
    
    # Use case 4: Diff Highlighting
    print("\n\n4. Code Diff Highlighting\n")
    vg.create("added", color="#00ff88", bg="#003322")
    vg.create("removed", color="#ff4444", bg="#330000")
    vg.create("modified", color="#ffaa00", bg="#332200")
    
    diff_lines = [
        ("  ", "def calculate_total(items):"),
        ("-", "    total = 0"),
        ("+", "    total = Decimal('0.00')"),
        ("  ", "    for item in items:"),
        ("-", "        total += item.price"),
        ("+", "        total += Decimal(str(item.price))"),
        ("  ", "    return total"),
    ]
    
    for marker, line in diff_lines:
        if marker == "+":
            print(vg.format(f"<added>{marker} {line}</added>"))
        elif marker == "-":
            print(vg.format(f"<removed>{marker} {line}</removed>"))
        else:
            print(f"{marker} {line}")
    
    # Use case 5: Interactive Menu
    print("\n\n5. Interactive Menu System\n")
    vg.create("menu_title", color="#00d9ff", look="bold")
    vg.create("menu_item", color="#00ff88")
    vg.create("menu_selected", color="black", bg="#00ff88", look="bold")
    vg.create("menu_disabled", color="#666666")
    
    print(vg.format("<menu_title>╔══════════════════════════════╗</menu_title>"))
    print(vg.format("<menu_title>║      MAIN MENU               ║</menu_title>"))
    print(vg.format("<menu_title>╚══════════════════════════════╝</menu_title>"))
    print()
    print(vg.format("<menu_selected> → New Project              </menu_selected>"))
    print(vg.format("<menu_item>   Open Project             </menu_item>"))
    print(vg.format("<menu_item>   Recent Files             </menu_item>"))
    print(vg.format("<menu_item>   Settings                 </menu_item>"))
    print(vg.format("<menu_disabled>   Export (Not Available)    </menu_disabled>"))
    print(vg.format("<menu_item>   Exit                     </menu_item>"))


# ============================================
# 10. PERFORMANCE AND UTILITIES
# ============================================

def demo_utilities():
    divider("UTILITIES & HELPERS")
    
    print("1. Strip markup:")
    markup = "<red>Error:</red> <bold>Connection failed</bold>"
    print(f"   Original: {markup}")
    print(f"   Stripped: {vg.strip(markup)}")
    
    print("\n2. Clean ANSI codes:")
    styled = vg.style("Hello World", color="red", look="bold")
    print(f"   Styled length: {len(styled)} chars (includes ANSI codes)")
    print(f"   Visible length: {vg.length(styled)} chars (visible only)")
    print(f"   Cleaned text: '{vg.clean(styled)}'")
    
    print("\n3. Temporary styles:")
    with vg.temporary("temp", color="magenta", look="italic"):
        print(vg.format("   <temp>This style exisvg only in this block</temp>"))
    print(vg.format("   <temp>This will be plain text (style deleted)</temp>"))
    
    print("\n4. Theme switching:")
    themes = ["dark", "light"]
    for theme_name in themes:
        vg.set_theme(theme_name)
        print(f"\n   {theme_name.capitalize()} theme:")
        print(vg.format("   <error>Error</error> <success>Success</success> <warning>Warning</warning> <info>Info</info>"))
    
    print("\n5. Enable/Disable styling:")
    print("   Enabled:", vg.style("Colored text", color="green"))
    vg.disable()
    print("   Disabled:", vg.style("Plain text", color="green"))
    vg.enable()
    print("   Re-enabled:", vg.style("Colored again", color="green"))


# ============================================
# MAIN DEMO RUNNER
# ============================================

def main():
    """Run all demos"""
    
    print(vg.style("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║              vargula COMPREHENSIVE DEMO                        ║
║            Advanced Terminal Styling & Color Theory              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""", color="#00d9ff", look="bold"))
    
    demos = [
        ("Basic Styling", demo_basic_styling),
        ("Markup Formatting", demo_markup_formatting),
        ("Palette Generation", demo_palette_generation),
        ("Theme Palettes", demo_theme_palettes),
        ("Color Manipulation", demo_color_manipulation),
        ("Accessibility", demo_accessibility),
        ("Color Blindness", demo_colorblind_simulation),
        ("Persistence", demo_palette_persistence),
        ("Real-World Use Cases", demo_real_world_use_cases),
        ("Utilities", demo_utilities),
    ]
    
    print("\nSelect a demo to run:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i:2d}. {name}")
    print(f"  {len(demos)+1:2d}. Run all demos")
    print(f"   0. Exit")
    
    try:
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "0":
            print("Goodbye!")
            return
        elif choice == str(len(demos) + 1):
            for name, func in demos:
                func()
                input("\nPress Enter to continue...")
        else:
            idx = int(choice) - 1
            if 0 <= idx < len(demos):
                demos[idx][1]()
            else:
                print("Invalid choice!")
    except (ValueError, KeyboardInterrupt):
        print("\nExiting...")
    except Exception as e:
        print(vg.format(f"<error>Error: {e}</error>"))


if __name__ == "__main__":
    main()