# 🚀 How to Run the Hackathon Expense Management Module

## 🎯 **QUICKEST WAY - Web Demo (Ready to Run!)**

### 1. **Run the Interactive Web Demo** (RECOMMENDED)
```bash
cd D:\EXP_Tra
python web_demo.py
```

Then open your browser and go to: **http://localhost:5000**

This gives you a **beautiful web interface** showing all features:
- ✅ Create expenses with multi-currency support
- ✅ OCR receipt processing demo
- ✅ Approval workflow simulation
- ✅ Real-time statistics
- ✅ Modern responsive UI

### 2. **Run the Command Line Demo**
```bash
cd D:\EXP_Tra
python demo_app.py
```
Choose option 1 for automated demo or 2 for interactive.

---

## 🏗️ **FULL ODOO INSTALLATION (For Production)**

### Option A: Using Odoo.sh (Cloud - Easiest)
1. Go to https://www.odoo.com/trial
2. Sign up for free trial (14 days)
3. Create ZIP file of our module:
   ```bash
   cd D:\EXP_Tra
   powershell Compress-Archive -Path hackathon_expense_management -DestinationPath hackathon_expense_management.zip
   ```
4. Upload the ZIP file to Odoo.sh
5. Install the module from Apps menu

### Option B: Docker Installation (Recommended for Local)
**Prerequisites:** Install Docker Desktop from https://www.docker.com/products/docker-desktop/

```bash
cd D:\EXP_Tra
docker-compose up
```

Then:
1. Go to http://localhost:8069
2. Create database with:
   - Database name: `hackathon_expense_db`
   - Admin password: `admin123`
3. Install "Hackathon Expense Management" from Apps

### Option C: Manual Windows Installation
1. **Install PostgreSQL**
   - Download: https://www.postgresql.org/download/windows/
   - Default settings, remember your password

2. **Download Odoo**
   - Get the Windows installer: https://nightly.odoo.com/17.0/nightly/exe/
   - Install with default settings

3. **Install the Module**
   ```bash
   # Copy module to Odoo addons directory
   xcopy /E /I hackathon_expense_management "C:\Program Files\Odoo 17.0\server\odoo\addons\hackathon_expense_management"
   ```

4. **Configure Odoo** (odoo.conf)
   ```ini
   [options]
   addons_path = C:\Program Files\Odoo 17.0\server\odoo\addons,D:\EXP_Tra
   admin_passwd = admin123
   ```

---

## 🎮 **WHAT YOU CAN DO IN THE DEMOS**

### Web Demo Features:
- **Create Expenses**: Test multi-currency with real-time conversion
- **OCR Testing**: Paste receipt text and see data extraction
- **Approval Flow**: Submit and approve expenses
- **Real-time Stats**: See live updates of totals and statuses
- **Responsive Design**: Works on mobile and desktop

### Command Demo Features:
- **Interactive Mode**: Step-by-step expense creation
- **Automated Demo**: See all features in action automatically
- **OCR Processing**: Test receipt text parsing
- **Workflow Simulation**: Complete approval cycle

---

## 📊 **DEMO SCENARIOS TO TRY**

### 1. **Multi-Currency Test**
- Create expense with EUR 500
- Watch it convert to USD automatically
- Try different currencies (GBP, INR, JPY)

### 2. **OCR Receipt Test**
Paste this sample receipt:
```
STARBUCKS COFFEE
Store #12345
123 Main St, City

Date: 10/04/2024
Time: 14:30

Grande Latte        $5.45
Blueberry Muffin    $3.25
-------------------------
Subtotal            $8.70
Tax                 $0.70
Total              $9.40

Thank you for visiting!
```

### 3. **Approval Workflow Test**
1. Create expense as "john.employee"
2. Add "jane.manager" as approver
3. Submit for approval
4. Approve as "jane.manager"
5. Watch status change to "Approved"

---

## 🔧 **TROUBLESHOOTING**

### Web Demo Issues:
```bash
# If Flask error
pip install flask

# If requests error  
pip install requests

# If OCR issues (optional)
pip install pytesseract Pillow
```

### Odoo Installation Issues:
- **PostgreSQL Connection**: Ensure PostgreSQL is running
- **Module Not Visible**: Check addons path in odoo.conf
- **Permission Errors**: Run as Administrator
- **Port Conflicts**: Change port in docker-compose.yml

### Demo Data Reset:
- Restart web demo: `Ctrl+C` then `python web_demo.py`
- Command demo: Run `python demo_app.py` again

---

## 📱 **ACCESS URLS**

- **Web Demo**: http://localhost:5000
- **Odoo (Docker)**: http://localhost:8069
- **Odoo (Windows)**: http://localhost:8069

---

## 🎯 **WHAT TO SHOW JUDGES**

1. **Start with Web Demo** - Most visual and impressive
2. **Show Multi-Currency** - Real API integration
3. **Demonstrate OCR** - Paste a receipt and watch magic
4. **Show Workflow** - Create → Submit → Approve cycle
5. **Highlight Statistics** - Real-time updates
6. **Mobile Responsive** - Works on all devices

## 📋 **QUICK COMMANDS**

```bash
# Web demo (recommended)
cd D:\EXP_Tra && python web_demo.py

# Command demo
cd D:\EXP_Tra && python demo_app.py

# Full Odoo with Docker (if Docker installed)
cd D:\EXP_Tra && docker-compose up

# Create module ZIP for upload
powershell Compress-Archive -Path hackathon_expense_management -DestinationPath hackathon_expense_management.zip
```

---

## 🏆 **HACKATHON PRESENTATION TIPS**

1. **Start with the problem**: "Managing expenses is complex and manual"
2. **Show the solution**: "Our Odoo module automates everything"
3. **Demo the features**: Use web demo for visual impact
4. **Highlight innovation**: OCR, multi-currency, smart workflows
5. **Show the code**: Professional Odoo development patterns

**Your module is ready for the hackathon! 🎉**