import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLineEdit, QTabWidget
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis, QBarSeries, QBarSet
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QColor
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

class StockApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Snapshot")
        self.setGeometry(100, 100, 1200, 600)

        # Define the button style
        self.button_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 10px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                margin: 2px 1px;
                border-radius: 4px;
                min-width: 80px;
                max-width: 80px;
                min-height: 30px;
                max-height: 30px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """

        # Define the search box style
        self.search_box_style = """
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
                min-width: 120px;
                max-width: 120px;
                min-height: 20px;
                max-height: 20px;
            }
        """

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create a tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create the main stock tab
        stock_tab = QWidget()
        self.tab_widget.addTab(stock_tab, "Stock Analysis")

        stock_layout = QVBoxLayout(stock_tab)

        # Add search box and button at the top
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter symbol")
        self.search_box.setStyleSheet(self.search_box_style)
        search_button = QPushButton("Search")
        search_button.setStyleSheet(self.button_style)
        search_button.clicked.connect(self.search_stock)
        search_layout.addWidget(self.search_box)
        search_layout.addWidget(search_button)
        search_layout.addStretch(1)  # Push search box and button to the left
        stock_layout.addLayout(search_layout)

        # Create a layout for the three columns
        columns_layout = QHBoxLayout()
        stock_layout.addLayout(columns_layout)

        # First column: Stock list
        stock_list_column = QVBoxLayout()
        stock_widget = QWidget()
        stock_widget.setLayout(stock_list_column)
        stock_widget.setFixedWidth(150)  # Set a fixed width for the first column
        
        # Add predefined stock buttons
        stocks = ["AAPL", "INTC", "NVDA", "TSLA", "GOOG", "AMZN", "META", "TSM", "AVGO", "XOM"]
        for stock in stocks:
            btn = QPushButton(stock)
            btn.setStyleSheet(self.button_style)
            btn.clicked.connect(lambda checked, s=stock: self.update_stock(s))
            stock_list_column.addWidget(btn)
        columns_layout.addWidget(stock_widget)

        # Second column: Chart
        chart_column = QVBoxLayout()
        self.chart_view = QChartView()
        chart_column.addWidget(self.chart_view)
        
        time_buttons = QHBoxLayout()
        for period in ["1d", "5d", "1mo"]:
            btn = QPushButton(period)
            btn.setStyleSheet(self.button_style)
            btn.clicked.connect(lambda checked, p=period: self.update_chart_period(p))
            time_buttons.addWidget(btn)
        chart_column.addLayout(time_buttons)
        
        columns_layout.addLayout(chart_column)

        # Third column: Analysis
        analysis_column = QVBoxLayout()
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        analysis_column.addWidget(self.analysis_text)
        columns_layout.addLayout(analysis_column)

        # Create the market indices tab
        indices_tab = QWidget()
        self.tab_widget.addTab(indices_tab, "Market Indices")

        indices_layout = QVBoxLayout(indices_tab)
        
        # Create chart views for S&P 500, DOW, and NASDAQ
        self.sp500_chart_view = QChartView()
        self.dow_chart_view = QChartView()
        self.nasdaq_chart_view = QChartView()

        indices_layout.addWidget(self.sp500_chart_view)
        indices_layout.addWidget(self.dow_chart_view)
        indices_layout.addWidget(self.nasdaq_chart_view)
        
        # Add time period buttons at the bottom
        time_buttons_layout = QHBoxLayout()
        for period in ["1d", "5d", "1mo"]:
            btn = QPushButton(period)
            btn.setStyleSheet(self.button_style)
            btn.clicked.connect(lambda checked, p=period: self.update_indices_charts(p))
            time_buttons_layout.addWidget(btn)
        indices_layout.addLayout(time_buttons_layout)

        self.current_stock = "AAPL"
        self.current_period = "1d"
        self.update_stock(self.current_stock)
        self.update_indices_charts("1d")  # Default to 1 day view

    def update_stock(self, stock):
        self.current_stock = stock
        self.update_chart()
        self.update_analysis()

    def update_chart_period(self, period):
        self.current_period = period
        self.update_chart()

    def update_chart(self):
        stock_data = yf.download(self.current_stock, period=self.current_period, interval="5m")
        
        # Price series
        price_series = QLineSeries()
        # Volume series
        volume_series = QBarSeries()
        volume_set = QBarSet("")  # Remove the "Volume" label
        
        for index, row in stock_data.iterrows():
            date_time = QDateTime()
            date_time.setSecsSinceEpoch(int(index.timestamp()))
            price_series.append(date_time.toMSecsSinceEpoch(), row['Close'])
            volume_set.append(row['Volume'])

        volume_series.append(volume_set)

        chart = QChart()
        chart.addSeries(price_series)
        chart.addSeries(volume_series)
        chart.setTitle(f"{self.current_stock} - {self.current_period}")

        # Create and set up the X-axis (date/time)
        axis_x = QDateTimeAxis()
        axis_x.setFormat("MM-dd HH:mm")
        axis_x.setTickCount(5)
        chart.addAxis(axis_x, Qt.AlignBottom)
        price_series.attachAxis(axis_x)
        volume_series.attachAxis(axis_x)

        # Create and set up the Y-axis for price
        axis_y_price = QValueAxis()
        axis_y_price.setTitleText("Price")
        chart.addAxis(axis_y_price, Qt.AlignLeft)
        price_series.attachAxis(axis_y_price)

        # Create and set up the Y-axis for volume
        axis_y_volume = QValueAxis()
        axis_y_volume.setTitleText("Volume")
        chart.addAxis(axis_y_volume, Qt.AlignRight)
        volume_series.attachAxis(axis_y_volume)

        # Set the range for volume axis
        max_volume = stock_data['Volume'].max()
        axis_y_volume.setRange(0, max_volume * 1.1)  # Add 10% margin

        # Set colors and style for price series
        price_series.setColor(QColor(255, 0, 0))  # Red color
        pen = price_series.pen()
        pen.setStyle(Qt.DashLine)
        pen.setWidth(2)
        price_series.setPen(pen)

        # Hide the legend
        chart.legend().hide()

        self.chart_view.setChart(chart)

    def update_analysis(self):
        stock = yf.Ticker(self.current_stock)
        stock_data = stock.history(period="6mo")
        
        # Calculate moving averages
        ma10 = stock_data['Close'].rolling(window=10).mean().iloc[-1]
        ma30 = stock_data['Close'].rolling(window=30).mean().iloc[-1]
        ma50 = stock_data['Close'].rolling(window=50).mean().iloc[-1]
        
        # Calculate Stochastic Oscillator
        low_14 = stock_data['Low'].rolling(window=14).min()
        high_14 = stock_data['High'].rolling(window=14).max()
        k = 100 * ((stock_data['Close'] - low_14) / (high_14 - low_14))
        d = k.rolling(window=3).mean()
        current_k = k.iloc[-1]
        current_d = d.iloc[-1]

        # Calculate RSI
        delta = stock_data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]

        # Prepare analysis text
        analysis = f"Analysis for {self.current_stock}:\n\n"
        
        # Add fundamental data
        info = stock.info
        analysis += "Fundamental Data:\n"
        analysis += f"Market Cap: ${info.get('marketCap', 'N/A'):,}\n"
        analysis += f"P/E Ratio: {info.get('trailingPE', 'N/A'):.2f}\n"
        analysis += f"EPS (TTM): ${info.get('trailingEps', 'N/A'):.2f}\n"
        analysis += f"Forward P/E: {info.get('forwardPE', 'N/A'):.2f}\n"
        
        # Handle dividend yield formatting
        dividend_yield = info.get('dividendYield', 'N/A')
        if isinstance(dividend_yield, (int, float)):
            analysis += f"Dividend Yield: {dividend_yield:.2%}\n"
        else:
            analysis += f"Dividend Yield: {dividend_yield}\n"
        
        analysis += f"52 Week High: ${info.get('fiftyTwoWeekHigh', 'N/A'):.2f}\n"
        analysis += f"52 Week Low: ${info.get('fiftyTwoWeekLow', 'N/A'):.2f}\n"

        analysis += "\n"

        # Add existing technical analysis
        analysis += f"Moving Averages:\n"
        analysis += f"10 Day: {ma10:.2f}\n"
        analysis += f"30 Day: {ma30:.2f}\n"
        analysis += f"50 Day: {ma50:.2f}\n"
        
        if ma10 > ma30 and ma30 > ma50:
            analysis += "Interpretation: Strong uptrend. All shorter-term MAs above longer-term MAs.\n\n"
        elif ma10 < ma30 and ma30 < ma50:
            analysis += "Interpretation: Strong downtrend. All shorter-term MAs below longer-term MAs.\n\n"
        elif ma10 > ma30 > ma50:
            analysis += "Interpretation: Potential bullish trend. Shorter-term MAs rising faster than longer-term MAs.\n\n"
        elif ma10 < ma30 < ma50:
            analysis += "Interpretation: Potential bearish trend. Shorter-term MAs falling faster than longer-term MAs.\n\n"
        else:
            analysis += "Interpretation: Mixed signals. No clear trend direction.\n\n"

        analysis += f"Stochastic Oscillator:\n"
        analysis += f"%K: {current_k:.2f}\n"
        analysis += f"%D: {current_d:.2f}\n"
        if current_k > 80 and current_d > 80:
            analysis += "Interpretation: Overbought condition\n"
        elif current_k < 20 and current_d < 20:
            analysis += "Interpretation: Oversold condition\n"
        else:
            analysis += "Interpretation: Neutral\n\n"

        analysis += f"Relative Strength Index (RSI): {current_rsi:.2f}\n"
        if current_rsi > 70:
            analysis += "Interpretation: Overbought condition\n"
        elif current_rsi < 30:
            analysis += "Interpretation: Oversold condition\n"
        else:
            analysis += "Interpretation: Neutral\n"
        
        # Fetch analyst price targets
        try:
            price_targets = stock.get_analyst_price_targets()
            analysis += f"\nAnalyst Price Targets:\n"
            analysis += f"Current price: ${price_targets['current']:.2f}\n"
            analysis += f"Low price: ${price_targets['low']:.2f}\n"
            analysis += f"High price: ${price_targets['high']:.2f}\n"
            analysis += f"Mean price: ${price_targets['mean']:.2f}\n"
            analysis += f"Median price: ${price_targets['median']:.2f}\n"
        except Exception as e:
            analysis += f"\nAnalyst Price Targets: Data not available\n"

        self.analysis_text.setText(analysis)

    def search_stock(self):
        stock_symbol = self.search_box.text().upper()
        if stock_symbol:
            self.update_stock(stock_symbol)

    def update_indices_charts(self, period):
        indices = [("^GSPC", "S&P 500"), ("^DJI", "Dow Jones"), ("^IXIC", "NASDAQ")]
        chart_views = [self.sp500_chart_view, self.dow_chart_view, self.nasdaq_chart_view]

        for (symbol, name), chart_view in zip(indices, chart_views):
            data = yf.download(symbol, period=period, interval="5m" if period == "1d" else "1d")
            
            series = QLineSeries()
            for index, row in data.iterrows():
                date_time = QDateTime()
                date_time.setSecsSinceEpoch(int(index.timestamp()))
                series.append(date_time.toMSecsSinceEpoch(), row['Close'])

            chart = QChart()
            chart.addSeries(series)
            chart.setTitle(f"{name} - {period}")

            axis_x = QDateTimeAxis()
            if period == "1d":
                axis_x.setFormat("HH:mm")
            elif period == "5d":
                axis_x.setFormat("MM-dd HH:mm")
            else:
                axis_x.setFormat("MM-dd")
            axis_x.setTickCount(5)
            chart.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)

            axis_y = QValueAxis()
            chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)

            series.setColor(QColor(255, 0, 0))  # Red color
            pen = series.pen()
            pen.setStyle(Qt.DashLine)  # Dashed line
            pen.setWidth(2)
            series.setPen(pen)

            chart.legend().hide()
            chart_view.setChart(chart)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockApp()
    window.show()
    sys.exit(app.exec_())