from gi.repository import Adw, Gtk, Gio, GObject
from data_manager import DataManager
from models import Asset, Stream, Milestone
from price_service import PriceService
from chart_widget import SimpleChart

class FireFinanceWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("FireFinance")
        self.set_default_size(1100, 750)

        # --- Data & Services ---
        self.data_manager = DataManager()
        self.finance_data = self.data_manager.load_data()

        self.projection_years = 30

        self.price_service = PriceService()
        self.price_service.connect('prices-updated', self.on_prices_updated)
        self.price_service.connect('update-failed', self.on_price_failed)
        self.price_service.fetch_prices()

        # --- Layout ---
        self.split_view = Adw.NavigationSplitView()
        self.set_content(self.split_view)

        self._build_sidebar()
        self.show_dashboard()

    def _build_sidebar(self):
        self.sidebar_page = Adw.NavigationPage(title="FireFinance", tag="sidebar")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.nav_list = Gtk.ListBox(css_classes=["navigation-sidebar"])
        self.nav_list.connect("row-selected", self.on_nav_row_selected)
        self.nav_list.set_vexpand(True)

        self.add_nav_row("dashboard", "Dashboard", "graph-app-symbolic")
        self.add_nav_row("assets", "Assets", "wallet-symbolic")
        self.add_nav_row("income", "Income", "money-symbolic")
        self.add_nav_row("expenses", "Expenses", "card-symbolic")
        self.add_nav_row("milestones", "Milestones", "flag-symbolic")
        self.add_nav_row("settings", "Settings", "preferences-system-symbolic")

        footer_grp = Adw.PreferencesGroup()
        toggle_row = Adw.SwitchRow(title="View in BTC")
        toggle_row.set_subtitle("Convert all values")
        toggle_row.connect("notify::active", self.on_currency_toggled)
        footer_grp.add(toggle_row)

        box.append(self.nav_list)
        box.append(footer_grp)

        self.sidebar_page.set_child(box)
        self.split_view.set_sidebar(self.sidebar_page)

    def add_nav_row(self, id_name, title, icon_name):
        row = Adw.ActionRow(title=title)
        row.add_prefix(Gtk.Image.new_from_icon_name(icon_name))
        row._id = id_name
        self.nav_list.append(row)

    # --- Events ---

    def on_nav_row_selected(self, listbox, row):
        if not row: return
        view_id = row._id

        if view_id == "dashboard": self.show_dashboard()
        elif view_id == "assets": self.show_assets()
        elif view_id == "income": self.show_streams(is_income=True)
        elif view_id == "expenses": self.show_streams(is_income=False)
        elif view_id == "milestones": self.show_milestones()
        elif view_id == "settings": self.show_settings()

    def on_currency_toggled(self, row, param):
        if row.get_active():
            self.finance_data.display_currency = "BTC"
        else:
            self.finance_data.display_currency = "USD"

        selected_row = self.nav_list.get_selected_row()
        if selected_row:
            self.on_nav_row_selected(self.nav_list, selected_row)

    def on_prices_updated(self, service):
        self.finance_data.btc_price = service.btc_price
        self.finance_data.stx_price = service.stx_price
        selected_row = self.nav_list.get_selected_row()
        if selected_row and selected_row._id == "dashboard":
            self.show_dashboard()

    def on_price_failed(self, service, error):
        print(f"Price update failed: {error}")

    def on_years_changed(self, spin_row, param):
        self.projection_years = int(spin_row.get_value())
        if hasattr(self, 'chart'):
            proj_values = self.finance_data.get_projection(years=self.projection_years)
            self.chart.set_data(proj_values, self.projection_years)

    # --- Views ---

    def show_dashboard(self):
        page = Adw.NavigationPage(title="Dashboard", tag="dashboard")

        status_desc = f"BTC: ${self.finance_data.btc_price:,.0f} | STX: ${self.finance_data.stx_price:,.2f}"
        status = Adw.StatusPage(icon_name="graph-app-symbolic", title="FireFinance", description=status_desc)
        status.set_vexpand(False)

        scroll = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.append(status)

        clamp = Adw.Clamp(maximum_size=700)
        card_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        card_box.set_margin_bottom(24)

        sym = "₿" if self.finance_data.display_currency == "BTC" else "$"

        # 1. Market Data
        grp_market = Adw.PreferencesGroup(title="Market Data")
        row_btc = Adw.ActionRow(title="Bitcoin (BTC)")
        row_btc.add_suffix(Gtk.Label(label=f"${self.finance_data.btc_price:,.2f}"))
        grp_market.add(row_btc)
        row_stx = Adw.ActionRow(title="Stacks (STX)")
        row_stx.add_suffix(Gtk.Label(label=f"${self.finance_data.stx_price:,.2f}"))
        grp_market.add(row_stx)
        card_box.append(grp_market)

        # 2. Metrics
        grp_metrics = Adw.PreferencesGroup(title="Overview")

        net_worth = self.finance_data.net_worth
        row_nw = Adw.ActionRow(title="Total Net Worth")
        row_nw.add_suffix(Gtk.Label(label=f"{sym} {net_worth:,.2f}"))
        grp_metrics.add(row_nw)

        w_apy = self.finance_data.weighted_apy * 100
        row_apy = Adw.ActionRow(title="Weighted APY")
        row_apy.set_subtitle("Average return on all assets")
        row_apy.add_suffix(Gtk.Label(label=f"{w_apy:.2f}%"))
        grp_metrics.add(row_apy)

        burn = self.finance_data.annual_burn_rate
        row_burn = Adw.ActionRow(title="Net Cash Flow (Pre-Tax)")
        row_burn.set_subtitle("Income - Expenses")
        color_class = "success" if burn > 0 else "error"
        lbl_burn = Gtk.Label(label=f"{sym} {burn:,.2f}")
        lbl_burn.add_css_class(color_class)
        row_burn.add_suffix(lbl_burn)
        grp_metrics.add(row_burn)

        burn_post_tax = self.finance_data.annual_net_flow_post_tax
        row_burn_tax = Adw.ActionRow(title="Projected Net Annual Change")
        row_burn_tax.set_subtitle("Cash Flow + Investment Growth (Post-Tax)")
        color_class_tax = "success" if burn_post_tax > 0 else "error"
        lbl_burn_tax = Gtk.Label(label=f"{sym} {burn_post_tax:,.2f}")
        lbl_burn_tax.add_css_class(color_class_tax)
        row_burn_tax.add_suffix(lbl_burn_tax)
        grp_metrics.add(row_burn_tax)

        card_box.append(grp_metrics)

        # 3. Chart
        grp_chart = Adw.PreferencesGroup(title="Projection (Includes Taxes and Milestones)")
        row_years = Adw.SpinRow.new_with_range(5, 100, 1)
        row_years.set_title("Timeframe (Years)")
        row_years.set_value(self.projection_years)
        row_years.connect("notify::value", self.on_years_changed)
        grp_chart.add(row_years)

        chart_bin = Adw.Bin()
        chart_bin.set_css_classes(["card"])
        chart_bin.set_size_request(-1, 250)

        self.chart = SimpleChart()
        proj_values = self.finance_data.get_projection(years=self.projection_years)
        self.chart.set_data(proj_values, self.projection_years)

        chart_bin.set_child(self.chart)
        card_box.append(grp_chart)
        card_box.append(chart_bin)

        clamp.set_child(card_box)
        box.append(clamp)
        scroll.set_child(box)
        page.set_child(scroll)
        self.split_view.set_content(page)

    def show_milestones(self):
        self._show_list_page(
            title="Milestones",
            items=self.finance_data.milestones,
            dialog_func=self.show_milestone_dialog,
            delete_func=self.delete_milestone
        )

    def show_assets(self):
        self._show_list_page("Assets", self.finance_data.assets, self.show_asset_dialog, self.delete_asset)

    def show_streams(self, is_income):
        items = [s for s in self.finance_data.streams if s.is_income == is_income]
        title = "Income" if is_income else "Expenses"
        def wrapper(item=None): self.show_stream_dialog(is_income, item)
        self._show_list_page(title, items, wrapper, self.delete_stream)

    def show_settings(self):
        page = Adw.NavigationPage(title="Settings", tag="settings")
        clamp = Adw.Clamp(maximum_size=600)

        # Tax Settings
        grp_tax = Adw.PreferencesGroup(title="Tax Estimation")

        def create_tax_row(title, current_val, callback):
            row = Adw.SpinRow.new_with_range(0, 100, 0.1)
            row.set_title(title)
            row.set_subtitle("Percentage (%)")
            row.set_value(current_val * 100)
            row.connect("notify::value", callback)
            return row

        def on_income_tax(row, p):
            self.finance_data.tax_rate_income = row.get_value() / 100.0
            self.data_manager.save_data()

        def on_prop_tax(row, p):
            self.finance_data.tax_rate_property = row.get_value() / 100.0
            self.data_manager.save_data()

        def on_cap_gains(row, p):
            self.finance_data.tax_rate_cap_gains = row.get_value() / 100.0
            self.data_manager.save_data()

        grp_tax.add(create_tax_row("Income Tax Rate", self.finance_data.tax_rate_income, on_income_tax))
        grp_tax.add(create_tax_row("Property Tax Rate", self.finance_data.tax_rate_property, on_prop_tax))
        grp_tax.add(create_tax_row("Capital Gains Tax Rate", self.finance_data.tax_rate_cap_gains, on_cap_gains))

        grp_data = Adw.PreferencesGroup(title="Storage")
        row = Adw.ActionRow(title="Data Location")
        row.set_subtitle(self.data_manager.data_dir)
        btn = Gtk.Button(icon_name="folder-open-symbolic", valign=Gtk.Align.CENTER)
        btn.add_css_class("flat")
        btn.connect("clicked", lambda x: Gtk.show_uri(None, f"file://{self.data_manager.data_dir}", 0))
        row.add_suffix(btn)
        grp_data.add(row)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.append(grp_tax)
        box.append(grp_data)

        clamp.set_child(box)
        page.set_child(clamp)
        self.split_view.set_content(page)

    # --- Generic List Builder ---
    def _show_list_page(self, title, items, dialog_func, delete_func):
        page = Adw.NavigationPage(title=title, tag=title.lower())
        tb_view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.connect("clicked", lambda x: dialog_func(None))
        header.pack_end(add_btn)
        tb_view.add_top_bar(header)

        clamp = Adw.Clamp(maximum_size=800)
        scroll = Gtk.ScrolledWindow()
        grp = Adw.PreferencesGroup()
        sym = "₿" if self.finance_data.display_currency == "BTC" else "$"

        for item in items:
            row = Adw.ActionRow(title=item.name)
            row.set_activatable(True)

            sub = ""
            if isinstance(item, Milestone):
                sub = f"Year {item.year_offset} • Duration: {item.duration} yr(s)"
            elif isinstance(item, Stream):
                sub = f"{item.frequency}"
            elif isinstance(item, Asset):
                if item.is_real_estate: sub = "Real Estate"
                if item.apy > 0: sub += f" • {(item.apy*100):.1f}% APY"
                if hasattr(item, 'tax_treatment'):
                    sub += f" • {item.tax_treatment}"

            row.set_subtitle(sub.strip(" •"))

            raw_val = getattr(item, 'balance', getattr(item, 'amount', 0))
            conv_val = self.finance_data.get_converted_value(raw_val, getattr(item, 'currency', 'USD'))

            val_label = Gtk.Label(label=f"{sym} {conv_val:,.2f}", margin_end=12)
            row.add_suffix(val_label)
            row.connect("activated", lambda r, i=item: dialog_func(i))

            del_btn = Gtk.Button(icon_name="user-trash-symbolic")
            del_btn.add_css_class("flat")
            del_btn.connect("clicked", lambda btn, i=item: delete_func(i))
            row.add_suffix(del_btn)
            grp.add(row)

        clamp.set_child(grp)
        scroll.set_child(clamp)
        tb_view.set_content(scroll)
        page.set_child(tb_view)
        self.split_view.set_content(page)

    # --- Dialogs ---

    def show_milestone_dialog(self, m=None):
        is_edit = m is not None
        dialog = Adw.MessageDialog(transient_for=self, heading="Edit Milestone" if is_edit else "Add Milestone", width_request=400)
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("save", "Save")
        dialog.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)

        grp = Adw.PreferencesGroup()
        name_entry = Adw.EntryRow(title="Name")
        amount_entry = Adw.EntryRow(title="Cost per Year")
        year_entry = Adw.SpinRow.new_with_range(0, 100, 1)
        year_entry.set_title("Starts In (Years)")
        dur_entry = Adw.SpinRow.new_with_range(1, 20, 1)
        dur_entry.set_title("Duration (Years)")

        if is_edit:
            name_entry.set_text(m.name)
            amount_entry.set_text(str(m.amount))
            year_entry.set_value(m.year_offset)
            dur_entry.set_value(m.duration)

        grp.add(name_entry)
        grp.add(amount_entry)
        grp.add(year_entry)
        grp.add(dur_entry)
        dialog.set_extra_child(grp)

        def on_response(d, response):
            if response == "save":
                try:
                    name = name_entry.get_text()
                    amt = float(amount_entry.get_text())
                    y = int(year_entry.get_value())
                    dur = int(dur_entry.get_value())

                    if is_edit:
                        m.name, m.amount, m.year_offset, m.duration = name, amt, y, dur
                    else:
                        self.finance_data.milestones.append(Milestone(name=name, amount=amt, year_offset=y, duration=dur))
                    self.data_manager.save_data()
                    self.show_milestones()
                except ValueError: print("Invalid")
        dialog.connect("response", on_response)
        dialog.present()

    def show_asset_dialog(self, asset=None):
        is_edit = asset is not None
        dialog = Adw.MessageDialog(transient_for=self, heading="Edit Asset" if is_edit else "Add Asset", width_request=400)
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("save", "Save")
        dialog.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)

        grp = Adw.PreferencesGroup()
        name_entry = Adw.EntryRow(title="Name")
        balance_entry = Adw.EntryRow(title="Balance")
        apy_entry = Adw.EntryRow(title="APY (0.05 = 5%)")
        re_switch = Adw.SwitchRow(title="Is Real Estate?")
        re_switch.set_subtitle("Subject to Property Tax")

        # New Tax Treatment Combo
        tax_row = Adw.ComboRow(title="Tax Treatment")
        tax_model = Gtk.StringList()
        tax_model.append("Capital Gains")
        tax_model.append("Ordinary Income")
        tax_row.set_model(tax_model)

        curr_row = Adw.ComboRow(title="Currency")
        curr_model = Gtk.StringList(); curr_model.append("USD"); curr_model.append("BTC"); curr_model.append("STX")
        curr_row.set_model(curr_model)

        if is_edit:
            name_entry.set_text(asset.name)
            balance_entry.set_text(str(asset.balance))
            apy_entry.set_text(str(asset.apy))
            re_switch.set_active(asset.is_real_estate)

            # Set Currency Selection
            if asset.currency == "BTC": curr_row.set_selected(1)
            elif asset.currency == "STX": curr_row.set_selected(2)

            # Set Tax Treatment Selection
            if asset.tax_treatment == "Ordinary Income":
                tax_row.set_selected(1)
            else:
                tax_row.set_selected(0)

        grp.add(name_entry)
        grp.add(balance_entry)
        grp.add(apy_entry)
        grp.add(tax_row)
        grp.add(re_switch)
        grp.add(curr_row)
        dialog.set_extra_child(grp)

        def on_response(d, response):
            if response == "save":
                try:
                    name = name_entry.get_text()
                    bal = float(balance_entry.get_text())
                    apy = float(apy_entry.get_text() or 0)
                    curr = ["USD", "BTC", "STX"][curr_row.get_selected()]
                    is_re = re_switch.get_active()

                    tax_idx = tax_row.get_selected()
                    tax_treat = "Ordinary Income" if tax_idx == 1 else "Capital Gains"

                    if is_edit:
                        asset.name = name
                        asset.balance = bal
                        asset.currency = curr
                        asset.apy = apy
                        asset.is_real_estate = is_re
                        asset.tax_treatment = tax_treat
                    else:
                        self.finance_data.assets.append(Asset(name, bal, curr, apy, is_re, tax_treat))
                    self.data_manager.save_data()
                    self.show_assets()
                except ValueError: print("Invalid")
        dialog.connect("response", on_response)
        dialog.present()

    def show_stream_dialog(self, is_income, stream=None):
        is_edit = stream is not None
        type_str = "Income" if is_income else "Expense"
        dialog = Adw.MessageDialog(transient_for=self, heading=f"{'Edit' if is_edit else 'Add'} {type_str}", width_request=400)
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("save", "Save")
        dialog.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)

        grp = Adw.PreferencesGroup()
        name_entry = Adw.EntryRow(title="Name")
        amount_entry = Adw.EntryRow(title="Amount")
        freq_row = Adw.ComboRow(title="Frequency")
        freq_model = Gtk.StringList(); freq_model.append("Monthly"); freq_model.append("Yearly")
        freq_row.set_model(freq_model)

        if is_edit:
            name_entry.set_text(stream.name)
            amount_entry.set_text(str(stream.amount))
            freq_row.set_selected(1 if stream.frequency == "Yearly" else 0)

        grp.add(name_entry)
        grp.add(amount_entry)
        grp.add(freq_row)
        dialog.set_extra_child(grp)

        def on_response(d, response):
            if response == "save":
                try:
                    name = name_entry.get_text()
                    amt = float(amount_entry.get_text())
                    freq = "Monthly" if freq_row.get_selected() == 0 else "Yearly"
                    if is_edit: stream.name, stream.amount, stream.frequency = name, amt, freq
                    else: self.finance_data.streams.append(Stream(name, amt, "USD", freq, is_income))
                    self.data_manager.save_data()
                    self.show_streams(is_income)
                except ValueError: print("Invalid")
        dialog.connect("response", on_response)
        dialog.present()

    def delete_milestone(self, m):
        self.finance_data.milestones.remove(m)
        self.data_manager.save_data()
        self.show_milestones()

    def delete_asset(self, a):
        self.finance_data.assets.remove(a)
        self.data_manager.save_data()
        self.show_assets()

    def delete_stream(self, s):
        self.finance_data.streams.remove(s)
        self.data_manager.save_data()
        self.show_streams(s.is_income)
