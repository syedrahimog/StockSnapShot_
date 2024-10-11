import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import Qt
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

        # First column: Stock selection
        stock_column = QVBoxLayout()
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
        for period in ["1d", "5d", "10d"]:
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
            series.append(index.timestamp() * 1000, row['Close'])

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"{self.current_stock} - {self.current_period}")
        chart.createDefaultAxes()
        self.chart_view.setChart(chart)

    def update_analysis(self):
        stock_data = yf.download(self.current_stock, period="6mo")
        
        # Calculate 10-day and 30-day moving averages
        ma10 = stock_data['Close'].rolling(window=10).mean().iloc[-1]
        ma30 = stock_data['Close'].rolling(window=30).mean().iloc[-1]
        
        if ma10 > ma30:
            prediction = "The stock is likely to increase based on moving averages."
        else:
            prediction = "The stock is likely to decrease based on moving averages."
        
        self.analysis_text.setText(prediction)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockApp()
    window.show()
    sys.exit(app.exec_())
