import gi
import math
gi.require_version('Gtk', '4.0')
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, Graphene, Pango, PangoCairo

class SimpleChart(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.set_draw_func(self.draw_func)
        self.data_points = []
        self.years = 30 # Default timeframe
        self.set_content_height(250)

    def set_data(self, points, years):
        self.data_points = points
        self.years = years
        self.queue_draw()

    def draw_func(self, area, cr, width, height):
        if not self.data_points:
            return

        # --- Configuration ---
        # Margins for text labels
        margin_left = 50
        margin_bottom = 30
        margin_top = 20
        margin_right = 20

        # Drawing Area Dimensions
        graph_w = width - margin_left - margin_right
        graph_h = height - margin_top - margin_bottom

        # Color: Adwaita Blue #3584e4
        r, g, b = 0.2, 0.52, 0.89

        # Data Normalization
        max_val = max(self.data_points)
        min_val = min(self.data_points)

        # Ensure we don't divide by zero if flat line
        if max_val == min_val:
            max_val += 100

        val_range = max_val - min_val

        # --- Helpers ---
        def get_x(index):
            # Map index (0..len) to X pixel
            return margin_left + (index / (len(self.data_points) - 1) * graph_w)

        def get_y(val):
            # Map value to Y pixel (inverted)
            ratio = (val - min_val) / val_range
            return (margin_top + graph_h) - (ratio * graph_h)

        # --- Draw Grid & Y-Axis Labels ---
        cr.set_line_width(1)
        layout = area.create_pango_layout("")
        layout.set_font_description(Pango.FontDescription("Sans 9"))

        # We draw 3 grid lines: Max, Mid, Min
        grid_steps = 3
        for i in range(grid_steps):
            ratio = i / (grid_steps - 1)
            val = min_val + (val_range * ratio)
            y = get_y(val)

            # Draw Text
            # Format large numbers (e.g. 1.2M or 120k)
            txt = f"{val:,.0f}"
            if val > 1_000_000: txt = f"{val/1_000_000:.1f}M"
            elif val > 1_000: txt = f"{val/1_000:.0f}k"

            layout.set_text(txt, -1)
            # Align text to right of margin_left
            ink, logical = layout.get_extents()
            text_w = logical.width / Pango.SCALE
            text_h = logical.height / Pango.SCALE

            cr.move_to(margin_left - text_w - 8, y - (text_h / 2))
            cr.set_source_rgba(0.5, 0.5, 0.5, 1) # Grey Text
            PangoCairo.show_layout(cr, layout)

            # Draw Grid Line
            cr.move_to(margin_left, y)
            cr.line_to(width - margin_right, y)
            cr.set_source_rgba(0.8, 0.8, 0.8, 0.5) # Light Grey Line
            cr.stroke()

        # --- Draw X-Axis Labels (Years) ---
        # Draw Start, Middle, End
        x_labels = [0, self.years // 2, self.years]
        for year in x_labels:
            # Find closest data index for this year
            # data_points length = years + 1 (usually)
            idx = int((year / self.years) * (len(self.data_points) - 1))
            x = get_x(idx)

            txt = f"Yr {year}"
            layout.set_text(txt, -1)
            ink, logical = layout.get_extents()
            text_w = logical.width / Pango.SCALE

            cr.move_to(x - (text_w / 2), margin_top + graph_h + 5)
            cr.set_source_rgba(0.5, 0.5, 0.5, 1)
            PangoCairo.show_layout(cr, layout)

        # --- Draw Graph Fill ---
        cr.set_source_rgba(r, g, b, 0.2)
        cr.move_to(margin_left, margin_top + graph_h) # Bottom Left

        for i, val in enumerate(self.data_points):
            cr.line_to(get_x(i), get_y(val))

        cr.line_to(width - margin_right, margin_top + graph_h) # Bottom Right
        cr.close_path()
        cr.fill()

        # --- Draw Graph Line ---
        cr.set_source_rgba(r, g, b, 1.0)
        cr.set_line_width(3)

        for i, val in enumerate(self.data_points):
            if i == 0:
                cr.move_to(get_x(i), get_y(val))
            else:
                cr.line_to(get_x(i), get_y(val))

        cr.stroke()

        # --- Draw Zero Baseline (if in range) ---
        if min_val < 0 and max_val > 0:
            zero_y = get_y(0)
            cr.set_source_rgba(0.9, 0.3, 0.3, 0.6) # Red
            cr.set_line_width(1.5)
            cr.move_to(margin_left, zero_y)
            cr.line_to(width - margin_right, zero_y)
            cr.stroke()
