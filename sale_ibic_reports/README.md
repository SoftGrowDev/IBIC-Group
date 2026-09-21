# IBIC Sale & Invoice Reports - Enhanced Version for Odoo 19

## Overview
This enhanced addon extends the original IBIC Sale Reports module to include:
- **Packing and Proforma reports for INVOICES** (not just sale orders)
- **Green background theme** for invoice reports (vs blue for sale orders)
- **Automatic data copying** from sale orders to invoices
- **Shipping & Reports tab** on invoice forms

## What's New

### 1. New Models
- **account_move.py**: Extends invoices with shipping, packing, and bank details fields
- **invoice_packing_line.py**: Packing list lines for invoices (similar to sale order packing lines)

### 2. New Views
- **invoice_views.xml**: Adds "Shipping & Reports" tab to invoice forms with:
  - Transport details (country of origin, board date, ports, etc.)
  - Packing list with container numbers and weights
  - Invoice notes and terms
  - Bank details with "Reload from Company" button

### 3. New Reports
- **Invoice Proforma Invoice (IBIC)**: Green-themed proforma invoice report
- **Invoice Packing List (IBIC)**: Green-themed packing list report

### 4. Color Scheme
**Sale Orders (Blue):**
- Header background: #1f6394 (dark blue)
- Data cells: #d6eaf8 (light blue)
- Borders: #aac9e0 (blue borders)

**Invoices (Green):**
- Header background: #2d8659 (dark green)
- Data cells: #d4f1e3 (light green)
- Borders: #a8ddc4 (green borders)

## Features

### Automatic Data Transfer
When an invoice is created from a sale order, the following data is **automatically copied**:
- All shipping/transport fields
- Packing list lines
- Payment notes and conditions
- Bank details
- Terms & conditions

### Manual Editing
All copied data can be manually edited on the invoice if needed.

## Installation

1. **Backup your database** before installing
2. Remove the old `sale_ibic_reports` module if installed:
   ```bash
   # In Odoo Apps, uninstall the old version first
   ```
3. Copy the new `sale_ibic_reports` folder to your Odoo addons directory
4. Update the apps list:
   ```bash
   # In Odoo: Apps → Update Apps List
   ```
5. Install/Upgrade the module:
   ```bash
   # In Odoo: Apps → Search "IBIC" → Install or Upgrade
   ```

## Usage

### For Sale Orders (Unchanged)
1. Create a sale order as usual
2. Go to "Shipping & Reports" tab
3. Fill in transport details, packing lines, bank details, etc.
4. Print reports:
   - Print → Proforma Invoice (Blue theme)
   - Print → Packing List (Blue theme)

### For Invoices (New!)
1. Create an invoice from a sale order (or manually)
2. If created from a sale order, all shipping data is **automatically copied**
3. Go to "Shipping & Reports" tab (only visible on customer invoices)
4. Review/edit the automatically copied data or add new data
5. Print reports:
   - Print → Proforma Invoice (IBIC) - Green theme
   - Print → Packing List (IBIC) - Green theme

## Field Mapping

### Sale Order Fields → Invoice Fields
```
so_country_of_origin_id  → inv_country_of_origin_id
so_board_date            → inv_board_date
so_carriage_by           → inv_carriage_by
so_port_of_loading       → inv_port_of_loading
so_port_of_discharge     → inv_port_of_discharge
so_waybill_no            → inv_waybill_no
so_container_lta         → inv_container_lta
so_place_of_delivery     → inv_place_of_delivery
so_incoterm_id           → inv_incoterm_id
so_bl_number             → inv_bl_number
so_payment_note          → inv_payment_note
so_conditions            → inv_conditions
so_terms                 → inv_terms
so_bank_*                → inv_bank_*
so_packing_line_ids      → inv_packing_line_ids
```

## Technical Details

### Dependencies
- sale_management
- account

### New Security Rules
Access rights added for:
- `invoice.packing.line` model
  - User: account.group_account_invoice
  - Manager: account.group_account_manager

### Database Schema
**New Table:** `invoice_packing_line`
- move_id (Many2one to account.move)
- sequence
- container_no
- product_id
- item_description
- origin_country_id
- qty_cartons
- unit_weight_kg
- tare_per_carton
- total_net_weight (computed)
- total_gross_weight (computed)

**Extended Table:** `account_move`
- All `inv_*` fields (see Field Mapping above)
- inv_total_cartons (computed)
- inv_total_net_weight (computed)
- inv_total_gross_weight (computed)
- inv_amount_in_words (computed)

## Customization

### Changing Colors
To modify report colors, edit:
- **Sale Order reports:** `report/proforma_invoice_template.xml` and `report/packing_list_template.xml`
- **Invoice reports:** `report/invoice_proforma_template.xml` and `report/invoice_packing_list_template.xml`

Search and replace:
- Header background: Change `#2d8659` (green) or `#1f6394` (blue)
- Light background: Change `#d4f1e3` (light green) or `#d6eaf8` (light blue)
- Borders: Change `#a8ddc4` (green borders) or `#aac9e0` (blue borders)

### Default Values
Modify default payment notes, conditions, etc. in:
- `models/sale_order.py` for sale orders
- `models/account_move.py` for invoices

## File Structure
```
sale_ibic_reports/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── res_company.py
│   ├── sale_order.py
│   ├── sale_packing_line.py
│   ├── account_move.py          ← NEW
│   └── invoice_packing_line.py  ← NEW
├── views/
│   ├── res_company_views.xml
│   ├── sale_order_views.xml
│   └── invoice_views.xml        ← NEW
├── report/
│   ├── report_actions.xml
│   ├── proforma_invoice_template.xml
│   ├── packing_list_template.xml
│   ├── invoice_report_actions.xml       ← NEW
│   ├── invoice_proforma_template.xml    ← NEW
│   └── invoice_packing_list_template.xml ← NEW
├── data/
│   └── paperformat.xml
└── security/
    └── ir.model.access.csv      ← UPDATED
```

## Troubleshooting

### Data not copying from sale order to invoice?
- Ensure the sale order has the shipping data filled in the "Shipping & Reports" tab
- Check that the invoice is created from a sale order (not manually)
- Verify the sale order is linked to the invoice (check invoice lines → sale order field)

### "Shipping & Reports" tab not visible on invoice?
- The tab only shows on customer invoices (out_invoice, out_refund)
- It's hidden for vendor bills and other invoice types

### Reports showing wrong colors?
- Clear your browser cache
- Regenerate the report
- Check if you're using the correct report (IBIC version for invoices)

## Support & Credits
- Original module: IBIC Sale Reports
- Enhanced by: Custom development for Odoo 19
- Date: 2026
- License: LGPL-3

## Changelog

### Version 19.0.1.0.0 (Enhanced)
- Added invoice support with green theme
- Automatic data copying from sale orders
- New Shipping & Reports tab for invoices
- New invoice packing list model
- Enhanced security rules

---

**Note:** This module works alongside the existing sale order functionality. Both sale orders (blue theme) and invoices (green theme) maintain their separate reports while sharing the same core functionality.
