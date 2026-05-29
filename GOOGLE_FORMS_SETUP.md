# Google Forms / Google Sheets Integration Setup

This guide explains how to set up Google Forms integration for order intake.

## Overview

1. Create a Google Form for customers to order
2. Link it to a Google Sheet
3. Configure the app to read from that sheet
4. Sync orders on demand

---

## Step 1: Create a Google Form

### Recommended Form Fields

Create a Google Form with these fields (in order):

| Question | Type | Required |
|----------|------|----------|
| Your Name | Short answer | Yes |
| Mobile Number | Short answer | Yes |
| Select Product | Dropdown or Multiple choice | Yes |
| Quantity | Dropdown (1-10) or Short answer | Yes |
| Apartment/Building | Short answer | No |
| Block/Tower | Short answer | No |
| Special Instructions | Paragraph | No |

### Sample Form for Mango Pickle Orders

**Title:** Mango Pickle Order Form - Soups, Snacks & More

**Description:** Order our homemade mango pickle! Orders received by Sunday will be delivered next week.

**Questions:**
1. **Your Name** (Short answer, Required)
2. **WhatsApp/Mobile Number** (Short answer, Required)
   - Description: "For delivery coordination"
3. **Which pickle would you like?** (Dropdown, Required)
   - Options: Mango Pickle 250g, Mango Pickle 500g, Mixed Pickle 250g
4. **Quantity** (Dropdown, Required)
   - Options: 1, 2, 3, 4, 5
5. **Apartment Name** (Short answer, Optional)
6. **Block/Tower** (Short answer, Optional)
7. **Any special instructions?** (Paragraph, Optional)

---

## Step 2: Link to Google Sheets

1. Open your Google Form
2. Click the **Responses** tab
3. Click the green **Sheets icon** (Create Spreadsheet)
4. Choose "Create a new spreadsheet"
5. Note the spreadsheet name and open it

The sheet will have columns:
- **A**: Timestamp
- **B**: Your Name
- **C**: Mobile Number
- **D**: Product selection
- **E**: Quantity
- **F**: Apartment
- **G**: Block
- **H**: Special instructions

---

## Step 3: Set Up Google Cloud Service Account

### Create a Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the **Google Sheets API**:
   - Go to APIs & Services → Library
   - Search for "Google Sheets API"
   - Click Enable
4. Create a Service Account:
   - Go to APIs & Services → Credentials
   - Click "Create Credentials" → "Service Account"
   - Name it (e.g., "soupssnacks-sheets")
   - Click Create and Continue
   - Skip roles (not needed for Sheets access)
   - Click Done
5. Create a key:
   - Click on the service account you created
   - Go to "Keys" tab
   - Add Key → Create new key → JSON
   - Download the JSON file

### Install the Key

**Option A: File-based (recommended for local)**
1. Rename the downloaded file to `google_credentials.json`
2. Place it in the SoupsSnacks project root folder

**Option B: Environment variable (recommended for production)**
```bash
export GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'
```

### Share Your Sheet

1. Open your Google Sheet
2. Click "Share" button
3. Add the service account email (found in the JSON file: `client_email`)
4. Give it "Editor" permission (needed for write-back)
5. Click Send

---

## Step 4: Install Python Dependencies

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

Or add to requirements.txt:
```
google-auth
google-auth-oauthlib
google-api-python-client
```

---

## Step 5: Configure in the App

1. Login as admin
2. Go to **📊 Google Sync** in the sidebar
3. Click **Add Configuration**
4. Fill in:
   - **Name**: "Mango Pickle Orders" (or your form name)
   - **Sheet ID**: Copy from the sheet URL (the long string between /d/ and /edit)
   - **Tab Name**: "Form Responses 1" (default for form responses)
5. Click **Test Connection** to verify access
6. Map the columns:
   - Order Date: A (timestamp)
   - Customer Name: B
   - Mobile: C
   - Product: D
   - Quantity: E
   - Apartment: F
7. Set a default product (optional, for simple forms)
8. Click **Create**

---

## Step 6: Sync Orders

1. Wait for form responses (or submit test responses)
2. Go to **📊 Google Sync**
3. Click **🔄 Sync Now** on your configuration
4. View results:
   - Rows processed
   - Orders created
   - Rows skipped (duplicates)
   - Errors (if any)

---

## Column Mapping Reference

| App Field | Description | Example Column |
|-----------|-------------|----------------|
| `order_date` | When the order was placed | A (Timestamp) |
| `customer_name` | Customer's name | B |
| `mobile` | Phone number (required) | C |
| `product_name` | Product selection | D |
| `quantity` | Number of items | E |
| `apartment` | Apartment/building name | F |
| `block` | Block/tower | G |
| `notes` | Special instructions | H |

---

## Write-Back Feature (Optional)

Enable write-back to update the Google Sheet with order status:

1. Add two empty columns to your sheet (e.g., I and J)
2. Label them "Order Number" and "Status"
3. In the app configuration:
   - Check "Enable write-back"
   - Order Number Column: I
   - Status Column: J

After syncing, the sheet will show the internal order number and status for each row.

---

## Duplicate Prevention

The app tracks which rows have been synced using:
- Row number
- Hash of row content

This means:
- Running sync multiple times won't create duplicate orders
- Changed rows will not be re-imported (by design - changes should be made in the app)

---

## Troubleshooting

### "Google credentials not found"
- Ensure `google_credentials.json` exists in the project root
- Or set `GOOGLE_CREDENTIALS_JSON` environment variable

### "Permission denied" on sheet
- Share the sheet with the service account email
- Give "Editor" permission for write-back

### "Sheet not found"
- Check the Sheet ID is correct (from URL)
- Check the Tab Name matches exactly (case-sensitive)

### "Invalid mobile number"
- Ensure mobile column has valid numbers
- Check for spaces or special characters

### "Product not found"
- Either set a default product in configuration
- Or ensure the product name in the sheet matches a product in the app

---

## Sample Test Data

To test, submit these responses to your form:

| Name | Mobile | Product | Qty | Apartment |
|------|--------|---------|-----|-----------|
| Test User 1 | 9876543210 | Mango Pickle 250g | 2 | Prestige Lakeside |
| Test User 2 | 9876543211 | Mango Pickle 500g | 1 | Brigade Gateway |
| Test User 3 | 9876543212 | Mixed Pickle 250g | 3 | Sobha Dream Acres |

Then sync in the app and verify orders were created.
