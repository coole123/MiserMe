# MiserMe
A simple, free form budgeting / financial Flask application built using Python, SQLite3, HTML, CSS, and JavaScript.

MiserMe is an application that can help users log, budget, and record their finances. I usually do my finances using Microsoft Excel, but grew tired of continually creating, styling, and manually editing each cell. I created MiserMe to help accelerate my financial recordings, and create files for my records on the fly. The biggest strength in MiserMe is it's ability to record every tiny change made to your budget, including that unexpected $3 bill you found as you were walking home from class.

<hr>

<br>
<br>
<br>

<h2 align="center">Preview: Login and Register</h2>
<p>Unregistered users will have to create an account before proceeding to use the application.</p>

<div align="center">
<img src="images/register.png">
</div>

<p>Registered users are free to login with credentials. If incorrect credentials are given, The user will be redirected to an error page.</p>

<div align="center">
<img src="images/login.png">
</div>

<hr>

<br>
<br>
<br>

<h2 align="center">Preview: Homepage</h2>
<p>Once logged in, users will be taken to a semi-blank page, signifying the user to start a budget.</p>

<div align="center">
<img src="images/homepage.png">
</div>

<hr>

<br>
<br>
<br>

<h2 align="center">Preview: Start Budget</h2>
<p>The user can start a budget by clicking the "Start Budget" option in the navigation bar. They will be prompted to enter a value (budget) that they want to allocate for this period.</p>

<div align="center">
<img src="images/start_budget.png">
</div>

<hr>

<br>
<br>
<br>

<h2 align="center">Preview: Add Expense</h2>
<p>After a budget is started, users have an option to add an expense (i.e. bills, transactions, etc.). Below is an example of a user entering his rent.</p>

<div align="center">
<img src="images/expense.png">
</div>

### Please note: Predicted cost is used for transactions that have not yet occurred. True cost is used for transactions that have already taken place.

### Updates

| Date | Major Updates |
| ------------- | ------------- |
| October 7th, 2020 | Began the application: created the flask app, necessary html pages, and the sqlite database file. |
| October 8th, 2020 | Continued the login function in app.py. Created connection to sqlite database, and created the register function. |
| October 12th, 2020 | Added items to style.css, created navbar, completed the login function to accurately read user input. |
| October 13th, 2020 | Registering successfully connects to sqlite3 database. New HTML file to confirm registration. |
| October 15th, 2020 | Fixed the login function: registered can log into the home page. Created logout function. Edited navbar. |
| October 16th, 2020 | Created the 'finances' database, and coded SQL query to retrieve user funds. Temporarily completed index function. Started Homepage html file. |
| N/A | Computer complications led to a temporary pause on development of this app. Development continued after November 4th, 2020. |
| November 4th, 2020 | Created the HTML files for Funds, Expenses, and History. Coded the functions in app.py to load the HTML files. |
| November 5th, 2020 | Completed expense.html file for user expense log; programmed the expense function, debugging to continue. |
| November 6th, 2020 | Completed expense function and properly connected it to index.html. Funds snapshot now displays. |
| November 10th, 2020 | Completed the add_funds function and the add_funds.html file. Adding to available funds now an option. |
| November 11th, 2020 | Completed the history function and the history.html file. Included SQL queries for history in other functions. |
| November 12th, 2020 | Debugged several issues that were causing values to show incorrectly (i.e. changed values to USD $, removed NONE values). |
| November 13th, 2020 | Debugged issues regarding empty values, included true costs in expense function, and included timestamp in history. |
| November 14th, 2020 | Restructured history function: shows detailed description as opposed to a table of entries. Altered all functions to match changes. |
| November 15th, 2020 | Completed "start_budget" function. Corrected decrement feature to available funds when creating expenses. Layout/design changes. |
| November 16th, 2020 | Debugged issues in the add_funds function, created the edit function. Edit function currently only features GET method. |
| November 17th, 2020 | Completed the edit function, added Entry ID to homepage, debugged issues after the creation of edit function. |
| November 18th, 2020 | Completed the edit_add function and the edit_added.html file. User is now able to edit funds that they added to account. |
| November 19th, 2020 | Completed the download function. Tested entire application. Application complete. Now starting restyling for aesthetics. |
