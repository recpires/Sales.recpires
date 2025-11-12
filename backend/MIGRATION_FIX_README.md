# Migration Fix for Render Deployment

## Problem

When deploying to Render, you may encounter this error:

```
django.db.utils.ProgrammingError: relation "sales_attribute" already exists
```

This happens when:
1. Tables already exist in the production database (from a previous deploy or manual creation)
2. Django tries to apply migration `0006_attribute_coupon_remove_product_color_and_more`
3. The migration contains `CreateModel` operations for tables that already exist
4. The `--fake-initial` flag doesn't work because the migration also contains `AddField`, `RemoveField`, and `AlterField` operations

## Solution 1: Automatic (Recommended)

The `migrate_safe.py` script has been integrated into `build.sh` to automatically:

1. Check if critical tables (`sales_attribute`, `sales_coupon`, etc.) exist
2. Check if migration 0006 has been applied
3. If tables exist but migration 0006 is not applied, it marks the migration as fake
4. Then runs normal migrations with `--fake-initial`

**This solution is automatic and requires no manual intervention.**

### How it works:

```bash
# In build.sh
python migrate_safe.py
```

The script will output detailed information about:
- Existing tables found
- Applied migrations
- Whether it needs to fake migration 0006
- Migration results

## Solution 2: Manual SQL Fix

If the automatic solution fails, you can manually mark the migration as applied:

### Step 1: Access Render Dashboard

1. Go to your Render dashboard
2. Navigate to your PostgreSQL database
3. Click "Connect" → "External Connection" or use the psql command provided

### Step 2: Run the SQL Script

Use the queries in `fix_migrations_manual.sql`:

```sql
-- First, verify tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('sales_attribute', 'sales_coupon', 'sales_category');

-- Check applied migrations
SELECT id, app, name, applied
FROM django_migrations
WHERE app = 'sales'
ORDER BY id DESC;

-- If tables exist but 0006 is not in the list, run this:
INSERT INTO django_migrations (app, name, applied)
VALUES ('sales', '0006_attribute_coupon_remove_product_color_and_more', NOW())
ON CONFLICT DO NOTHING;
```

### Step 3: Redeploy

After manually adding the migration record, trigger a new deploy on Render.

## Solution 3: Nuclear Option (Last Resort)

⚠️ **WARNING: This will delete all data!**

If nothing else works, you can reset the database:

1. In Render dashboard, go to your database
2. Delete the database
3. Create a new database with the same name
4. Update your web service environment variables if needed
5. Trigger a new deploy

This ensures a clean slate but **all existing data will be lost**.

## Prevention

To prevent this issue in the future:

1. **Always commit migrations to git** before deploying
2. **Never manually create tables** in production
3. **Use migrations for all schema changes**
4. **Keep local, staging, and production in sync**

## Testing Locally

To test the migration fix script locally:

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the migration script
python migrate_safe.py
```

You should see output like:

```
======================================================================
SAFE MIGRATION SCRIPT
======================================================================

Existing tables found: 5
  ✓ sales_attribute
  ✓ sales_coupon
  ✓ sales_category
  ✓ sales_attributevalue
  ✓ sales_productvariant

Applied migrations: 6
  ✓ sales.0001_initial
  ✓ sales.0002_product_color_product_size
  ✓ sales.0003_product_image
  ✓ sales.0004_store_order_store_product_store
  ✓ sales.0005_alter_product_sku_productvariant_orderitem_variant

======================================================================
Running migrations...
======================================================================

Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sales, sessions
Running migrations:
  No migrations to apply.

✓ Migrations completed successfully!
```

## Troubleshooting

### Script fails with "module not found"

Make sure Django is installed:
```bash
pip install -r requirements.txt
```

### Script can't connect to database

Check your `.env` file has correct database credentials:
```
DB_NAME=sales_db
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=localhost
DB_PORT=5432
```

### Still getting "relation already exists" error

This means the automatic script didn't catch it. Use Solution 2 (Manual SQL Fix).

## Questions?

If you encounter issues not covered here, check:
1. Render deployment logs for detailed error messages
2. Django migration state: `python manage.py showmigrations`
3. Database tables: Connect to DB and run `\dt` in psql

---

**Last updated:** 2025-11-04
