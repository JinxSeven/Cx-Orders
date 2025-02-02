import sqlite3
import uuid
from src.config import DB_PATH
from src.utils.color import Color
from src.utils.services import Services

class ProductHandler:
    def __init__(self, ui):
        self.ui = ui
        self.services = Services()
        
        self.services.load_combobox(self.ui.prodModNameSel, "SELECT product_name FROM product_data")
        self.load_product_details()
        
        self.ui.prodAddBtn.clicked.connect(self.add_new_product)
        self.ui.prodModDeleteBtn.clicked.connect(self.delete_product)
        self.ui.prodModResetBtn.clicked.connect(self.reset_changes)
        self.ui.prodModUpdateBtn.clicked.connect(self.update_product)
        
        self.ui.prodModNameSel.currentIndexChanged.connect(self.load_product_details)

    def load_product_details(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            selected_name = self.ui.prodModNameSel.currentText()
            cursor = conn.execute("SELECT * FROM product_data WHERE product_name=?", (selected_name,))
            result = cursor.fetchone()
            if result:
                self.ui.prodModIdInp.setText(str(result[0]))
                self.ui.prodModCostPriceInp.setText(str(result[2]))
                self.ui.prodModSellingPriceInp.setText(str(result[3]))
                self.ui.prodModQuantityInp.setText(str(result[4]))
            conn.close()
            # print(selected_name, result)
        except Exception as ex:
            print(Color.RED + f"An error occurred while adding product: {ex}" + Color.RED)
    
    def add_new_product(self):
        try:
            name = self.ui.prodAddNameInp.text()
            cp = float(self.ui.prodAddCostPriceInp.text())
            sp = float(self.ui.prodAddSellingPriceInp.text())
            quantity = int(self.ui.prodAddQuantityInp.text())
            id = str(uuid.uuid4())
        except ValueError:
            self.ui.prodModPosInfoLbl.clear()
            self.services.display_info(self.ui.prodModNegInfoLbl, 'Input type mismatch, adding failed!')
            return
        
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT INTO product_data (product_id, product_name, cost_price, selling_price, quantity) VALUES (?, ?, ?, ?, ?)",
                (id, name, cp, sp, quantity)
            )
            conn.commit()
            conn.close()
            
            self.ui.prodModNegInfoLbl.clear()
            self.services.display_info(self.ui.prodModPosInfoLbl, 'Product added successfully!')
            self.services.load_combobox(self.ui.prodModNameSel, "SELECT product_name FROM product_data")
        except sqlite3.Error as ex:
            self.ui.prodModPosInfoLbl.clear()
            self.services.display_info(self.ui.prodModNegInfoLbl, 'Product might already exist!')
            print(Color.RED + f"An error occurred while adding product: {ex}" + Color.RED)
            return
        finally:
            self.ui.prodAddNameInp.clear()
            self.ui.prodAddCostPriceInp.clear()
            self.ui.prodAddSellingPriceInp.clear()
            self.ui.prodAddQuantityInp.clear()

    def delete_product(self):
        id = self.ui.prodModIdInp.text()
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.execute("SELECT product_name FROM product_data WHERE product_id = ?", (id,))
                name = cursor.fetchone()
        except sqlite3.Error as ex:
            print(Color.RED + f"An error occurred while fetching data: {ex}")
        proceed = self.services.confirmation_messagebox("Product Mod", f"Do you want to proceed deleting {name[0]}?")
        if not proceed:
            return
        
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("DELETE FROM product_data WHERE product_id=?", (id,))
                conn.commit()
                
            self.ui.prodModPosInfoLbl.clear()
            self.services.display_info(self.ui.prodModNegInfoLbl, 'Product deleted successfully!')
            self.services.load_combobox(self.ui.prodModNameSel, "SELECT product_name FROM product_data")
        except sqlite3.Error as ex:
            print(Color.RED + f"An error occurred while deleting product: {ex}")
            self.ui.prodModPosInfoLbl.clear()
            self.services.display_info(self.ui.prodModNegInfoLbl, 'Could not delete product')
    
    def update_product(self):
        try:
            id = self.ui.prodModIdInp.text()
            name = self.ui.prodModNameSel.currentText()
            cp = float(self.ui.prodModCostPriceInp.text())
            sp = float(self.ui.prodModSellingPriceInp.text())
            quantity = int(self.ui.prodModQuantityInp.text())
        except ValueError:
            self.ui.prodModPosInfoLbl.clear()
            self.services.display_info(self.ui.prodModNegInfoLbl, 'Input type mismatch, update failed!')
            return
        
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("""
                    UPDATE product_data SET 
                    product_name=?, cost_price=?,
                    selling_price=?, quantity=?
                    WHERE product_id=?
                """, (name, cp, sp, quantity, id))
                conn.commit()
                prod_index = self.ui.prodModNameSel.currentIndex()
                self.ui.prodModNameSel.removeItem(prod_index)
                self.ui.prodModNameSel.insertItem(prod_index, name)
                self.ui.prodModNameSel.setCurrentIndex(prod_index)
                
                self.ui.prodModNegInfoLbl.clear()
                self.services.display_info(self.ui.prodModPosInfoLbl, 'Product updated successfully!')
                # self.services.load_combobox(self.ui.prodModNameSel, "SELECT product_name FROM product_data")
        except sqlite3.Error as ex:
            print(Color.RED + f"An error occurred while updating product: {ex}")
            self.ui.prodModPosInfoLbl.clear()
            self.services.display_info(self.ui.prodModNegInfoLbl, 'Could not update product!')
        except Exception as ex:
            print(Color.RED + f"An error occurred while updating product: {ex}")
    
    def reset_changes(self):
        id = self.ui.prodModIdInp.text()
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.execute("SELECT * FROM product_data WHERE product_id = ?", (id,))
                result = cursor.fetchone()
        except sqlite3.Error as ex:
            print(Color.RED + f"An error occurred while fetching data: {ex}")
        proceed = self.services.confirmation_messagebox("Product Mod", f"Do you want to reset temporary changes made towards {str(result[1])}?")
        if not proceed:
            return

        if result:
            self.ui.prodModNameSel.setCurrentText(str(result[1]))
            self.ui.prodModCostPriceInp.setText(str(result[2]))
            self.ui.prodModSellingPriceInp.setText(str(result[3]))
            self.ui.prodModQuantityInp.setText(str(result[4]))
    