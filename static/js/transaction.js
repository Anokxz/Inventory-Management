document.getElementById('transactionType').addEventListener('change', function (e) {
    const transactionType = e.target.value;
    const dealerField = document.getElementById('dealerField');
    const customerField = document.getElementById('customerField');

    if (transactionType === 'buy') {
        dealerField.style.display = 'block';
        customerField.style.display = 'none';
    } else if (transactionType === 'sell') {
        dealerField.style.display = 'none';
        customerField.style.display = 'block';
    } else {
        dealerField.style.display = 'none';
        customerField.style.display = 'none';
    }
});

document.getElementById('transactionForm').addEventListener('submit', function (e) {
    e.preventDefault();

    // Get form values
    const transactionType = document.getElementById('transactionType').value;
    const dealer = document.getElementById('dealer').value;
    const customer = document.getElementById('customer').value;
    const product = document.getElementById('product').value;
    const quantity = parseInt(document.getElementById('quantity').value);
    const price = parseFloat(document.getElementById('price').value);
    const totalPrice = quantity * price;

    let transactionEntity = '';
    let rowClass = '';

    if (transactionType === 'buy') {
        transactionEntity = dealer;
        rowClass = 'buy'; 
    } else if (transactionType === 'sell') {
        transactionEntity = customer;
        rowClass = 'sale'; 
    }

    const tableBody = document.querySelector('#transactionTable tbody');
    const newRow = tableBody.insertRow();
    newRow.classList.add(rowClass);

    newRow.innerHTML = `
        <td>${transactionType.charAt(0).toUpperCase() + transactionType.slice(1)}</td>
        <td>${transactionEntity}</td>
        <td>${product}</td>
        <td>${quantity}</td>
        <td>${price.toFixed(2)}</td>
        <td>${totalPrice.toFixed(2)}</td>
    `;

    document.getElementById('transactionForm').reset();
    document.getElementById('dealerField').style.display = 'none';
    document.getElementById('customerField').style.display = 'none';
});
