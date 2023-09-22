// Wait for the DOM to be ready
document.addEventListener("DOMContentLoaded", function () {
    const orderForm = document.getElementById("order-form");

    // Add an event listener to the form's submit button
    orderForm.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent the form from submitting normally

        // Get form input values
        const addressInput = document.getElementById("address");
        const productNameInput = document.getElementById("product_name");
        const productPriceInput = document.getElementById("product_price");

        const address = addressInput.value.trim();
        const productName = productNameInput.value.trim();
        const productPrice = parseFloat(productPriceInput.value);

        // Validate form inputs
        if (!address || !productName || isNaN(productPrice) || productPrice <= 0) {
            alert("Please fill in all fields correctly.");
            return;
        }

        // Prepare data for the AJAX request
        const data = {
            address: address,
            product_name: productName,
            product_price: productPrice,
        };

        // Send an AJAX POST request to the server
        fetch("/order", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
        .then(response => response.text())
        .then(message => {
            alert(message); // Display the server's response message
            if (message.includes("successful")) {
                // Clear form inputs on successful order
                addressInput.value = "";
                productNameInput.value = "";
                productPriceInput.value = "";
            }
        })
        .catch(error => {
            console.error("An error occurred:", error);
        });
    });
});
