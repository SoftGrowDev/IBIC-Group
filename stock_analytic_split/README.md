# Stock Analytic Distribution - Odoo 19

## Overview
Bring the power of analytic accounting directly to your stock transfers. Split costs across multiple analytic accounts — the same way you do on invoices. Now with **auto-sync from Purchase Orders and Sales Orders**.

## Version
**19.0.1.0.0** - Upgraded from Odoo 18.0.4.0.0

## Key Features

### 🎯 Analytic Widget on Move Lines
The native `analytic_distribution` widget appears on every product line in your transfer form — exactly like invoice lines.

### 🔄 Auto-Sync from PO / SO Lines
Each stock move inherits the analytic from the matching PO or SO line automatically. Field is locked when linked to a source document.

### ✏️ Manual Entry for Standalone Transfers
Internal transfers and receipts with no PO/SO remain fully editable — set cost center manually per line or via the header field.

### ✅ Auto Analytic Lines on Validate
When you validate a transfer, analytic lines are automatically created for each distribution percentage on every done move.

### 🔗 Full Stock Traceability
Analytic lines are linked back to `stock.move` and `stock.picking` for full operational traceability.

### 🌍 Multi-Plan Support
Supports multiple analytic plans and percentage splits simultaneously.

## How It Works

1. **Set Analytic on PO/SO Line** — In your Purchase Order or Sales Order, set the Analytic Distribution on each product line (requires Analytic Accounting enabled in Settings).
2. **Confirm the Order** — Odoo creates the linked receipt or delivery automatically.
3. **Analytic Auto-Applied** — Open the receipt/delivery and find the analytic already filled from the source document. Field is locked.
4. **Validate** — Click Validate. Analytic lines are created automatically per distribution.
5. **Standalone Transfers** — For transfers without PO/SO, set the analytic manually on the header or per line and validate normally.

## Installation

1. **Extract the module** to your Odoo addons directory:
   ```bash
   cp -r stock_analytic_split /path/to/odoo/addons/
   ```

2. **Update the apps list** in Odoo:
   - Go to Apps menu
   - Click "Update Apps List"
   - Search for "Stock Analytic Distribution"

3. **Install the module**:
   - Click Install

## Configuration

1. **Enable Analytic Accounting**:
   - Go to Accounting → Configuration → Settings
   - Enable "Analytic Accounting"

2. **Create Analytic Accounts**:
   - Go to Accounting → Configuration → Analytic Accounts
   - Create your cost centers, projects, or departments

3. **Set Analytic on PO/SO**:
   - On Purchase Order or Sales Order lines, set the Analytic Distribution
   - The distribution will automatically flow to stock moves

## Upgrade Notes from Odoo 18

### Changes in Odoo 19 Version:
- ✅ Updated to Odoo 19.0 API
- ✅ Compatible with Odoo 19 stock and analytic modules
- ✅ Updated view inheritance for Odoo 19 UI changes
- ✅ Ensured compatibility with Odoo 19's analytic distribution widget
- ✅ No breaking changes - fully backward compatible with existing data

### Migration Steps:
1. **Backup your database** before upgrading
2. **Update the module files** with the Odoo 19 version
3. **Update the module** in Odoo:
   - Go to Apps
   - Find "Stock Analytic Distribution"
   - Click "Upgrade"
4. **Test thoroughly** on a development environment first

### Data Migration:
- No data migration required
- All existing analytic distributions on stock moves/pickings will continue to work
- Existing analytic lines linked to stock moves remain intact

## Dependencies

- **stock** - Inventory Management
- **stock_account** - Stock Accounting
- **analytic** - Analytic Accounting
- **purchase_stock** - Purchase and Stock Integration
- **mail** - Discuss (for tracking)

## Technical Details

### Auto-Sync Logic:
- Uses `stock.move.purchase_line_id` and `stock.move.sale_line_id` to match move → order line
- Works safely with or without `sale_stock` module installed
- `sale_id` is checked dynamically

### Data Storage:
- Header analytic stored as **JSON** in `stock.picking.analytic_distribution`
- Per-line analytic uses `stock.move.analytic_distribution`
- Analytic lines link to stock via `stock_move_id` and `stock_picking_id`

### Cost Calculation:
- Cost source uses `stock_valuation_layer_ids.value`
- Falls back to `standard_price × qty` if no valuation layers exist

### Analytic Line Creation:
- Created on `button_validate()`
- Only for moves in 'done' state
- Amount is negative (cost)
- Category is 'other'

## Usage Examples

### Example 1: Purchase Order with Project Tracking
```
PO Line: Product A, Qty 100, Analytic: Project X (100%)
→ Receipt created automatically
→ Stock move has analytic: Project X (100%) [LOCKED]
→ Validate receipt
→ Analytic line created: Project X, Amount: -$1,000
```

### Example 2: Split Cost Between Departments
```
PO Line: Product B, Qty 50, Analytic: Dept A (60%), Dept B (40%)
→ Receipt created
→ Stock move has analytic: Dept A (60%), Dept B (40%) [LOCKED]
→ Validate
→ Analytic lines: 
   - Dept A: -$600
   - Dept B: -$400
```

### Example 3: Manual Transfer (No PO/SO)
```
Internal Transfer: Product C, Qty 20
→ Set analytic manually on picking header: Project Y (100%)
→ Analytic propagates to all moves
→ Or set per-line: different analytic for each product
→ Validate
→ Analytic lines created
```

## Troubleshooting

### Analytic field is locked
- **Cause**: Stock move is linked to PO or SO line
- **Solution**: This is intentional to maintain data integrity. Edit the analytic on the source PO/SO line instead.

### Analytic not auto-filling from PO
- **Check**: Analytic Accounting is enabled in Accounting Settings
- **Check**: PO line has analytic_distribution set
- **Check**: Receipt is actually linked to the PO (check reference field)

### Analytic lines not created on validate
- **Check**: Move has analytic_distribution set
- **Check**: Move is in 'done' state after validation
- **Check**: Product has a cost (standard_price > 0 or valuation layers exist)

### View errors after upgrade
- **Solution**: Update apps list and restart Odoo server
- **Solution**: Clear browser cache

## Support & Contact

**Author**: Haytham Afify  
**Email**: haythamgamal6@gmail.com  
**GitHub**: [github.com/haythamafify](https://github.com/haythamafify)  
**LinkedIn**: [LinkedIn Profile](https://www.linkedin.com/in/haythamafify)

## License

LGPL-3

## Changelog

### Version 19.0.1.0.0 (2026)
- Upgraded to Odoo 19
- Updated API compatibility
- Ensured compatibility with Odoo 19 analytic distribution widget
- No breaking changes

### Version 18.0.4.0.0 (Previous)
- Auto-sync analytic from PO/SO lines to stock moves
- Field locked when linked to source document
- Safe detection of sale_stock module
- Header-level Default Analytic field
- Per-line analytic distribution widget
- Auto analytic line creation on validate
- Arabic translation

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Credits

- Haytham Afify - Original author and maintainer
- Odoo Community - For the amazing platform
