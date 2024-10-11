import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLineEdit
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PyQt5.QtCore import Qt, QDateTime
import yfinance as yf
import pandas as pd

class StockApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Snapshot")
        self.setGeometry(100, 100, 1200, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # First column: Stock selection and search
        stock_column = QVBoxLayout()
        
        # Add search box and button
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter stock symbol")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_stock)
        search_layout.addWidget(self.search_box)
        search_layout.addWidget(search_button)
        stock_column.addLayout(search_layout)

        # Add predefined stock buttons
        stocks = ["AAPL", "INTC", "NVDA", "TSLA", "GOOG", "AMZN", "META", "TSM", "AVGO", "XOM"]
        for stock in stocks:
            btn = QPushButton(stock)
            btn.clicked.connect(lambda checked, s=stock: self.update_stock(s))
            stock_column.addWidget(btn)
        main_layout.addLayout(stock_column)

        # Second column: Chart
        chart_column = QVBoxLayout()
        self.chart_view = QChartView()
        chart_column.addWidget(self.chart_view)
        
        time_buttons = QHBoxLayout()
        for period in ["1d", "5d", "1mo"]:  # Changed "10d" to "1m"
            btn = QPushButton(period)
            btn.clicked.connect(lambda checked, p=period: self.update_chart_period(p))
            time_buttons.addWidget(btn)
        chart_column.addLayout(time_buttons)
        
        main_layout.addLayout(chart_column)

        # Third column: Analysis
        analysis_column = QVBoxLayout()
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        analysis_column.addWidget(self.analysis_text)
        main_layout.addLayout(analysis_column)

        self.current_stock = "AAPL"
        self.current_period = "1d"
        self.update_stock(self.current_stock)

    def update_stock(self, stock):
        self.current_stock = stock
        self.update_chart()
        self.update_analysis()

    def update_chart_period(self, period):
        self.current_period = period
        self.update_chart()

    def update_chart(self):
        stock_data = yf.download(self.current_stock, period=self.current_period, interval="5m")
        
        series = QLineSeries()
        for index, row in stock_data.iterrows():
            date_time = QDateTime()
            date_time.setSecsSinceEpoch(int(index.timestamp()))
            series.append(date_time.toMSecsSinceEpoch(), row['Close'])

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"{self.current_stock} - {self.current_period}")

        # Create and set up the X-axis (date/time)
        axis_x = QDateTimeAxis()
        axis_x.setFormat("MM-dd HH:mm")
        axis_x.setTickCount(5)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        # Create and set up the Y-axis (stock price)
        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        self.chart_view.setChart(chart)

    def update_analysis(self):
        stock_data = yf.download(self.current_stock, period="6mo")
        
        # Calculate 10-day and 30-day moving averages
        ma10 = stock_data['Close'].rolling(window=10).mean().iloc[-1]
        ma30 = stock_data['Close'].rolling(window=30).mean().iloc[-1]
        
        if ma10 > ma30:
            prediction = f"{self.current_stock} is likely to INCREASE based on moving averages. The ma10 is {ma10:.2f} and the ma30 is {ma30:.2f}."
        else:
            prediction = f"{self.current_stock} is likely to DECREASE based on moving averages. The ma10 is {ma10:.2f} and the ma30 is {ma30:.2f}."
        
        self.analysis_text.setText(prediction)

    def search_stock(self):
        stock_symbol = self.search_box.text().upper()
        if stock_symbol:
            self.update_stock(stock_symbol)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockApp()
    window.show()
    sys.exit(app.exec_())
