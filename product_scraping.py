"""gtx product scraping

Creates a window where the user can input a file and folder path.
Scrapes ebay for product information.
Takes a .csv file and for each search term in the file returns the product's price, postage, name and seller.

Author: Behnam Mozafari
Date Last Modified: 19/04/23
"""
import os
import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtGui import QIcon
from bs4 import BeautifulSoup
import requests
import pandas


class MyWindow(QMainWindow):
    """
    Class which performs all functionalities for the application.
    """

    def __init__(self):
        """
        init method for MyWindow class
        """
        super(MyWindow, self).__init__()
        self.lbl_update_loading = None
        self.folder_btn_select = None
        self.lbl_folder_path = None
        self.folder_name_lbl = None
        self.lbl_filepath = None
        self.btn_select = None
        self.lbl_loading = None
        self.btn_run = None
        self.filename_lbl = None
        self.setGeometry(1000, 250, 600, 600)
        self.setWindowTitle("eBay Scraper")
        self.setWindowIcon(QIcon("scraper_icon.jpg"))
        self.init_ui()

    def init_ui(self) -> None:
        """
        initialises ui for pop-up window
        """
        self.filename_lbl = QtWidgets.QLabel(self)
        self.filename_lbl.setText('Select keyword file:')
        self.filename_lbl.setFont(QtGui.QFont('Arial', 11))
        self.filename_lbl.adjustSize()
        self.filename_lbl.move(20, 25)

        self.lbl_filepath = QtWidgets.QLabel(self)
        self.lbl_filepath.setText(' ')
        self.lbl_filepath.setFont(QtGui.QFont('Arial', 11))
        self.lbl_filepath.adjustSize()
        self.lbl_filepath.move(20, 60)

        self.btn_select = QtWidgets.QPushButton(self)
        self.btn_select.setText('Select File')
        self.btn_select.adjustSize()
        self.btn_select.clicked.connect(self.select_file)
        self.btn_select.move(150, 20)

        self.folder_name_lbl = QtWidgets.QLabel(self)
        self.folder_name_lbl.setText('Select output folder:')
        self.folder_name_lbl.setFont(QtGui.QFont('Arial', 11))
        self.folder_name_lbl.adjustSize()
        self.folder_name_lbl.move(20, 90)

        self.lbl_folder_path = QtWidgets.QLabel(self)
        self.lbl_folder_path.setText(' ')
        self.lbl_folder_path.setFont(QtGui.QFont('Arial', 11))
        self.lbl_folder_path.adjustSize()
        self.lbl_folder_path.move(20, 125)

        self.folder_btn_select = QtWidgets.QPushButton(self)
        self.folder_btn_select.setText('Select Folder')
        self.folder_btn_select.adjustSize()
        self.folder_btn_select.clicked.connect(self.select_folder)
        self.folder_btn_select.move(150, 90)

        def run_scraper() -> None:
            """
            calls web_scraper method, performs input validation
            """
            QApplication.processEvents()
            if (len(self.lbl_filepath.text()) > 0) & (len(self.lbl_folder_path.text()) > 0):
                self.lbl_loading.setText("Processing...")
                self.lbl_loading.adjustSize()
                QApplication.processEvents()
                self.web_scraper(self.lbl_filepath.text(), self.lbl_folder_path.text())
                self.lbl_loading.setText("Done!")
            else:
                self.lbl_loading.setText("Please select an input file and output folder")
                self.lbl_loading.adjustSize()

        self.btn_run = QtWidgets.QPushButton(self)
        self.btn_run.setText('Run Scraper')
        self.btn_run.adjustSize()
        self.btn_run.clicked.connect(run_scraper)
        self.btn_run.move(20, 180)

        self.lbl_loading = QtWidgets.QLabel(self)
        self.lbl_loading.setText(" ")
        self.lbl_loading.move(20, 210)
        self.lbl_loading.adjustSize()

    def select_file(self) -> None:
        """
        creates file select dialog
        """
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setNameFilter("CSV files (*.csv)")
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.lbl_filepath.setText(file_path)
            self.lbl_filepath.adjustSize()

    def select_folder(self) -> None:
        """
        creates folder select dialog
        """
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        if file_dialog.exec_():
            folder_path = file_dialog.selectedFiles()[0]
            self.lbl_folder_path.setText(folder_path)
            self.lbl_folder_path.adjustSize()

    def web_scraper(self, search_terms_file_path: str, output_folder_path: str):
        """
        Searches eBay for terms in provided file, returns csv "scraped_data.csv" containing name, price, postage and
        seller of each product
        :param output_folder_path: path of folder to output results to
        :param search_terms_file_path: file path of csv file containing search terms.
        :return: scraped_data.csv, including name, price postage and seller of each product.
        """

        # reading search terms from csv
        chunk_size = 10000
        chunk_red = pandas.read_csv(search_terms_file_path, chunksize=chunk_size, header=None)
        search_terms_df = pandas.concat(chunk_red, ignore_index=True)
        search_terms = search_terms_df.values.flatten()
        # initialising arrays to hold scraped data
        prices = ['']*len(search_terms)
        postage = ['']*len(search_terms)
        listing_names = ['']*len(search_terms)
        sellers = ['']*len(search_terms)
        links = ['']*len(search_terms)
        exact_match = ['']*len(search_terms)
        prices2 = ['']*len(search_terms)
        postage2 = ['']*len(search_terms)
        listing_names2 = ['']*len(search_terms)
        sellers2 = ['']*len(search_terms)
        links2 = ['']*len(search_terms)
        i = 0
        # retrieving the price, postage info and name from each link
        for search_term in search_terms:
            if search_term is not None:
                # Make a GET request to the eBay search page with the search term as a parameter
                response = requests.get('https://www.ebay.com.au/sch/i.html', params={'_nkw': search_term})
                # Parse the response content with BeautifulSoup
                soup = BeautifulSoup(response.content, "html.parser")
                prices[i] = soup.select_one('ul.srp-results li span.s-item__price').get_text()
                postage[i] = soup.select_one('ul.srp-results li span.s-item__shipping.s-item__logisticsCost').get_text()
                listing_names[i] = soup.select_one('ul.srp-results li div.s-item__title').get_text()
                sellers[i] = soup.select_one('ul.srp-results li span.s-item__seller-info').get_text()
                links[i] = soup.select_one('ul.srp-results li a.s-item__link').get('href')
                try:
                    listing2 = soup.find('li', attrs={"data-view": "mi:1686|iid:2"})
                    prices2[i] = listing2.select_one("span.s-item__price").get_text()
                    postage2[i] = listing2.select_one('li span.s-item__shipping.s-item__logisticsCost').get_text()
                    listing_names2[i] = listing2.select_one('div.s-item__title').get_text()
                    sellers2[i] = listing2.select_one('span.s-item__seller-info').get_text()
                    links2[i] = listing2.select_one('a.s-item__link').get('href')
                except:
                    prices2[i] = ""
                    postage2[i] = ""
                    listing_names2[i] = search_term
                    sellers2[i] = ""
                    links2[i] = ""
                try:
                    exact_match[i] = soup.select_one('ul.srp-results li h3.srp-save-null-search__heading').get_text()
                except:
                    exact_match[i] = ""
            i += 1
            num = str(i)
            self.lbl_loading.setText("Processing: " + num)
            self.lbl_loading.adjustSize()
            QApplication.processEvents()
        # writing data to new csv
        if len(exact_match) != 0:
            scraping_output = {'listing_names1': listing_names, 'prices1': prices, 'postage1': postage,
                               'seller1': sellers, 'links1': links, 'listing_names2': listing_names2,
                               'prices2': prices2, 'postage2': postage2, 'seller2': sellers2, 'links2': links2,
                               'no_exact_match': exact_match}
        else:
            scraping_output = {'listing_names1': listing_names, 'prices1': prices, 'postage1': postage,
                               'seller1': sellers, 'links1': links, 'listing_names2': listing_names2,
                               'prices2': prices2, 'postage2': postage2, 'seller2': sellers2, 'links2': links2}
        output_df = pandas.DataFrame(scraping_output)
        output_file_path = os.path.join(output_folder_path, 'scraped_data.csv')
        output_df.to_csv(output_file_path, index=False)
        output_file_path = os.path.normpath(output_file_path)
        os.startfile(output_file_path)


def window():
    """
    Opens window
    """
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())


def main():
    window()


if __name__ == '__main__':
    main()
