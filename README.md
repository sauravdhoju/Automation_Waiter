# Automation Waiter Setup Guide

## 🚀 Steps to Run the Project

1. **Clone the Repository**
   ```bash
   git clone git@github.com:sauravdhoju/Automation_Waiter.git
   cd Automation_Waiter
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv env
   source env/bin/activate   # For Linux/Mac
   # OR
   env\Scripts\activate      # For Windows
   ```

3. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright (only the first time)**
   ```bash
   playwright install
   ```

5. **Edit Input Files**
   - Open and edit the following text files:
     - `menu_list.txt`
     - `category_list.txt`

6. **Run Scripts**
   ```bash
   python menu.py
   python category.py
   ```

---

## 📄 Data Format Guide

### Category Sample
**Columns:**  
`Category Name, Cost Center`

### Menu Sample
**Columns:**  
`Unit, Category Name, Item Name, Price, Description`

**Rules:**
- Use a single comma to separate each field.  
- No extra commas between fields.  
- Commas are allowed **inside Description only**.  
- Description can be **left blank**.

**Examples:**

`Piece, Beverages, Coffee, 120, Freshly brewed with milk and sugar`  
`Piece, Beverages, Coffee, 120,`
