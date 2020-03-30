# StockTrendViewer
This is a program which uses a database of stocknames and urls to their historical prices page on yahoo finance, to find data about these stocks and display it to a user

I coded this program to:
 - Learn how to integrate matplotlib with pyqt5 (I will need this knowlege in my upcoming computer science coursework).
 - Practice pyqt5.
 - Learn the matplotlib module.
 - practice webscraping data.
 
I am happy with the outcome of the program, a small kink I would iron out if I had more time to focus on the program, would be dealing with changes in the webscraped data:
 - for example at some points in yahoo finances something called dividens occours, I have a very limited knowlege of stocks so I dont know    what that means, however there is no price data for those dates, so I implemented a error message that occours if you try to retrieve      data when an dividend appears. If I had more time I would find a way to plot an average of the day before and after, and find a way to    highlight the fact that I have done so.
 
If I had more time I would also of added a window for an admin to add new stock URLS to the database. 
