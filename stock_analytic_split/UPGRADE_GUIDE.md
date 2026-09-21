# Upgrade Guide: Odoo 18 to Odoo 19

## Stock Analytic Distribution Module

This guide will help you upgrade the stock_analytic_split module from Odoo 18.0 to Odoo 19.0.

## Pre-Upgrade Checklist

- [ ] **Backup your database** completely
- [ ] **Test on development environment** first
- [ ] **Document current configuration** (analytic accounts, distributions)
- [ ] **Check dependencies** are compatible with Odoo 19
- [ ] **Review customizations** if any modifications were made to the module

## Changes from 18.0 to 19.0

### Version Numbers
- **Old**: 18.0.4.0.0
- **New**: 19.0.1.0.0

### Code Changes

#### 1. Manifest File (__manifest__.py)
```python
# Changed
'version': '18.0.4.0.0'  →  'version': '19.0.1.0.0'

# Dependencies remain the same
'depends': ['stock', 'stock_account', 'analytic', 'purchase_stock', 'mail']
```

#### 2. View Compatibility
- Updated view inheritance to be compatible with Odoo 19 UI
- Analytic distribution widget works the same way
- No changes to field names or structure

#### 3. API Changes
- All API methods remain compatible
- No deprecated methods used
- Standard Odoo 19 ORM methods

### What Stays the Same

✅ **Database Structure**
- All table structures unchanged
- Field names identical
- Data types unchanged

✅ **Functionality**
- Auto-sync from PO/SO lines works the same
- Analytic line creation logic identical
- User interface behavior unchanged

✅ **Configuration**
- Analytic accounts setup unchanged
- Distribution percentages work the same
- No new settings required

## Upgrade Steps

### Step 1: Prepare Your Environment

```bash
# 1. Backup your Odoo 18 database
pg_dump your_db_name > backup_before_upgrade.sql

# 2. Backup your addons (if customized)
cp -r /path/to/odoo/addons/stock_analytic_split /path/to/backup/

# 3. Stop Odoo service
sudo systemctl stop odoo
```

### Step 2: Upgrade Odoo to 19.0

Follow the official Odoo upgrade procedure:
- Use Odoo's upgrade service, OR
- Manually upgrade your Odoo instance to 19.0

### Step 3: Install the Upgraded Module

```bash
# 1. Remove old module files
rm -rf /path/to/odoo/addons/stock_analytic_split

# 2. Copy new module files
cp -r stock_analytic_split /path/to/odoo/addons/

# 3. Set correct ownership
chown -R odoo:odoo /path/to/odoo/addons/stock_analytic_split

# 4. Start Odoo
sudo systemctl start odoo
```

### Step 4: Update the Module in Odoo

1. **Login** to Odoo 19
2. **Activate Developer Mode**:
   - Settings → Activate Developer Mode

3. **Update Apps List**:
   - Apps → Update Apps List

4. **Upgrade the Module**:
   - Apps → Search "Stock Analytic Distribution"
   - Click "Upgrade"
   - Wait for completion

### Step 5: Verify the Upgrade

#### Test Checklist:

##### Test 1: View Access
- [ ] Navigate to Inventory → Operations → Transfers
- [ ] Open a picking
- [ ] Verify "Analytic Distribution" field is visible
- [ ] Check field is positioned correctly

##### Test 2: Auto-Sync from PO
- [ ] Create a Purchase Order
- [ ] Set analytic on PO line (e.g., Project A - 100%)
- [ ] Confirm PO
- [ ] Open the receipt
- [ ] Verify analytic auto-filled from PO
- [ ] Verify field is readonly (locked)

##### Test 3: Auto-Sync from SO
- [ ] Create a Sales Order
- [ ] Set analytic on SO line (e.g., Department B - 50%, Department C - 50%)
- [ ] Confirm SO
- [ ] Open the delivery
- [ ] Verify analytic auto-filled from SO
- [ ] Verify field is readonly (locked)

##### Test 4: Manual Entry
- [ ] Create an internal transfer
- [ ] Set analytic manually on header
- [ ] Verify it propagates to move lines
- [ ] Change analytic on individual move
- [ ] Verify changes are saved

##### Test 5: Analytic Line Creation
- [ ] Create a transfer with analytic distribution
- [ ] Validate the transfer
- [ ] Go to Accounting → Reporting → Analytic Accounts
- [ ] Find your analytic account
- [ ] Verify analytic lines were created
- [ ] Check amounts are correct (negative for costs)

##### Test 6: Existing Data
- [ ] Review transfers created in Odoo 18
- [ ] Verify existing analytic distributions are intact
- [ ] Check old analytic lines are still linked correctly

## Troubleshooting

### Issue: Module won't upgrade

**Solution:**
```bash
# Clear Odoo cache
sudo rm -rf /var/lib/odoo/.local/share/Odoo/sessions/*

# Restart Odoo
sudo systemctl restart odoo

# Try upgrade again
```

### Issue: Views not loading correctly

**Solution:**
```bash
# Update view files
cd /path/to/odoo/addons/stock_analytic_split
# Ensure all .xml files are present

# Restart with update
sudo -u odoo odoo -c /etc/odoo/odoo.conf -u stock_analytic_split -d your_db_name --stop-after-init
```

### Issue: Analytic field not showing

**Check:**
1. Analytic Accounting is enabled (Settings → Accounting → Analytic Accounting)
2. User has access rights to analytic group
3. Views are updated correctly
4. Browser cache is cleared

### Issue: Auto-sync not working

**Check:**
1. PO/SO line has analytic_distribution set
2. Receipt/delivery is linked to PO/SO (check source document field)
3. Module dependencies are all installed
4. Check server logs for errors

## Rollback Procedure

If upgrade fails and you need to rollback:

```bash
# 1. Stop Odoo
sudo systemctl stop odoo

# 2. Restore database backup
psql -d your_db_name < backup_before_upgrade.sql

# 3. Restore old module files
rm -rf /path/to/odoo/addons/stock_analytic_split
cp -r /path/to/backup/stock_analytic_split /path/to/odoo/addons/

# 4. Downgrade Odoo to 18.0 (if needed)

# 5. Start Odoo
sudo systemctl start odoo
```

## Performance Considerations

### Before Upgrade
- Document number of stock moves with analytic
- Check number of analytic lines created
- Note any performance issues

### After Upgrade
- Compare performance metrics
- If slower, check indexes:
```sql
-- Check indexes on analytic lines
SELECT * FROM pg_indexes WHERE tablename = 'account_analytic_line';

-- Should have indexes on stock_move_id and stock_picking_id
```

## Data Migration

**Good News:** No data migration needed!

The module structure is identical:
- Same field names
- Same data types
- Same relationships

Your existing data will work immediately after upgrade.

## Post-Upgrade Tasks

1. **Inform Users**:
   - Send notification about upgrade
   - Explain any UI changes (if any)
   - Provide support contact

2. **Monitor**:
   - Watch server logs for errors
   - Check analytic line creation is working
   - Verify auto-sync from PO/SO

3. **Documentation**:
   - Update internal documentation
   - Note Odoo 19 specific features
   - Document any new workflows

## Support

If you encounter issues during upgrade:

**Author**: Haytham Afify  
**Email**: haythamgamal6@gmail.com  
**GitHub**: [Issues Page](https://github.com/haythamafify)

## Upgrade Confirmation

After successful upgrade, you should see:

```
Module: Stock Analytic Distribution
Version: 19.0.1.0.0
State: Installed
```

In Apps → Stock Analytic Distribution → Technical Details

## Conclusion

The upgrade from Odoo 18 to Odoo 19 for this module is **straightforward** with:
- ✅ No breaking changes
- ✅ No data migration
- ✅ Full backward compatibility
- ✅ Same functionality

Just follow the steps above and test thoroughly!
