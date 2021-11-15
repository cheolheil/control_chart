import matplotlib.pyplot as plt


class ccplot:
    # this class accepts an instance of schewart_chart
    def __init__(self, chart, X_test, figsize=(18, 6)):
        self.chart_name = chart.stat.__repr__()
        self.figsize = figsize
        self.fig, self.ax = plt.subplots(figsize=self.figsize)
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel(self.chart_name)
        self.ax.set_title(self.chart_name + ' Control Chart')
        self.ax.axhline(y=chart.upper_limit, color='grey', linestyle='--', lw=0.5)
        self.ax.axhline(y=chart.lower_limit, color='grey', linestyle='--', lw=0.5)
        self.ax.axhline(y=chart.center_line, color='black', lw=0.75)

        stat_test, ooc_indices = chart.run(X_test, verbose=False)
        self.ax.plot(stat_test, color='lightseagreen', lw=1.25)
        self.ax.scatter(ooc_indices, stat_test[ooc_indices], facecolor='crimson', marker='s', s=10)
        plt.show()       
        
