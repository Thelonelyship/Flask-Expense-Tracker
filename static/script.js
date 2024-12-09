const expenseStorageKey = 'expenses';

//! Get them
function getExpenses() {
    return JSON.parse(localStorage.getItem(expenseStorageKey)) || [];
}

//! write them
function setExpenses(expenses) {
    localStorage.setItem(expenseStorageKey, JSON.stringify(expenses));
}

//! show them
function renderExpenses() {
    const expenseList = document.getElementById('expenselist');
    const localStorageExpenses = getExpenses();
    expenseList.innerHTML = '';
    if (localStorageExpenses.length === 0) {
        expenseList.innerHTML = '<tr><td colspan="4">Go out and spend some money! It\'s fun! I promise!</td></tr>';
    }

localStorageExpenses.forEach(expense => {
    const row = document.createElement('tr');
    row.id = `expense-${expense.id}`;
    row.innerHTML = `
        <td>${expense.category}</td>
        <td>${expense.amount}</td>
        <td>${expense.description}</td>
        <td><button class="delete-btn" onclick="deleteExpense('${expense.id}')">Delete</button></td>`;
    expenseList.appendChild(row);
});

//! Sum them
const total = localStorageExpenses.reduce((sum, expense) => sum + parseFloat(expense.amount || 0), 0);
document.getElementById('total').innerText = total.toFixed(2);
}
//! submit new locally
document.getElementById('expenseform').addEventListener('submit', function(event) {
    event.preventDefault();

//! new expense with unique id
const newExpense = {
    id: new Date().toISOString(),
    category: document.getElementById('category').value,
    amount: document.getElementById('amount').value,
    description: document.getElementById('description').value
};

//! get and add from local storage
const expenses = getExpenses();
    expenses.push(newExpense);
    setExpenses(expenses);

//! put it in the data
fetch('/insert', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(newExpense)
});

//! reset and reload
    this.reset();
    renderExpenses();
});

//! Delete one row
function deleteExpense(id) {
    let expenses = getExpenses();
    expenses = expenses.filter(expense => expense.id !== id);
    setExpenses(expenses);
    document.getElementById(`expense-${id}`).remove();
    fetch(`/delete/${id}`, { method: 'GET' });

    renderExpenses();
}

//! Delete all expenses
function deleteAll() {
    setExpenses([]);
    document.getElementById('expenselist').innerHTML = '';
    document.getElementById('total').innerText = '0.00';
    fetch('/deleteall', { method: 'GET' });
}

//! Initialize on page load
window.onload = renderExpenses;
